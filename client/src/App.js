import { Link, Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import SearchAnimePage from "./pages/SearchAnimePage";
import PredictionPage from "./pages/PredictionPage";
import LoginPage from "./pages/LoginPage";
import RatingPage from "./pages/RatingPage";
import AboutPage from "./pages/AboutPage";
import ProfilePage from "./pages/ProfilePage";

const NotFound = () => (
  <div className="py-20 text-center">
    <p className="text-6xl font-bold text-slate-700">404</p>
    <p className="mt-4 text-slate-400">Cette page n'existe pas.</p>
    <Link to="/" className="mt-6 inline-block text-violet-400 hover:text-violet-300">
      Retour à la recherche
    </Link>
  </div>
);

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<SearchAnimePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/predictions/:id" element={<PredictionPage />} />
        <Route path="/rating" element={<RatingPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/profil" element={<ProfilePage />} />
        <Route path="/pour-vous" element={<Navigate to="/profil" replace />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
