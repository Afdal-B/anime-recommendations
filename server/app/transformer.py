from transformers import AutoTokenizer, AutoModel
import torch
import pandas as pd
from tqdm import tqdm

# Charger BERT pré-entraîné
model_name = "bert-base-uncased"  # Vous pouvez remplacer par un modèle multilingue si besoin
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Vérifier si un GPU est disponible et l'utiliser
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Charger vos données
anime_data = pd.read_csv("server/data/anime-dataset-2023.csv")
synopsis = anime_data['Synopsis'].fillna("")  # Gérer les valeurs manquantes

# Fonction pour encoder un texte avec BERT
def encode_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
    with torch.no_grad():  # Pas besoin de calculer les gradients
        outputs = model(**inputs)
        # Utiliser la moyenne des embeddings de chaque token pour représenter le texte
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
    return embeddings.cpu().numpy()

# Appliquer l'encodage sur les synopsis
tqdm.pandas()  # Pour afficher la barre de progression
anime_data["embedding"] = synopsis.progress_apply(encode_text)

# Sauvegarder les embeddings dans un fichier
anime_data.to_pickle("anime_embeddings.pkl")
