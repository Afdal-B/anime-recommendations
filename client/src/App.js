import ReactDom from "react-dom/client";
import SearchAnimePage from "./pages/SearchAnimePage";
import PredictionPage from "./pages/PredictionPage";
import LoginPage from "./pages/LoginPage";
import RatingPage from "./pages/RatingPage";
import { Routes, Route } from "react-router";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<SearchAnimePage />} />
      <Route path="/predictions/:id" element={<PredictionPage />} />
      <Route path="/rating" element={<RatingPage />} />
    </Routes>
  );
}
