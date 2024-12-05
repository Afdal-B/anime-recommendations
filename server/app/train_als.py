from pandas import read_csv,concat
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from azure.storage.blob import BlobServiceClient
import os 

import zipfile

def upload_model_to_blob(container_name="models", model_path="als_model.zip"):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=animerecommend1274417208;AccountKey=6IE3piaK42Tpt0ExsKoirjKBjcyB3aUQ3XUTDt6fzQ3trW/va+gBYLiA8Qtt2B32g2HuDhnj8uAp+AStfMJd0Q==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=model_path)

    # Zip le dossier et uploader le modèle
    try:
        with zipfile.ZipFile(model_path, 'w') as zipf:
            zipf.write("als_model")  # Zip le dossier entier
        with open(model_path, "rb") as data:
            blob_client.upload_blob(data, blob_type="BlockBlob", overwrite=True)
    except Exception as e:
        print(f"Erreur lors de l'upload du modèle : {e}")


def download_rating_csv(container_name="data",blob_name="ratings.csv"):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=animerecommend1274417208;AccountKey=6IE3piaK42Tpt0ExsKoirjKBjcyB3aUQ3XUTDt6fzQ3trW/va+gBYLiA8Qtt2B32g2HuDhnj8uAp+AStfMJd0Q==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Télécharger le fichier existant
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    # Lire le fichier existant dans un DataFrame
    try:
        with open("ratings.csv", "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
    except Exception as e:
        print(f"Erreur lors du téléchargement du blob : {e}")
        return
    
ratings_df= read_csv("ratings.csv")
rating_df = ratings_df[ratings_df['rating'] != -1]

    # Créer une session Spark
spark = SparkSession.builder \
    .appName("AnimeRecommendation") \
    .getOrCreate()

# Étape 1 : Charger les données dans Spark DataFrame
# Convertir le DataFrame pandas en DataFrame Spark
rating_df_spark = spark.createDataFrame(
rating_df[['user_id', 'anime_id', 'rating']].values.tolist(),  # Convertir en liste de listes
    schema=["user_id", "anime_id", "rating"]  )


# Étape 2 : Configurer le modèle ALS
als = ALS(
    userCol="user_id",
    itemCol="anime_id",
    ratingCol="rating",
    nonnegative=True,              # Assurer que les prédictions sont positives
    implicitPrefs=False,           # On utilise des notes explicites
    coldStartStrategy="drop"       # Supprimer les prédictions sur données inconnues
)

# Étape 3 : Entraîner le modèle
print(">>>> TRAINIG")
model = als.fit(rating_df_spark)
model.save("als_model")
print(">>>> UPLOAD TO BLOB")
upload_model_to_blob()