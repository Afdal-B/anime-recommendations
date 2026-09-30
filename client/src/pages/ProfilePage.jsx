import React, { useEffect, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import api, { getErrorMessage } from "../api";
import AnimeCard from "../components/AnimeCard";
import ForYou from "../components/ForYou";
import { ErrorState } from "../components/States";
import { useUser } from "../user";

const ProfilePage = () => {
  const { user } = useUser();
  const { state } = useLocation();
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Incrémenté à chaque modification de note : les recommandations sont recalculées
  const [version, setVersion] = useState(0);

  const loadRatings = () => {
    setLoading(true);
    setError(null);
    api
      .get(`/users/${user.userId}/ratings`)
      .then((response) => setRatings(response.data))
      .catch((error) => setError(getErrorMessage(error)))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (user) loadRatings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  if (!user) return <Navigate to="/login" replace />;

  // Modifier ou retirer une note est enregistré tout de suite
  const handleRatingChange = (anime, rating) => {
    const request =
      rating == null
        ? api.delete(`/users/${user.userId}/ratings/${anime.anime_id}`)
        : api.post("/ratings", [{ user_id: user.userId, anime_id: anime.anime_id, rating }]);
    request
      .then(() => {
        setRatings((current) =>
          rating == null
            ? current.filter((r) => r.anime_id !== anime.anime_id)
            : current.map((r) => (r.anime_id === anime.anime_id ? { ...r, rating } : r))
        );
        setVersion((v) => v + 1);
      })
      .catch((error) => setError(getErrorMessage(error)));
  };

  const rated = state?.rated;

  return (
    <div>
      {rated > 0 && (
        <p className="mb-6 rounded-xl bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300 ring-1 ring-emerald-500/20">
          {rated} note{rated > 1 ? "s" : ""} enregistrée{rated > 1 ? "s" : ""} : vos
          recommandations sont à jour.
        </p>
      )}

      <div className="mb-10 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium uppercase tracking-wider text-violet-300">Profil</p>
          <h1 className="mt-1 text-3xl font-bold">{user.username}</h1>
          {!loading && !error && (
            <p className="mt-2 text-slate-400">
              {ratings.length} anime{ratings.length > 1 ? "s" : ""} noté{ratings.length > 1 ? "s" : ""}
            </p>
          )}
        </div>
        <Link
          to="/rating"
          className="rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 px-4 py-2 text-sm font-semibold hover:brightness-110"
        >
          Noter d'autres animés
        </Link>
      </div>

      <h2 className="mb-5 text-xl font-semibold">Vos recommandations</h2>
      <ForYou count={12} title={false} refreshKey={version} />

      <h2 className="mb-2 text-xl font-semibold">Vos notes</h2>
      <p className="mb-5 text-sm text-slate-400">
        Changez une note ou cliquez de nouveau dessus pour la retirer : vos recommandations
        s'adaptent aussitôt.
      </p>
      {error ? (
        <ErrorState message={error} onRetry={loadRatings} />
      ) : loading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }, (_, i) => (
            <div key={i} className="h-36 animate-pulse rounded-2xl bg-slate-900" />
          ))}
        </div>
      ) : ratings.length === 0 ? (
        <p className="text-slate-400">Vous n'avez encore noté aucun anime.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {ratings.map((anime) => (
            <AnimeCard
              key={anime.anime_id}
              anime={anime}
              rating={anime.rating}
              onRatingChange={handleRatingChange}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
