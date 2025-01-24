# Anime Recommendations

[![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/-Uvicorn-000000?logo=uvicorn&logoColor=white)
![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=white)
![Azure Blob Storage](https://img.shields.io/badge/Azure%20Blob%20Storage-0089D6?logo=microsoft-azure&logoColor=white)
![Azure Web App](https://img.shields.io/badge/Azure%20Web%20App-F25022?logo=microsoft-azure&logoColor=white)
![Azure Machine Learning](https://img.shields.io/badge/Azure%20Machine%20Learning-7FBA00?logo=azure-machine-learning&logoColor=white)
![Azure SQL Database](https://img.shields.io/badge/Azure%20SQL%20Database-FFB900?logo=azure-sql-database&logoColor=white)
![PySpark](https://img.shields.io/badge/-PySpark-E25A1C?logo=apache-spark&logoColor=white)

Welcome to the anime recommendations project! This project uses a collaborative filtering model to recommend animes based on user preferences.


## Video Demo

https://github.com/user-attachments/assets/5e116876-fa0f-48ca-8b05-49ef5f62f7de

## Features

- Search for animes by name
- Recommend similar animes
- Rate animes (enhance the training database)

## Architecture

<img width="647" alt="Screenshot 2024-12-27 at 17 39 41" src="https://github.com/user-attachments/assets/6eaa3921-2983-4f0e-9789-be1ab8e24fcd" />

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Afdal-B/anime-recommendations.git
   ```
2. Navigate to the project directory:
   ```bash
   cd anime-recommendations
   ```
3. Install server dependencies:
   ```bash
   pip install -r server/app/requirements.txt
   ```
4. Install front-end dependencies:
   ```bash
   cd client
   npm install
   ```

## Usage

1. Start the server:
   ```bash
   uvicorn server.app.main:app --reload
   ```
2. Start the front-end:
   ```bash
   npm start
   ```
3. Open your browser and go to `http://localhost:8000` for the API and `http://localhost:3000` for the user interface.

