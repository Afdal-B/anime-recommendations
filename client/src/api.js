import axios from "axios";

// En dev, /api est redirigé vers localhost:8000 (voir "proxy" dans package.json)
const api = axios.create({ baseURL: "/api" });

export const getErrorMessage = (error) =>
  error?.response?.data?.detail ||
  "Le serveur ne répond pas. Réessayez dans quelques instants.";

export default api;
