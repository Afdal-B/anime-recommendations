import os
import uuid
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def save_ratings_for_training(ratings, container_name="data"):
    """Ajoute des notes au jeu d'entraînement stocké dans Blob Storage.

    Chaque envoi devient un petit fichier new/<date>-<id>.csv : pas de réécriture
    du gros ratings.csv, et pas de conflit si plusieurs utilisateurs notent en même temps.
    Optionnel : ne fait rien si AZURE_STORAGE_CONNECTION_STRING n'est pas définie.
    """
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string or not ratings:
        return

    from azure.storage.blob import BlobServiceClient

    blob_name = f"new/{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:8]}.csv"
    csv = pd.DataFrame(
        [(r.user_id, r.anime_id, r.rating) for r in ratings],
        columns=["user_id", "anime_id", "rating"],
    ).to_csv(index=False)

    try:
        BlobServiceClient.from_connection_string(connection_string).get_blob_client(
            container=container_name, blob=blob_name
        ).upload_blob(csv)
        print(f"Notes ajoutées au jeu d'entraînement : {blob_name}")
    except Exception as e:
        print(f"Erreur lors de l'envoi des notes vers Blob Storage : {e}")
