# Recommandations d'Animes

Bienvenue dans le projet de recommandations d'animes ! Ce projet utilise un modèle de filtrage collaboratif pour recommander des animes en fonction des préférences de l'utilisateur.

## Technologies Utilisées

[![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/-Uvicorn-000000?logo=uvicorn&logoColor=white)
![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=white)

## Fonctionnalités

- Recherche d'animes par nom
- Recommandations d'animes similaires
- Noter des animés (enrichir la base d'entrainement)

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
