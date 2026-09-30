"""Crée le schéma et charge le catalogue d'animés dans Azure SQL.

Usage : AZURE_DATABASE_CONNECTION_STRING=... python server/seed_db.py
"""
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from database import get_db_connection

HERE = os.path.dirname(__file__)


def create_schema(cursor):
    cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'animes'")
    if cursor.fetchone()[0]:
        print("Schéma déjà présent.")
        return
    with open(os.path.join(HERE, "schema.sql")) as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip()]
    for statement in statements:
        cursor.execute(statement)
    print("Schéma créé.")


def migrate(cursor):
    """Mises à jour du schéma pour une base créée avec une version précédente."""
    cursor.execute("SELECT COUNT(*) FROM sys.indexes WHERE name = 'ux_users_username'")
    if cursor.fetchone()[0] == 0:
        try:
            cursor.execute("CREATE UNIQUE INDEX ux_users_username ON users (username)")
            print("Index d'unicité des pseudos créé.")
        except Exception as e:
            # Des pseudos en double existent déjà : l'application fonctionne quand même
            print(f"Index d'unicité des pseudos non créé (pseudos en double ?) : {e}")


def load_animes(cursor, csv_path=os.path.join(HERE, "data", "anime-dataset-2023.csv")):
    df = pd.read_csv(csv_path)
    # Ne garder que les animés dont le score est connu
    df = df[df["Score"].notna() & (df["Score"] != "UNKNOWN")]
    rows = [
        (int(anime_id), name, image_url, synopsis, genres, float(score))
        for anime_id, name, image_url, synopsis, genres, score in df[
            ["anime_id", "Name", "Image URL", "Synopsis", "Genres", "Score"]
        ].values.tolist()
    ]
    cursor.execute("DELETE FROM animes")
    cursor.fast_executemany = True
    # Insertion par lots pour limiter la mémoire utilisée par fast_executemany
    for start in range(0, len(rows), 1000):
        cursor.executemany(
            "INSERT INTO animes (anime_id, name, image_url, synopsis, genres, score) VALUES (?, ?, ?, ?, ?, ?)",
            rows[start:start + 1000],
        )
    print(f"{len(rows)} animés chargés.")


if __name__ == "__main__":
    conn = get_db_connection()
    cursor = conn.cursor()
    create_schema(cursor)
    conn.commit()
    migrate(cursor)
    conn.commit()
    load_animes(cursor)
    conn.commit()
    conn.close()
