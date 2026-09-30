import React, { useState } from "react";
import AnimeImage from "./AnimeImage";

const RATINGS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

const AnimeCard = ({ anime, rating, onRatingChange }) => {
  const [showSynopsis, setShowSynopsis] = useState(false);
  const rated = rating != null;

  return (
    <div
      className={`flex gap-4 rounded-2xl bg-slate-900 p-3 ring-1 transition ${
        rated ? "ring-violet-500/60" : "ring-white/5"
      }`}
    >
      <AnimeImage src={anime.image_url} alt={anime.name} className="h-32 w-24 shrink-0 rounded-xl" />
      <div className="flex min-w-0 flex-1 flex-col">
        <h2 className="line-clamp-2 font-semibold leading-snug">{anime.name}</h2>
        <div className="mt-1 flex items-center gap-3 text-xs">
          {anime.score && <span className="text-amber-400">★ {anime.score.toFixed(2)}</span>}
          <button
            onClick={() => setShowSynopsis(!showSynopsis)}
            className="text-slate-400 hover:text-white"
            aria-expanded={showSynopsis}
          >
            {showSynopsis ? "Masquer le synopsis" : "Synopsis"}
          </button>
        </div>
        {showSynopsis && (
          <p className="mt-2 max-h-32 overflow-y-auto text-xs leading-relaxed text-slate-400">{anime.synopsis}</p>
        )}

        <div className="mt-auto pt-3">
          <div className="mb-1 flex items-center justify-between text-xs">
            <span className="text-slate-500">Votre note</span>
            <span className={rated ? "font-semibold text-violet-300" : "text-slate-600"}>
              {rated ? `${rating}/10` : "Non noté"}
            </span>
          </div>
          <div className="flex gap-0.5" role="radiogroup" aria-label={`Noter ${anime.name}`}>
            {RATINGS.map((value) => (
              <button
                key={value}
                role="radio"
                aria-checked={rating === value}
                aria-label={`${value} sur 10`}
                title={`${value}/10`}
                // Un second clic sur la note choisie l'annule
                onClick={() => onRatingChange(anime, rating === value ? null : value)}
                className={`h-6 flex-1 rounded transition-colors ${
                  rated && value <= rating
                    ? "bg-gradient-to-t from-violet-600 to-fuchsia-500"
                    : "bg-slate-800 hover:bg-slate-700"
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnimeCard;
