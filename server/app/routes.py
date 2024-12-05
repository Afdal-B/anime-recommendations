from fastapi import APIRouter, HTTPException
from pyspark.sql import SparkSession
from utils import load_model,update_ratings_blob
from models import UserRequest, RecommendationResponse,RatingRequest
from database import get_db_connection

router = APIRouter()

@router.get("/")
def home():
    return {"message":"hello"}


@router.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(request: UserRequest):
    # Charger le modèle ALS
    model = load_model()
    spark = SparkSession.builder.getOrCreate()
    
    user_id = request.user_id

    # Vérifier si l'utilisateur est dans le modèle
    try:
        user_recommendations = model.recommendForAllUsers(10)  # 10 recommandations
        recommendations = user_recommendations.filter(f"user_id = {user_id}").select("recommendations").collect()

        if not recommendations:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

        anime_ids = [row[0] for row in recommendations[0].recommendations]
        
        # Remplir la table recommendations
        conn = get_db_connection()
        cursor = conn.cursor()
        for anime_id in anime_ids:
            cursor.execute("INSERT INTO recommendations (user_id, anime_id) VALUES (?, ?)", (user_id, anime_id))
        
        conn.commit()
        cursor.close()
        return RecommendationResponse(user_id=user_id, recommendations=anime_ids)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    #return "hello"

#-------------------------------------------------------------------

@router.post("/users", response_model=UserRequest)
def create_user(user: UserRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insérer l'utilisateur dans la base de données
        cursor.execute("INSERT INTO users (username) VALUES (?)", (user.username))
        conn.commit()
        
        # Récupérer l'ID de l'utilisateur nouvellement créé
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (user.username))
        user_id = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {"user_id": user_id, "username": user.username}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#------------------------------------------------------------------------
from typing import List

@router.post("/ratings", response_model=List[RatingRequest])
def create_ratings(ratings: List[RatingRequest]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insérer les notes dans la base de données
        for rating in ratings:
            cursor.execute("INSERT INTO ratings (user_id, anime_id, rating) VALUES (?, ?, ?)", 
                           (rating.user_id, rating.anime_id, rating.rating))
        
        conn.commit()
        
        cursor.close()
        conn.close()

        # Start of Selection
        update_ratings_blob(ratings[0].user_id)
        return ratings  # Retourner les informations des notes créées

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#-----------------------------------------------------------

@router.get("/animes/top")
def get_top_animes(limit: int = 100):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Requête pour récupérer les animés avec les scores les plus élevés
        cursor.execute("""
            SELECT anime_id, name, image_url, synopsis, score
            FROM animes
            WHERE score IS NOT NULL
            ORDER BY score DESC
            OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
        """, (limit,))
        
        top_animes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "anime_id": anime[0],
                "name": anime[1],
                "image_url": anime[2],
                "synopsis": anime[3],
                "score": anime[4]
            }
            for anime in top_animes
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))