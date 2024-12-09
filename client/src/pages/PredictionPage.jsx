import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
import { ClipLoader } from "react-spinners"; // Importation du composant ClipLoader

const PredictionPage = () => {
  const { id: animeId } = useParams();
  const [similarAnimes, setSimilarAnimes] = useState([]);
  const [loading, setLoading] = useState(true); // État pour gérer le chargement

  useEffect(() => {
    axios
      .get(`http://localhost:8000/animes/similar/${animeId}`)
      .then((response) => {
        setSimilarAnimes(response.data);
        setLoading(false); // Arrêter le chargement une fois les données récupérées
      })
      .catch((error) => {
        console.error(
          "Erreur lors de la récupération des animes similaires :",
          error
        );
        setLoading(false); // Arrêter le chargement en cas d'erreur
      });
  }, [animeId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#e3f2fd] to-[#90caf9] py-12">
      <div className="container mx-auto px-6">
        <h1 className="text-6xl font-bold text-center text-blue-900 mb-12 drop-shadow-md">
          Explorez des Animes Similaires
        </h1>
        {loading ? ( // Afficher le loader pendant le chargement
          <div className="flex justify-center">
            <ClipLoader color="#007bff" loading={loading} size={50} />
          </div>
        ) : similarAnimes.length === 0 ? (
          <p className="text-center text-gray-700 text-xl">
            Aucun anime similaire trouvé.
          </p>
        ) : (
          <div className="grid gap-10 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {similarAnimes.map((anime) => (
              <div
                key={anime.anime_id}
                className="bg-white rounded-3xl shadow-lg hover:shadow-2xl hover:scale-105 transform transition-all duration-300 group"
              >
                {/* Image Section */}
                <div className="relative">
                  <img
                    src={anime.image_url}
                    alt={anime.name}
                    className="w-full h-64 object-cover rounded-t-3xl"
                  />
                  <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-black/30 to-transparent rounded-t-3xl"></div>
                  <h2 className="absolute bottom-4 left-4 text-2xl font-semibold text-white group-hover:text-yellow-400 transition-all duration-300 drop-shadow-lg">
                    {anime.name}
                  </h2>
                </div>
                {/* Content Section */}
                <div className="p-6">
                  <p className="text-gray-700 text-sm mb-6 line-clamp-4">
                    {anime.synopsis}
                  </p>
                  <a
                    href={`/anime/${anime.anime_id}`}
                    className="block text-center px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-800 text-white text-sm font-bold rounded-full shadow-md hover:shadow-lg hover:from-blue-500 hover:to-blue-700 transition-all duration-300"
                  >
                    Voir Détails
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionPage;
