import pyodbc
from dotenv import load_dotenv
import os
load_dotenv()


def get_db_connection():     
    # Établir la connexion
    try:
        connection_string = os.getenv("AZURE_DATABASE_CONNECTION_STRING")
        conn = pyodbc.connect(connection_string)
        print("Connexion réussie à la base de données Azure SQL.")
        
        # Exemple de requête
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION;")  # Exemple de requête pour obtenir la version SQL Server
        row = cursor.fetchone()
        print("Version de SQL Server :", row[0])
        
        return conn  # Retourner la connexion
    except Exception as e:
        print("Erreur lors de la connexion à la base de données :", e)
        return None  # Retourner None en cas d'erreur

