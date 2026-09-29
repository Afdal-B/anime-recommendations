import os
import time
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


def get_db_connection(retries=3, delay=10):
    """Ouvre une connexion à Azure SQL.

    La base serverless se met en pause quand elle est inactive : la première
    connexion peut échouer le temps qu'elle redémarre, d'où les tentatives.
    """
    import pyodbc

    connection_string = os.getenv("AZURE_DATABASE_CONNECTION_STRING")
    if not connection_string:
        raise RuntimeError("AZURE_DATABASE_CONNECTION_STRING n'est pas définie.")

    for attempt in range(1, retries + 1):
        try:
            return pyodbc.connect(connection_string, timeout=30)
        except pyodbc.Error as e:
            if attempt == retries:
                raise
            print(f"Connexion à la base échouée (tentative {attempt}/{retries}) : {e}")
            time.sleep(delay)


@contextmanager
def db_cursor():
    """Fournit un curseur, commit en cas de succès et ferme toujours la connexion."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        conn.close()
