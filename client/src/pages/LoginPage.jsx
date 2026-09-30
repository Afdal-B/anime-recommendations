import React, { useRef, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../api";
import { useUser } from "../user";

const LoginPage = () => {
  const { user, login } = useUser();
  const [username, setUsername] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  // Déjà identifié en arrivant sur la page : directement vers le profil
  // (pas après la connexion, qui choisit elle-même la page suivante)
  const alreadyLoggedIn = useRef(Boolean(user));

  if (alreadyLoggedIn.current) return <Navigate to="/profil" replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const response = await api.post("/users", { username: username.trim() });
      login(response.data);
      // Nouveau profil : on commence par noter ; profil existant : on le retrouve
      navigate(response.data.created ? "/rating" : "/profil");
    } catch (error) {
      setError(getErrorMessage(error));
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-md pt-10">
      <div className="rounded-3xl bg-slate-900 p-8 ring-1 ring-white/5">
        <h1 className="text-2xl font-bold">Votre profil</h1>
        <p className="mt-2 text-sm text-slate-400">
          Entrez votre pseudo. Si vous êtes déjà venu, vous retrouverez vos notes et vos
          recommandations ; sinon, un profil est créé.
        </p>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-300">Pseudo</span>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="ex. spike_spiegel"
              maxLength={50}
              required
              autoFocus
              className="w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 placeholder-slate-600 outline-none transition focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20"
            />
          </label>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button
            type="submit"
            disabled={submitting || !username.trim()}
            className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 px-6 py-3 font-semibold transition hover:brightness-110 disabled:opacity-50"
          >
            {submitting ? "Connexion…" : "Continuer"}
          </button>
        </form>
        <p className="mt-4 text-xs text-slate-500">
          Il n'y a pas de mot de passe : quiconque connaît votre pseudo peut ouvrir votre profil.
          Choisissez-en un qui ne se devine pas.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
