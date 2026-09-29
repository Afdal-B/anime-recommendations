import React from "react";
import AnimeImage from "./AnimeImage";

// Vignette cliquable : affiche, titre et, au choix, le score ou un badge (ex. % de similarité)
const AnimeTile = ({ anime, onClick, badge }) => (
  <button
    onClick={onClick}
    className="group overflow-hidden rounded-2xl bg-slate-900 text-left ring-1 ring-white/5 transition hover:-translate-y-1 hover:ring-violet-500/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
  >
    <div className="relative overflow-hidden">
      <AnimeImage
        src={anime.image_url}
        alt={anime.name}
        className="aspect-[3/4] w-full transition duration-300 group-hover:scale-105"
      />
      {(badge || anime.score) && (
        <span className="absolute right-2 top-2 rounded-full bg-slate-950/80 px-2 py-0.5 text-xs font-semibold text-amber-400 backdrop-blur">
          {badge || `★ ${anime.score.toFixed(2)}`}
        </span>
      )}
    </div>
    <div className="p-3">
      <p className="line-clamp-2 text-sm font-medium">{anime.name}</p>
    </div>
  </button>
);

export default AnimeTile;
