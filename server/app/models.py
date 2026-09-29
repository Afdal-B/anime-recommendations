from pydantic import BaseModel, Field
from typing import List

# Connexion par pseudo : l'utilisateur est retrouvé s'il existe, créé sinon
class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)

class UserResponse(BaseModel):
    user_id: int
    username: str
    created: bool

class RatingRequest(BaseModel):
    user_id: int
    anime_id: int
    rating: int = Field(ge=1, le=10)
