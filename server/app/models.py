from pydantic import BaseModel
from typing import List

# Schéma pour une requête utilisateur
class UserRequest(BaseModel):
    user_id: int
    username: str

# Schéma pour une réponse de recommandations
class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[int]  # Liste des anime_id recommandés

class RatingRequest(BaseModel):
    user_id: int
    anime_id: int
    rating: int
