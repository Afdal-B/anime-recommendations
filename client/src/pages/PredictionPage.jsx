import React, { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api, { getErrorMessage } from "../api";
import AnimeImage from "../components/AnimeImage";
import { CardSkeleton, ErrorState } from "../components/States";

const PredictionPage = () => {
  const { id: animeId } = useParams();
  const navigate = useNavigate();
  const [anime, setAnime] = useState(null);
  const [similarAnimes, setSimilarAnimes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      api.get(`/animes/${animeId}`),
      api.get(`/animes/similar/${animeId}`, { params: { top_n: 8 } }),
    ])
      .then(([animeResponse, similarResponse]) => {
        setAnime(animeResponse.data);
        setSimilarAnimes(similarResponse.data);
      })
      .catch((error) => setError(getErrorMessage(error)))
      .finally(() => setLoading(false));
  }, [animeId]);

  useEffect(() => {
    load();
    window.scrollTo(0, 0);
  }, [load]);

  if (error) {
    return (
      <div className="py-10">
        <ErrorState message={error} onRetry={load} />
        <p className="mt-6 text-center">
          <Link to="/" className="text-violet-400 hover:text-violet-300">
            ← Retour à la recherche
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div>
      <Link to="/" className="text-sm text-slate-400 hover:text-white">
        ← Nouvelle recherche
      </Link>

      {/* Anime de référence */}
      {loading || !anime ? (
        <div className="mt-6 flex animate-pulse gap-6">
          <div className="h-48 w-32 rounded-2xl bg-slate-800" />
          <div className="flex-1 space-y-3 pt-2">
            <div className="h-8 w-1/2 rounded bg-slate-800" />
            <div className="h-4 w-full rounded bg-slate-800" />
            <div className="h-4 w-5/6 rounded bg-slate-800" />
          </div>
        </div>
      ) : (
        <section className="mt-6 flex flex-col gap-6 rounded-3xl bg-gradient-to-br from-violet-500/10 to-fuchsia-500/5 p-6 ring-1 ring-white/5 sm:flex-row">
          <AnimeImage src={anime.image_url} alt={anime.name} className="h-48 w-32 shrink-0 rounded-2xl" />
          <div>
            <p className="text-sm font-medium uppercase tracking-wider text-violet-300">Parce que vous aimez</p>
            <h1 className="mt-1 text-3xl font-bold">{anime.name}</h1>
            {anime.score && <p className="mt-1 text-amber-400">★ {anime.score.toFixed(2)}</p>}
            <p className="mt-3 line-clamp-4 max-w-3xl text-sm leading-relaxed text-slate-300">{anime.synopsis}</p>
          </div>
        </section>
      )}

      <h2 className="mb-5 mt-12 text-xl font-semibold">Vous pourriez aussi aimer</h2>
      {!loading && similarAnimes.length === 0 ? (
        <p className="text-slate-400">Aucun anime similaire trouvé.</p>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {loading ? (
            <CardSkeleton count={8} />
          ) : (
            similarAnimes.map((similar) => (
              <button
                key={similar.anime_id}
                onClick={() => navigate(`/predictions/${similar.anime_id}`)}
                className="group flex flex-col overflow-hidden rounded-2xl bg-slate-900 text-left ring-1 ring-white/5 transition hover:-translate-y-1 hover:ring-violet-500/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
              >
                <div className="relative overflow-hidden">
                  <AnimeImage
                    src={similar.image_url}
                    alt={similar.name}
                    className="aspect-[3/4] w-full transition duration-300 group-hover:scale-105"
                  />
                  <span className="absolute right-2 top-2 rounded-full bg-slate-950/80 px-2 py-0.5 text-xs font-semibold text-emerald-400 backdrop-blur">
                    {Math.round(similar.similarity * 100)} % similaire
                  </span>
                </div>
                <div className="flex flex-1 flex-col p-4">
                  <p className="font-semibold">{similar.name}</p>
                  <p className="mt-2 line-clamp-3 text-sm text-slate-400">{similar.synopsis}</p>
                  <p className="mt-auto pt-3 text-sm font-medium text-violet-400 group-hover:text-violet-300">
                    Explorer ses similaires →
                  </p>
                </div>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default PredictionPage;
