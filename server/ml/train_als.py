"""Entraîne le modèle ALS à partir des notes stockées dans Blob Storage.

Lancé par Azure ML (voir train-pipeline.yml) : le conteneur "data" est monté en entrée,
le modèle est écrit dans le conteneur "models". Aucune clé n'est nécessaire ici.

Données attendues dans --ratings :
  ratings.csv         notes de départ (jeu MyAnimeList, voir prepare_ratings.py)
  new/*.csv           notes envoyées depuis l'application
Colonnes : user_id, anime_id, rating

Usage local : python train_als.py --ratings <dossier> --output <dossier>
"""
import argparse
import glob
import os
import shutil
import tempfile

import pandas as pd
from pyspark.ml.recommendation import ALS
from pyspark.sql import SparkSession

COLUMNS = ["user_id", "anime_id", "rating"]


def load_ratings(ratings_dir):
    files = [os.path.join(ratings_dir, "ratings.csv")]
    files += sorted(glob.glob(os.path.join(ratings_dir, "new", "*.csv")))
    frames = [pd.read_csv(f, usecols=COLUMNS) for f in files if os.path.exists(f)]
    if not frames:
        raise FileNotFoundError(f"Aucune note trouvée dans {ratings_dir}")

    ratings = pd.concat(frames, ignore_index=True)
    # -1 : anime vu mais pas noté
    ratings = ratings[ratings["rating"] != -1]
    # Si un utilisateur a noté plusieurs fois le même anime, garder la dernière note
    ratings = ratings.drop_duplicates(subset=["user_id", "anime_id"], keep="last")
    print(f"{len(ratings)} notes, dont {len(frames) - 1} fichiers envoyés depuis l'application")
    return ratings.astype("int32")


def train(ratings, rank=10):
    spark = (
        SparkSession.builder.appName("AnimeRecommendation")
        .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "8g"))
        .getOrCreate()
    )
    ratings_spark = spark.createDataFrame(ratings)

    als = ALS(
        userCol="user_id",
        itemCol="anime_id",
        ratingCol="rating",
        rank=rank,
        regParam=0.1,              # Valeur par défaut de Spark ; reprise par le fold-in de l'API
        nonnegative=True,          # Facteurs positifs ou nuls (contrainte reprise par le fold-in)
        implicitPrefs=False,       # On utilise des notes explicites
        coldStartStrategy="drop",  # Supprimer les prédictions sur données inconnues
    )
    return als.fit(ratings_spark)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ratings", required=True, help="Dossier contenant ratings.csv et new/")
    parser.add_argument("--output", required=True, help="Dossier où écrire le modèle")
    args = parser.parse_args()

    ratings = load_ratings(args.ratings)
    model = train(ratings)

    # Spark écrit d'abord en local, puis on copie vers la sortie (montage Blob)
    with tempfile.TemporaryDirectory() as tmp:
        local_path = os.path.join(tmp, "als_model")
        model.save(local_path)
        shutil.copytree(local_path, args.output, dirs_exist_ok=True)

    # Nombre de notes par anime : l'API ne recommande que les animés au vecteur fiable
    counts = ratings.groupby("anime_id").size().rename("count")
    counts.to_csv(os.path.join(args.output, "item_counts.csv"))

    # Marqueur écrit en dernier : l'API ne charge que les modèles complets
    with open(os.path.join(args.output, "_READY"), "w") as f:
        f.write("ok\n")
    print(f"Modèle écrit dans {args.output}")
