"""Prépare ratings.csv, les notes de départ de l'entraînement.

Source : user-filtered.csv du jeu Kaggle "MyAnimeList Dataset" (dbdmobile/myanimelist-dataset).
Comme dans le notebook, on garde les 30 000 premiers utilisateurs.

Usage : python prepare_ratings.py <user-filtered.csv> <ratings.csv>
"""
import sys

import pandas as pd

N_USERS = 30000

if __name__ == "__main__":
    source, target = sys.argv[1], sys.argv[2]
    chunks = pd.read_csv(source, usecols=["user_id", "anime_id", "rating"], chunksize=1_000_000)
    ratings = pd.concat(chunk[chunk["user_id"] <= N_USERS] for chunk in chunks)
    ratings = ratings[ratings["rating"] != -1]
    ratings.to_csv(target, index=False)
    print(f"{len(ratings)} notes de {ratings['user_id'].nunique()} utilisateurs écrites dans {target}")
