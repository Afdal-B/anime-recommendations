import pyodbc
from dotenv import load_dotenv
import os
load_dotenv()


def get_db_connection():
    # Informations de connexion
    server = 'anime-recommendation.database.windows.net'  # Remplacez par le nom de votre serveur
    database = 'anime-recommendation'              # Remplacez par le nom de votre base de données
    username = 'afdal'               # Remplacez par votre nom d'utilisateur
    password = os.getenv("AZURE_DATABASE_CONNECTION_PASSWORD")                 # Remplacez par votre mot de passe
    driver = '{ODBC Driver 18 for SQL Server}'       # Assurez-vous que le driver est installé

    # Établir la connexion
    try:
        connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
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

