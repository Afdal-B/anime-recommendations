import os
import zipfile
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
import pandas as pd
from database import get_db_connection

load_dotenv()
def unzip_file(zip_file_path, extract_to_folder):
    """Dézippe un fichier zip dans le dossier spécifié, en ne gardant que le dossier principal."""
    try:
        folder_name = (os.path.splitext(zip_file_path)[0]).split("/")[-1]
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Extraire uniquement le dossier correspondant au nom du fichier
            for member in zip_ref.namelist():
                if member.startswith(folder_name):
                    zip_ref.extract(member, extract_to_folder)
        print(f"Fichier dézippé dans : {extract_to_folder}")
    except zipfile.BadZipFile:
        print(f"Erreur : Le fichier {zip_file_path} n'est pas un fichier zip valide.")
    except Exception as e:
        print(f"Erreur lors de la décompression : {e}")

def download_model_from_blob(blob_name="als_model.zip", download_path="../models/zipped/als_model.zip"):
    # Connexion au compte de stockage
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_name = "models"
    
    # Accéder au blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    try:
        # Télécharger le modèle
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        with open(download_path, "wb") as file:
            file.write(blob_client.download_blob().readall())
        
        print(f"Modèle téléchargé depuis Blob Storage : {download_path}")

        unzip_file(download_path, '../models/unzipped/')
    
    except Exception as e:
        print(f"Erreur lors du téléchargement du blob : {e}")

#download_model_from_blob(blob_name="anime-filtered.csv",download_path="models/anime.csv")
# Configuration de la session Spark
def get_spark_session():
    return SparkSession.builder \
        .appName("AnimeRecommendationAPI") \
        .getOrCreate()

# Charger le modèle ALS pré-entraîné
def load_model(path="../models/unzipped/als_model.zip"):
    # On telecharge le modèle
    download_model_from_blob()
    spark = get_spark_session()
    return ALSModel.load(path)



def load_anime_data_from_csv(csv_file_path):
    try:
        # Charger les données des animés depuis le fichier CSV
        df = pd.read_csv(csv_file_path)
        df = df[df['Score'].notna() & (df['Score'] != 'UNKNOWN')]  # Filtrer pour ne garder que les lignes où le score est connu et différent de 'UNKNOWN'
        anime_data = df[['anime_id', 'Name', 'Image URL', 'Synopsis', 'Genres', 'Score']].values.tolist()  # Ajout du score
        
        # Enregistrer les données dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for anime_id, name, image_url, synopsis, Genres, score in anime_data:  
            cursor.execute("INSERT INTO animes (anime_id, name, image_url, synopsis, genres, score) VALUES (?, ?, ?, ?, ?, ?)", 
                           (anime_id, name, image_url, synopsis, Genres, float(score)))  
        
        conn.commit()
        cursor.close()
        conn.close()
    
    except Exception as e:
        print(f"Erreur lors du chargement des données des animés depuis le CSV : {e}")
#load_anime_data_from_csv("../data/anime-dataset-2023.csv")
#print(pd.read_csv("../data/anime-dataset-2023.csv").columns)

def update_ratings_blob(user_id, blob_name="ratings.csv", container_name="data"):
    # Connexion au compte de stockage
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Télécharger le fichier existant
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    # Lire le fichier existant dans un DataFrame
    try:
        with open("ratings_temp.csv", "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        existing_ratings = pd.read_csv("ratings_temp.csv")
    except Exception as e:
        print(f"Erreur lors du téléchargement du blob : {e}")
        return

    # Récupérer les nouvelles notes de la base de données pour l'utilisateur
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, anime_id, rating FROM ratings WHERE user_id = ?", (user_id,))
    new_ratings = cursor.fetchall()
    cursor.close()
    conn.close()
    new_ratings = [{'user_id': user_id, 'anime_id': anime_id, 'rating': rating} for user_id, anime_id, rating in new_ratings]

    # Vérifier si de nouvelles notes ont été récupérées
    if new_ratings:
        # Ajouter les nouvelles notes
        new_ratings_df = pd.DataFrame(new_ratings, columns=['user_id', 'anime_id', 'rating'])
        updated_ratings = pd.concat([existing_ratings, new_ratings_df], ignore_index=True)

        # Enregistrer le DataFrame mis à jour dans un nouveau fichier CSV
        updated_ratings.to_csv("ratings_temp.csv", index=False)

        # Télécharger le fichier mis à jour dans le blob
        with open("ratings_temp.csv", "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        print("Fichier ratings.csv mis à jour dans Blob Storage.")
    else:
        print("Aucune nouvelle note à ajouter.")

def export_first_30000_ratings_to_csv(file_name="ratings.csv"):
        # Lire les données à partir de user-filtered.csv
        try:
            ratings_df = pd.read_csv("../data/user_filtered.csv")
            # Prendre les 30000 premières lignes
            first_30000_ratings = ratings_df[ratings_df['user_id']<=30000]
            # Enregistrer dans un fichier CSV
            first_30000_ratings.to_csv(file_name, index=False)
            print(f"Les 30000 premières notes ont été exportées vers {file_name}.")
        except Exception as e:
            print(f"Erreur lors de l'exportation des notes : {e}")

#export_first_30000_ratings_to_csv()
#update_ratings_blob(30002)
