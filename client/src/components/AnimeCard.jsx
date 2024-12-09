import React, { useState } from "react";
import { FaInfoCircle } from "react-icons/fa";

const AnimeCard = ({ anime, onRatingChange }) => {
  const [showSynopsis, setShowSynopsis] = useState(false);
  const [rating, setRating] = useState(1);

  const handleRatingChange = (e) => {
    const newRating = e.target.value;
    setRating(newRating);
    onRatingChange(anime.anime_id, newRating);
  };

  return (
    <div className="p-4 border rounded-lg shadow-lg bg-white hover:shadow-xl transition-shadow transform hover:scale-105">
      <h2 className="text-xl font-bold text-gray-800">{anime.name}</h2>
      <img
        src={anime.image_url}
        alt={anime.name}
        className="w-full h-48 object-cover rounded mb-4"
      />
      <div className="flex items-center justify-between mb-2">
        <button
          onClick={() => setShowSynopsis(!showSynopsis)}
          className="flex items-center text-blue-500 hover:text-blue-700"
        >
          <FaInfoCircle className="mr-2" />
          Info
        </button>
        <span className="text-gray-600">Note : {rating}</span>
      </div>
      {showSynopsis && (
        <p className="text-gray-700 text-sm mb-4">{anime.synopsis}</p>
      )}
      <input
        type="range"
        min="1"
        max="10"
        value={rating}
        onChange={handleRatingChange}
        className="w-full"
      />
      <span className="block text-center text-gray-800 font-medium mt-2">
        {rating}/10
      </span>
    </div>
  );
};

export default AnimeCard;
