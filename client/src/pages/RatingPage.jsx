import React, { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../api";
import AnimeCard from "../components/AnimeCard";
import { ErrorState } from "../components/States";
import useAnimeSearch from "../hooks/useAnimeSearch";
import { useUser } from "../user";

const CardGrid = ({ animes, ratings, onRatingChange }) => (
  <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
    {animes.map((anime) => (
      <AnimeCard
        key={anime.anime_id}
        anime={anime}
        rating={ratings[anime.anime_id]?.rating}
        onRatingChange={onRatingChange}
      />
    ))}
  </div>
);

const RatingPage = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [animes, setAnimes] = useState([]);
  // Notes en cours, indexées par anime_id : { anime, rating }
  const [ratings, setRatings] = useState({});
  // Notes déjà enregistrées : seules les différences sont envoyées
  const [savedRatings, setSavedRatings] = useState({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const [query, setQuery] = useState("");
  const { results, searching } = useAnimeSearch(query, 12);
  const isSearching = query.trim().length >= 2;

  const loadAnimes = () => {
    setLoading(true);
    setLoadError(null);
    api
      .get("/animes/top", { params: { limit: 60 } })
      .then((response) => setAnimes(response.data))
      .catch((error) => setLoadError(getErrorMessage(error)))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!user) return;
    loadAnimes();
    api
      .get(`/users/${user.userId}/ratings`)
      .then((response) => {
        const saved = Object.fromEntries(
          response.data.map((anime) => [anime.anime_id, { anime, rating: anime.rating }])
        );
        setSavedRatings(saved);
        // Les notes saisies avant la fin du chargement sont conservées
        setRatings((current) => ({ ...saved, ...current }));
      })
      .catch(() => {});
  }, [user]);

  // Pas encore identifié : passer par la création du pseudo
  if (!user) return <Navigate to="/login" replace />;

  const handleRatingChange = (anime, rating) => {
    setRatings((current) => {
      const next = { ...current };
      if (rating == null) delete next[anime.anime_id];
      else next[anime.anime_id] = { anime, rating };
      return next;
    });
  };

  const rated = Object.values(ratings);
  const ratedCount = rated.length;
  const changed = rated.filter(({ anime, rating }) => savedRatings[anime.anime_id]?.rating !== rating);
  const removed = Object.keys(savedRatings).filter((animeId) => !ratings[animeId]);
  const hasChanges = changed.length > 0 || removed.length > 0;

  const handleSubmit = () => {
    const ratingData = changed.map(({ anime, rating }) => ({
      user_id: user.userId,
      anime_id: anime.anime_id,
      rating,
    }));

    setSubmitting(true);
    setSubmitError(null);
    Promise.all([
      ratingData.length ? api.post("/ratings", ratingData) : null,
      ...removed.map((animeId) => api.delete(`/users/${user.userId}/ratings/${animeId}`)),
    ])
      // Les recommandations sont recalculées à partir des notes : on les affiche aussitôt
      .then(() => navigate("/profil", { state: { rated: ratingData.length } }))
      .catch((error) => {
        setSubmitError(getErrorMessage(error));
        setSubmitting(false);
      });
  };

  return (
    <div className="pb-24">
      <h1 className="text-3xl font-bold">Notez les animés que vous avez vus</h1>
      <p className="mt-2 text-slate-400">
        Vos recommandations sont calculées à partir de ces notes. Inutile de tout noter : cinq
        ou six notes suffisent pour commencer. Cliquez de nouveau sur une note pour l'annuler.
      </p>

      <div className="relative mt-6">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Rechercher un anime que vous avez vu…"
          aria-label="Rechercher un anime à noter"
          className="w-full rounded-2xl border border-white/10 bg-slate-900 px-5 py-3.5 placeholder-slate-500 outline-none transition focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20"
        />
        {searching && (
          <div className="absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 animate-spin rounded-full border-2 border-slate-600 border-t-violet-400" />
        )}
      </div>

      {/* Animés déjà notés : restent visibles même s'ils viennent d'une recherche */}
      {ratedCount > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {rated.map(({ anime, rating }) => (
            <span
              key={anime.anime_id}
              className="flex items-center gap-2 rounded-full bg-violet-500/15 py-1 pl-3 pr-1 text-sm ring-1 ring-violet-500/30"
            >
              <span className="max-w-[14rem] truncate">{anime.name}</span>
              <span className="font-semibold text-violet-300">{rating}/10</span>
              <button
                onClick={() => handleRatingChange(anime, null)}
                aria-label={`Retirer la note de ${anime.name}`}
                className="grid h-6 w-6 place-items-center rounded-full text-slate-400 hover:bg-white/10 hover:text-white"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="mt-8">
        {isSearching ? (
          <>
            <h2 className="mb-4 text-lg font-semibold">Résultats pour « {query.trim()} »</h2>
            {!searching && results.length === 0 ? (
              <p className="text-slate-400">Aucun anime trouvé. Essayez avec le titre japonais ou anglais.</p>
            ) : (
              <CardGrid animes={results} ratings={ratings} onRatingChange={handleRatingChange} />
            )}
          </>
        ) : (
          <>
            <h2 className="mb-4 text-lg font-semibold">Les plus populaires</h2>
            {loadError ? (
              <ErrorState message={loadError} onRetry={loadAnimes} />
            ) : loading ? (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 9 }, (_, i) => (
                  <div key={i} className="h-36 animate-pulse rounded-2xl bg-slate-900" />
                ))}
              </div>
            ) : (
              <CardGrid animes={animes} ratings={ratings} onRatingChange={handleRatingChange} />
            )}
          </>
        )}
      </div>

      {/* Barre d'envoi fixe */}
      <div className="fixed inset-x-0 bottom-0 z-20 border-t border-white/5 bg-slate-950/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3">
          <p className="mr-auto text-sm text-slate-400">
            {submitError ? (
              <span className="text-red-400">{submitError}</span>
            ) : ratedCount ? (
              <>
                <span className="font-semibold text-white">{ratedCount}</span> anime
                {ratedCount > 1 ? "s" : ""} noté{ratedCount > 1 ? "s" : ""}
              </>
            ) : (
              "Aucune note pour l'instant"
            )}
          </p>
          <button
            onClick={handleSubmit}
            disabled={!hasChanges || submitting}
            className="rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 px-5 py-2.5 text-sm font-semibold transition hover:brightness-110 disabled:opacity-40"
          >
            {submitting ? "Envoi…" : "Voir mes recommandations"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RatingPage;
