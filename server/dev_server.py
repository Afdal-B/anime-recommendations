"""Lance l'application en local avec SQLite à la place d'Azure SQL.

Aucune base ni driver ODBC requis : la base SQLite (server/dev.sqlite3) est créée
et remplie avec le catalogue d'animés au premier lancement.

Usage : python server/dev_server.py   puis ouvrir http://localhost:8000
"""
import os
import re
import sqlite3
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "dev.sqlite3")
sys.path.insert(0, os.path.join(HERE, "app"))

# Servir le build React s'il existe (sinon utiliser `npm start` dans client/)
os.environ.setdefault("STATIC_DIR", os.path.join(HERE, "..", "client", "build"))

SCHEMA = """
CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE);
CREATE TABLE animes (anime_id INTEGER PRIMARY KEY, name TEXT NOT NULL, image_url TEXT,
                     synopsis TEXT, genres TEXT, score REAL);
CREATE TABLE ratings (rating_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                      anime_id INTEGER NOT NULL, rating INTEGER NOT NULL,
                      created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE recommendations (recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                              user_id INTEGER NOT NULL, anime_id INTEGER NOT NULL,
                              created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""


def to_sqlite(sql):
    """Traduit les tournures SQL Server utilisées par l'API en SQLite."""
    sql = re.sub(r"OFFSET\s+0\s+ROWS\s+FETCH\s+NEXT\s+\?\s+ROWS\s+ONLY", "LIMIT ?", sql)
    match = re.search(r"OUTPUT\s+INSERTED\.(\w+)\s+", sql)
    if match:
        sql = sql.replace(match.group(0), "") + f" RETURNING {match.group(1)}"
    return sql


class Cursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=()):
        self._cursor.execute(to_sqlite(sql), params)
        return self

    def executemany(self, sql, seq):
        self._cursor.executemany(to_sqlite(sql), seq)
        return self

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class Connection:
    def __init__(self):
        self._conn = sqlite3.connect(DB_PATH)

    def cursor(self):
        return Cursor(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def init_db():
    if os.path.exists(DB_PATH):
        return
    print("Création de la base SQLite locale…")
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    df = pd.read_csv(os.path.join(HERE, "data", "anime-dataset-2023.csv"))
    df = df[df["Score"].notna() & (df["Score"] != "UNKNOWN")]
    rows = [
        (int(anime_id), name, image_url, synopsis, genres, float(score))
        for anime_id, name, image_url, synopsis, genres, score in df[
            ["anime_id", "Name", "Image URL", "Synopsis", "Genres", "Score"]
        ].values.tolist()
    ]
    conn.executemany("INSERT INTO animes VALUES (?, ?, ?, ?, ?, ?)", rows)
    # Même décalage des identifiants que dans schema.sql
    conn.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('users', 9999999)")
    conn.commit()
    conn.close()
    print(f"{len(rows)} animés chargés dans {DB_PATH}")


if __name__ == "__main__":
    import database

    init_db()
    database.get_db_connection = lambda *args, **kwargs: Connection()

    import uvicorn
    from main import app

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", 8000)))
