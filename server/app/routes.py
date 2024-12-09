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

@router.get("/animes/search")
def search_animes(query: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Requête pour rechercher des animes par nom
        cursor.execute("""
            SELECT anime_id, name, image_url, synopsis, score
            FROM animes
            WHERE name LIKE ?
        """, (f"%{query}%",))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Vérifier si des résultats ont été trouvés
        if not results:
            raise HTTPException(status_code=404, detail="Aucun anime trouvé.")
        
        return [
            {
                "anime_id": anime[0],
                "name": anime[1],
                "image_url": anime[2],
                "synopsis": anime[3],
                "score": anime[4]
            }
            for anime in results
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, posexplode, sqrt, sum as spark_sum, pow, lit
from pyspark.sql.window import Window
from pyspark.sql import Row
from fastapi import HTTPException

def get_anime_info(anime_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Requête pour obtenir les informations d'un anime par son ID
        cursor.execute("""
            SELECT anime_id, name, image_url, synopsis, score
            FROM animes
            WHERE anime_id = ?
        """, (anime_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Vérifier si l'anime a été trouvé
        if not result:
            raise HTTPException(status_code=404, detail="Anime non trouvé.")
        
        return {
            "anime_id": result[0],
            "name": result[1],
            "image_url": result[2],
            "synopsis": result[3],
            "score": result[4]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/animes/similar/{anime_id}")
def get_similar_animes(anime_id: int, top_n: int = 5):
    try:
        # Charger le modèle ALS
        model = load_model()
        spark = SparkSession.builder.getOrCreate()
        
        # Obtenir les caractéristiques de l'anime donné
        anime_vector = (
            model.itemFactors.filter(col("id") == anime_id).collect()
        )
        
        if not anime_vector:
            raise HTTPException(status_code=404, detail="Anime non trouvé.")
        
        # Récupérer le vecteur de l'anime sous forme de liste
        anime_vector_values = anime_vector[0]["features"]
        
        # Créer un DataFrame pour l'anime cible avec ses indices
        anime_vector_df = spark.createDataFrame(
            [(i, val) for i, val in enumerate(anime_vector_values)],
            schema=["index", "target_feature"]
        )
        
        # Exploser le tableau de chaque item dans le modèle pour avoir des éléments scalaires
        exploded_item_factors = (
            model.itemFactors
            .select(col("id"), posexplode(col("features")).alias("index", "item_feature"))
        )
        
        # Joindre sur l'index pour associer chaque élément avec l'élément correspondant de l'anime cible
        joined_df = exploded_item_factors.join(anime_vector_df, on="index")
        
        # Calculer le produit scalaire et les normes
        similarity_df = (
            joined_df.groupBy("id")
            .agg(
                spark_sum(col("item_feature") * col("target_feature")).alias("dot_product"),
                sqrt(spark_sum(pow(col("item_feature"), 2))).alias("norm_item"),
                sqrt(spark_sum(pow(col("target_feature"), 2))).alias("norm_target")
            )
            .withColumn(
                "similarity",
                col("dot_product") / (col("norm_item") * col("norm_target"))
            )
        )
        
        # Trier par similarité et récupérer les meilleurs résultats
        similar_animes = (
            similarity_df
            .select("id", "similarity")
            .where(col("id") != anime_id)  # Exclure l'anime lui-même
            .orderBy(col("similarity").desc())
            .limit(top_n)
        )
        
        results = similar_animes.collect()
        
        # Récupérer les informations de l'anime
        anime_details = []
        for row in results:
            anime_info = get_anime_info(row.id)  # Fonction fictive pour récupérer les détails de l'anime
            anime_details.append({
                "anime_id": row.id,
                "similarity": row.similarity,
                "name": anime_info["name"],
                "synopsis": anime_info["synopsis"],
                "image_url": anime_info["image_url"]
            })
        
        return anime_details
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")
