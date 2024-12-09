import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom"; // Ajout pour gérer les liens

const SearchAnimePage = () => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [selectedAnimeId, setSelectedAnimeId] = useState(null);

  useEffect(() => {
    if (query.length > 2) {
      axios
        .get(`http://localhost:8000/animes/search?query=${query}`)
        .then((response) => {
          setSuggestions(response.data);
        })
        .catch((error) => {
          console.error(
            "Erreur lors de la récupération des suggestions :",
            error
          );
        });
    } else {
      setSuggestions([]);
    }
  }, [query]);

  const handleSelectAnime = (anime) => {
    setSelectedAnimeId(anime.anime_id);
    setQuery(anime.name);
    setSuggestions([]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedAnimeId) {
      window.location.href = `/predictions/${selectedAnimeId}`;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-purple-600 flex justify-center items-center p-6">
      {/* Ajout du bouton "Noter des animés" */}
      <div className="absolute top-4 right-4">
        <Link
          to="/login"
          className="py-2 px-4 bg-gray-800 text-white rounded-lg shadow-md hover:bg-gray-700 transition duration-300"
        >
          Noter des Animés
        </Link>
      </div>

      <div className="w-full max-w-lg bg-white rounded-lg shadow-xl p-8">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
          🔎 Rechercher un Anime
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Entrez le nom de l'anime"
              className="w-full p-4 rounded-lg border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition duration-200"
            />
            {suggestions.length > 0 && (
              <ul className="absolute left-0 right-0 bg-white border border-gray-300 rounded-lg shadow-lg mt-2 max-h-60 overflow-y-auto z-10">
                {suggestions.map((anime) => (
                  <li
                    key={anime.anime_id}
                    onClick={() => handleSelectAnime(anime)}
                    className="px-4 py-2 hover:bg-purple-100 cursor-pointer transition duration-200"
                  >
                    {anime.name}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <button
            type="submit"
            className="w-full py-3 px-6 bg-purple-600 text-white text-lg font-semibold rounded-lg shadow-md hover:bg-purple-700 hover:shadow-lg transition duration-300"
          >
            Prédire les Animés Similaires
          </button>
        </form>
      </div>
    </div>
  );
};

export default SearchAnimePage;
