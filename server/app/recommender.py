import os
import numpy as np
import pandas as pd

# Chemin du modèle ALS entraîné avec PySpark (dossier contenant userFactors/ et itemFactors/)
DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "unzipped", "als_model.zip"
)
# Régularisation utilisée à l'entraînement (regParam dans server/ml/train_als.py)
REG_PARAM = 0.1
# Un anime noté par trop peu de personnes a un vecteur peu fiable : on ne le recommande pas
MIN_ITEM_RATINGS = int(os.getenv("MIN_ITEM_RATINGS", 50))


class ALSRecommender:
    """Sert les prédictions d'un modèle ALS Spark sans JVM.

    Un modèle ALS n'est qu'un ensemble de facteurs latents (parquet) :
    - score(user, item) = produit scalaire des facteurs
    - similarité entre animés = cosinus entre facteurs d'items
    """

    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        self.user_ids, self.user_factors = self._load_factors(model_path, "userFactors")
        self.item_ids, self.item_factors = self._load_factors(model_path, "itemFactors")
        self.user_index = {int(u): i for i, u in enumerate(self.user_ids)}
        self.item_index = {int(a): i for i, a in enumerate(self.item_ids)}

        self.recommendable = self._load_recommendable(model_path)

        # Facteurs normalisés pour la similarité cosinus (vecteurs nuls laissés à 0)
        norms = np.linalg.norm(self.item_factors, axis=1, keepdims=True)
        self.item_factors_normed = np.divide(
            self.item_factors, norms, out=np.zeros_like(self.item_factors), where=norms > 0
        )

    def _load_recommendable(self, model_path):
        """Masque des animés assez notés à l'entraînement (item_counts.csv écrit avec le modèle)."""
        counts_path = os.path.join(model_path, "item_counts.csv")
        if not os.path.exists(counts_path):
            return np.ones(len(self.item_ids), dtype=bool)
        counts = pd.read_csv(counts_path, index_col="anime_id")["count"]
        return counts.reindex(self.item_ids, fill_value=0).to_numpy() >= MIN_ITEM_RATINGS

    @staticmethod
    def _load_factors(model_path, name):
        df = pd.read_parquet(os.path.join(model_path, name))
        ids = df["id"].to_numpy()
        factors = np.vstack(df["features"].to_numpy()).astype(np.float32)
        return ids, factors

    def user_vector_from_ratings(self, ratings, iterations=200):
        """Calcule le vecteur d'un utilisateur à partir de ses notes, sans réentraîner (« fold-in »).

        Les vecteurs des animés restent fixes : c'est une demi-étape d'ALS. On minimise
        ||V u - r||² + λ·n·||u||² sous la contrainte u ≥ 0, comme Spark (nonnegative=True,
        régularisation proportionnelle au nombre de notes n).
        """
        known = [(self.item_index[a], r) for a, r in ratings.items() if a in self.item_index]
        if not known:
            return None
        indices, values = zip(*known)
        V = self.item_factors[list(indices)].astype(np.float64)
        r = np.asarray(values, dtype=np.float64)

        A = V.T @ V + REG_PARAM * len(r) * np.eye(V.shape[1])
        b = V.T @ r
        # Gradient projeté sur u ≥ 0 (problème de dimension 10 : quelques microsecondes)
        step = 1.0 / np.linalg.eigvalsh(A)[-1]
        u = np.zeros_like(b)
        for _ in range(iterations):
            u = np.maximum(u - step * (A @ u - b), 0.0)
        return u.astype(np.float32)

    def recommend_from_ratings(self, ratings, k=10):
        """Animés que l'utilisateur noterait le mieux, d'après ses notes {anime_id: note}.

        Les animés déjà notés sont exclus. Renvoie None si aucune note ne porte sur un
        animé connu du modèle.
        """
        u = self.user_vector_from_ratings(ratings)
        if u is None:
            return None
        scores = self.item_factors @ u
        scores[~self.recommendable] = -np.inf
        for anime_id in ratings:
            if anime_id in self.item_index:
                scores[self.item_index[anime_id]] = -np.inf
        top = np.argsort(-scores)[:k]
        return [int(self.item_ids[i]) for i in top]

    def similar_items(self, anime_id, k=5):
        """Retourne [(anime_id, similarité)] triés par similarité cosinus décroissante."""
        idx = self.item_index.get(anime_id)
        if idx is None:
            return None
        similarities = self.item_factors_normed @ self.item_factors_normed[idx]
        similarities[idx] = -np.inf  # Exclure l'anime lui-même
        similarities[~self.recommendable] = -np.inf
        top = np.argsort(-similarities)[:k]
        return [(int(self.item_ids[i]), float(similarities[i])) for i in top]
