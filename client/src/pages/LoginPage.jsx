import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/users", {
        username: username,
        user_id: 0, // L'ID sera généré par le backend
      });

      // Stocker l'ID utilisateur dans le localStorage
      localStorage.setItem("userId", response.data.user_id);
      localStorage.setItem("username", response.data.username);

      // Rediriger vers la page de notation
      navigate("/rating");
    } catch (error) {
      console.error("Erreur lors de la création de l'utilisateur:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-purple-600 flex justify-center items-center p-6">
      <div className="w-full max-w-md bg-white rounded-lg shadow-xl p-8">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
          👋 Bienvenue
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Votre pseudo
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Entrez votre pseudo"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full py-3 px-6 bg-purple-600 text-white font-semibold rounded-lg shadow-md hover:bg-purple-700 transition duration-300"
          >
            Commencer
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
