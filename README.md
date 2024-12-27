# Recommandations d'Animes

Bienvenue dans le projet de recommandations d'animes ! Ce projet utilise un modèle de filtrage collaboratif pour recommander des animes en fonction des préférences de l'utilisateur.

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
<video src="demo/demo.mov" controls="controls" style="max-width: 100%;"></video>
[![Regardez la vidéo](https://raw.githubusercontent.com/Afdal-B/anime-recommendations/main/demo/demo.png)](https://raw.githubusercontent.com/Afdal-B/anime-recommendations/main/demo/demo.mov)
