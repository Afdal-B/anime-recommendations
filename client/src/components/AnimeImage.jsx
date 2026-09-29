import React, { useState } from "react";

// Image avec repli si l'URL (MyAnimeList) est cassée
const AnimeImage = ({ src, alt, className = "" }) => {
  const [failed, setFailed] = useState(false);

  if (!src || failed) {
    return (
      <div className={`grid place-items-center bg-slate-800 text-3xl text-slate-600 ${className}`}>
        ア
      </div>
    );
  }
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      onError={() => setFailed(true)}
      className={`bg-slate-800 object-cover ${className}`}
    />
  );
};

export default AnimeImage;
