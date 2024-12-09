import React, { useState, useEffect } from "react";
import axios from "axios";
import AnimeCard from "../components/AnimeCard";
import { useNavigate } from "react-router-dom";

const RatingPage = () => {
  const [animes, setAnimes] = useState([]);
  const [ratings, setRatings] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    // Vérifier si l'utilisateur est connecté
    const userId = localStorage.getItem("userId");
    if (!userId) {
      navigate("/login");
      return;
    }

    axios
      .get("http://localhost:8000/animes/top")
      .then((response) => {
        setAnimes(response.data);
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération des animés :", error);
      });
  }, [navigate]);

  const handleRatingChange = (animeId, rating) => {
    setRatings({
      ...ratings,
      [animeId]: rating,
    });
  };

  const handleSubmit = () => {
    const userId = localStorage.getItem("userId");

    const ratingData = Object.keys(ratings).map((animeId) => ({
      user_id: parseInt(userId),
      anime_id: parseInt(animeId),
      rating: parseInt(ratings[animeId]),
    }));

    axios
      .post("http://localhost:8000/ratings", ratingData)
      .then((response) => {
        console.log("Notes soumises avec succès :", response.data);
        navigate("/search"); // Redirection vers la page de recherche après la soumission
      })
      .catch((error) => {
        console.error("Erreur lors de la soumission des notes :", error);
      });
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
        Noter vos Animés Préférés
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {animes.map((anime) => (
          <AnimeCard
            key={anime.anime_id}
            anime={anime}
            onRatingChange={handleRatingChange}
          />
        ))}
      </div>
      <div className="mt-6 text-center">
        <button
          onClick={handleSubmit}
          className="px-6 py-3 bg-blue-500 text-white font-medium rounded shadow hover:bg-blue-600"
        >
          Soumettre les Notes
        </button>
      </div>
    </div>
  );
};

export default RatingPage;
