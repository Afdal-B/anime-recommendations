# Recommandations d'Animes

[![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/-Uvicorn-000000?logo=uvicorn&logoColor=white)
![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=white)
![Azure Blob Storage](https://img.shields.io/badge/Azure%20Blob%20Storage-0089D6?logo=microsoft-azure&logoColor=white)
![Azure Web App](https://img.shields.io/badge/Azure%20Web%20App-0078D4?logo=microsoft-azure&logoColor=white)
![Azure Machine Learning](https://img.shields.io/badge/Azure%20Machine%20Learning-0078D4?logo=azure-machine-learning&logoColor=white)
![Azure SQL Database](https://img.shields.io/badge/Azure%20SQL%20Database-000000?logo=azure-sql-database&logoColor=white)
![PySpark](https://img.shields.io/badge/-PySpark-E25A1C?logo=apache-spark&logoColor=white)

Bienvenue dans le projet de recommandations d'animes ! Ce projet utilise un modèle de filtrage collaboratif pour recommander des animes en fonction des préférences de l'utilisateur.

## Fonctionnalités

- Recherche d'animes par nom
- Recommandations d'animes similaires
- Noter des animés (enrichir la base d'entrainement)

## Architecture
<img width="647" alt="Screenshot 2024-12-27 at 17 39 41" src="https://github.com/user-attachments/assets/6eaa3921-2983-4f0e-9789-be1ab8e24fcd" />


## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Afdal-B/anime-recommendations.git
   ```
2. Accédez au répertoire du projet :
   ```bash
   cd anime-recommendations
   ```
3. Installez les dépendances du serveur :
   ```bash
   pip install -r server/app/requirements.txt
   ```
4. Installez les dépendances du front-end :
   ```bash
   cd client
   npm install
   ```

## Utilisation

1. Lancez le serveur :
   ```bash
   uvicorn server.app.main:app --reload
   ```
2. Lancez le front-end :
   ```bash
   npm start
   ```
3. Ouvrez votre navigateur et accédez à `http://localhost:8000` pour l'API et `http://localhost:3000` pour l'interface utilisateur.

## Démo Vidéo

https://github.com/user-attachments/assets/5e116876-fa0f-48ca-8b05-49ef5f62f7de
