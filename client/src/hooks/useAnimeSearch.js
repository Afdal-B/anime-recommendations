import { useEffect, useState } from "react";
import api from "../api";

// Recherche d'animés par nom, avec délai de frappe ; les requêtes périmées sont annulées
const useAnimeSearch = (query, limit = 8) => {
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setResults([]);
      setSearching(false);
      return;
    }
    const controller = new AbortController();
    setSearching(true);
    const timer = setTimeout(() => {
      api
        .get("/animes/search", { params: { query: trimmed, limit }, signal: controller.signal })
        .then((response) => {
          setResults(response.data);
          setSearching(false);
        })
        .catch((error) => {
          if (error.name !== "CanceledError") {
            setResults([]);
            setSearching(false);
          }
        });
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, limit]);

  return { results, searching };
};

export default useAnimeSearch;
