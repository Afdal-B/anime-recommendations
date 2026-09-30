import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";
import AnimeTile from "./AnimeTile";
import { CardSkeleton } from "./States";
import { useUser } from "../user";

const RateInvite = ({ children }) => (
  <div className="rounded-2xl bg-gradient-to-br from-violet-500/15 to-fuchsia-500/10 p-6 ring-1 ring-white/5">
    <p className="text-slate-300">{children}</p>
    <Link
      to="/rating"
      className="mt-4 inline-block rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 px-5 py-2.5 text-sm font-semibold hover:brightness-110"
    >
      Noter des animés
    </Link>
  </div>
);

// Recommandations personnelles, calculées par l'API à partir des notes de l'utilisateur
const ForYou = ({ count = 6, title = true, refreshKey = 0 }) => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [animes, setAnimes] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | ready | empty | error

  useEffect(() => {
    if (!user) return;
    // Lors d'un rafraîchissement, les recommandations actuelles restent affichées
    setStatus((current) => (current === "ready" ? current : "loading"));
    api
      .get(`/users/${user.userId}/recommendations`, { params: { top_n: count } })
      .then((response) => {
        setAnimes(response.data);
        setStatus("ready");
      })
      .catch((error) => setStatus(error?.response?.status === 404 ? "empty" : "error"));
  }, [user, count, refreshKey]);

  if (status === "error") return null;

  return (
    <section className="mb-12">
      {title && (
        <h2 className="mb-5 text-xl font-semibold">
          {user ? `Pour vous, ${user.username}` : "Des recommandations rien que pour vous"}
        </h2>
      )}
      {!user ? (
        <RateInvite>
          Notez quelques animés que vous avez vus : l'application en déduit vos goûts et vous
          propose ceux que vous devriez aimer.
        </RateInvite>
      ) : status === "empty" ? (
        <RateInvite>
          Vous n'avez encore noté aucun animé. Quelques notes suffisent pour recevoir vos
          recommandations.
        </RateInvite>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {status === "loading" ? (
            <CardSkeleton count={count} />
          ) : (
            animes.map((anime) => (
              <AnimeTile
                key={anime.anime_id}
                anime={anime}
                onClick={() => navigate(`/predictions/${anime.anime_id}`)}
              />
            ))
          )}
        </div>
      )}
    </section>
  );
};

export default ForYou;
