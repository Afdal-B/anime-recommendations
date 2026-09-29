from typing import List
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from utils import save_ratings_for_training
from models import LoginRequest, UserResponse, RatingRequest
from database import db_cursor

router = APIRouter(prefix="/api")


def _anime_row_to_dict(anime):
    return {
        "anime_id": anime[0],
        "name": anime[1],
        "image_url": anime[2],
        "synopsis": anime[3],
        "score": anime[4],
    }


def get_animes_info(anime_ids: List[int]):
    """Récupère les informations de plusieurs animés en une requête, indexées par anime_id."""
    if not anime_ids:
        return {}
    placeholders = ",".join("?" for _ in anime_ids)
    with db_cursor() as cursor:
        cursor.execute(
            f"SELECT anime_id, name, image_url, synopsis, score FROM animes WHERE anime_id IN ({placeholders})",
            anime_ids,
        )
        return {row[0]: _anime_row_to_dict(row) for row in cursor.fetchall()}


@router.get("/health")
def health(request: Request):
    return {"status": "ok", "model_version": getattr(request.app.state, "model_version", None)}


@router.get("/users/{user_id}/recommendations")
def get_recommendations(user_id: int, request: Request, top_n: int = 10):
    recommender = request.app.state.recommender

    # Notes de l'utilisateur ; en cas de notes multiples sur un même anime, la dernière compte
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT anime_id, rating FROM ratings WHERE user_id = ? ORDER BY rating_id", (user_id,)
        )
        ratings = {anime_id: rating for anime_id, rating in cursor.fetchall()}

    # Profil calculé à la volée à partir des notes : pas besoin de réentraîner le modèle.
    # Plus de candidats que nécessaire : certains animés ne sont pas dans le catalogue
    candidates = recommender.recommend_from_ratings(ratings, k=top_n * 3) if ratings else None
    if candidates is None:
        raise HTTPException(
            status_code=404, detail="Notez quelques animés pour recevoir des recommandations."
        )

    infos = get_animes_info(candidates)
    recommendations = [infos[a] for a in candidates if a in infos][:top_n]

    # Historique des recommandations servies
    with db_cursor() as cursor:
        cursor.executemany(
            "INSERT INTO recommendations (user_id, anime_id) VALUES (?, ?)",
            [(user_id, anime["anime_id"]) for anime in recommendations],
        )
    return recommendations


def _find_user(cursor, username):
    cursor.execute("SELECT user_id, username FROM users WHERE username = ?", (username,))
    return cursor.fetchone()


@router.post("/users", response_model=UserResponse)
def login(request: LoginRequest):
    """Retrouve l'utilisateur par son pseudo (insensible à la casse), ou le crée."""
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Le pseudo ne peut pas être vide.")

    with db_cursor() as cursor:
        row = _find_user(cursor, username)
    if row:
        return {"user_id": row[0], "username": row[1], "created": False}

    try:
        with db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username) OUTPUT INSERTED.user_id VALUES (?)", (username,)
            )
            user_id = cursor.fetchone()[0]
        return {"user_id": user_id, "username": username, "created": True}
    except Exception:
        # Pseudo créé au même moment par une autre requête (contrainte d'unicité)
        with db_cursor() as cursor:
            row = _find_user(cursor, username)
        if not row:
            raise
        return {"user_id": row[0], "username": row[1], "created": False}


@router.get("/users/{user_id}/ratings")
def get_user_ratings(user_id: int):
    """Animés notés par l'utilisateur, du plus récent au plus ancien."""
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT r.anime_id, r.rating, a.name, a.image_url, a.synopsis, a.score
            FROM ratings r JOIN animes a ON a.anime_id = r.anime_id
            WHERE r.user_id = ?
            ORDER BY r.rating_id
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
    # Une seule entrée par anime : la note la plus récente
    latest = {}
    for anime_id, rating, name, image_url, synopsis, score in rows:
        latest.pop(anime_id, None)
        latest[anime_id] = {
            "anime_id": anime_id,
            "rating": rating,
            "name": name,
            "image_url": image_url,
            "synopsis": synopsis,
            "score": score,
        }
    return list(reversed(latest.values()))


@router.delete("/users/{user_id}/ratings/{anime_id}", status_code=204)
def delete_user_rating(user_id: int, anime_id: int):
    with db_cursor() as cursor:
        cursor.execute("DELETE FROM ratings WHERE user_id = ? AND anime_id = ?", (user_id, anime_id))


@router.post("/ratings", response_model=List[RatingRequest])
def create_ratings(ratings: List[RatingRequest], background_tasks: BackgroundTasks):
    if not ratings:
        return ratings

    # Une note par anime et par utilisateur : noter à nouveau remplace l'ancienne note
    with db_cursor() as cursor:
        for r in ratings:
            cursor.execute(
                "UPDATE ratings SET rating = ? WHERE user_id = ? AND anime_id = ?",
                (r.rating, r.user_id, r.anime_id),
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    "INSERT INTO ratings (user_id, anime_id, rating) VALUES (?, ?, ?)",
                    (r.user_id, r.anime_id, r.rating),
                )

    # Ajout au jeu d'entraînement sans bloquer la réponse
    background_tasks.add_task(save_ratings_for_training, ratings)
    return ratings


@router.get("/animes/top")
def get_top_animes(limit: int = 100):
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT anime_id, name, image_url, synopsis, score
            FROM animes
            WHERE score IS NOT NULL
            ORDER BY score DESC
            OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
            """,
            (limit,),
        )
        return [_anime_row_to_dict(anime) for anime in cursor.fetchall()]


@router.get("/animes/search")
def search_animes(query: str, limit: int = 20):
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT anime_id, name, image_url, synopsis, score
            FROM animes
            WHERE name LIKE ?
            ORDER BY score DESC
            OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
            """,
            (f"%{query}%", limit),
        )
        return [_anime_row_to_dict(anime) for anime in cursor.fetchall()]


@router.get("/animes/similar/{anime_id}")
def get_similar_animes(anime_id: int, request: Request, top_n: int = 5):
    recommender = request.app.state.recommender

    # On demande plus de candidats que nécessaire : certains animés du modèle
    # n'ont pas de score et ne sont donc pas dans la table animes
    candidates = recommender.similar_items(anime_id, k=top_n * 3)
    if candidates is None:
        raise HTTPException(status_code=404, detail="Anime non trouvé.")

    infos = get_animes_info([candidate_id for candidate_id, _ in candidates])
    anime_details = [
        {
            "anime_id": candidate_id,
            "similarity": similarity,
            "name": infos[candidate_id]["name"],
            "synopsis": infos[candidate_id]["synopsis"],
            "image_url": infos[candidate_id]["image_url"],
        }
        for candidate_id, similarity in candidates
        if candidate_id in infos
    ]
    return anime_details[:top_n]


@router.get("/animes/{anime_id}")
def get_anime(anime_id: int):
    anime = get_animes_info([anime_id]).get(anime_id)
    if anime is None:
        raise HTTPException(status_code=404, detail="Anime non trouvé.")
    return anime
