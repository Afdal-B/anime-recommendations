import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../api";
import AnimeImage from "../components/AnimeImage";
import AnimeTile from "../components/AnimeTile";
import ForYou from "../components/ForYou";
import useAnimeSearch from "../hooks/useAnimeSearch";
import { CardSkeleton, ErrorState } from "../components/States";

const SearchAnimePage = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const { results: suggestions, searching } = useAnimeSearch(query);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [open, setOpen] = useState(false);

  const [topAnimes, setTopAnimes] = useState([]);
  const [topError, setTopError] = useState(null);
  const [topLoading, setTopLoading] = useState(true);

  // Nouvelle liste de suggestions : aucune n'est présélectionnée
  useEffect(() => setActiveIndex(-1), [suggestions]);

  const loadTop = () => {
    setTopLoading(true);
    setTopError(null);
    api
      .get("/animes/top", { params: { limit: 12 } })
      .then((response) => setTopAnimes(response.data))
      .catch((error) => setTopError(getErrorMessage(error)))
      .finally(() => setTopLoading(false));
  };

  useEffect(loadTop, []);

  const openAnime = (anime) => navigate(`/predictions/${anime.anime_id}`);

  const handleKeyDown = (e) => {
    if (!suggestions.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setOpen(true);
      setActiveIndex((i) => (i + 1) % suggestions.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => (i <= 0 ? suggestions.length - 1 : i - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      openAnime(suggestions[Math.max(activeIndex, 0)]);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  const showDropdown = open && query.trim().length >= 2;

  return (
    <div>
      <section className="mx-auto max-w-2xl pb-14 pt-6 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Trouvez votre{" "}
          <span className="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
            prochain anime
          </span>
        </h1>
        <p className="mt-4 text-slate-400">
          Choisissez un anime que vous aimez : le modèle de filtrage collaboratif vous propose
          ceux qu'apprécient les spectateurs aux goûts similaires.
        </p>

        <div className="relative mt-8 text-left">
          <input
            type="search"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setOpen(true);
            }}
            onFocus={() => setOpen(true)}
            onBlur={() => setTimeout(() => setOpen(false), 150)}
            onKeyDown={handleKeyDown}
            placeholder="Naruto, Frieren, Cowboy Bebop…"
            aria-label="Rechercher un anime"
            role="combobox"
            aria-expanded={showDropdown}
            aria-controls="search-suggestions"
            className="w-full rounded-2xl border border-white/10 bg-slate-900 px-5 py-4 text-lg placeholder-slate-500 shadow-xl shadow-violet-950/30 outline-none transition focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20"
          />
          {searching && (
            <div className="absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 animate-spin rounded-full border-2 border-slate-600 border-t-violet-400" />
          )}

          {showDropdown && !searching && (
            <ul
              id="search-suggestions"
              role="listbox"
              className="absolute left-0 right-0 z-20 mt-2 max-h-96 overflow-y-auto rounded-2xl border border-white/10 bg-slate-900 p-1 shadow-2xl"
            >
              {suggestions.length === 0 ? (
                <li className="px-4 py-3 text-slate-500">Aucun anime trouvé.</li>
              ) : (
                suggestions.map((anime, index) => (
                  <li
                    key={anime.anime_id}
                    role="option"
                    aria-selected={index === activeIndex}
                    onMouseDown={() => openAnime(anime)}
                    onMouseEnter={() => setActiveIndex(index)}
                    className={`flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 ${
                      index === activeIndex ? "bg-violet-500/15" : ""
                    }`}
                  >
                    <AnimeImage src={anime.image_url} alt="" className="h-14 w-10 shrink-0 rounded-md text-base" />
                    <span className="flex-1 truncate">{anime.name}</span>
                    {anime.score && (
                      <span className="text-sm text-amber-400">★ {anime.score.toFixed(2)}</span>
                    )}
                  </li>
                ))
              )}
            </ul>
          )}
        </div>
      </section>

      <ForYou />

      <section>
        <h2 className="mb-5 text-xl font-semibold">Les mieux notés</h2>
        {topError ? (
          <ErrorState message={topError} onRetry={loadTop} />
        ) : (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
            {topLoading ? (
              <CardSkeleton count={12} />
            ) : (
              topAnimes.map((anime) => (
                <AnimeTile key={anime.anime_id} anime={anime} onClick={() => openAnime(anime)} />
              ))
            )}
          </div>
        )}
      </section>
    </div>
  );
};

export default SearchAnimePage;
