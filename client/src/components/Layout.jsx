import React from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useUser } from "../user";

const navClass = ({ isActive }) =>
  `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
    isActive ? "bg-white/10 text-white" : "text-slate-400 hover:text-white"
  }`;

const Layout = () => {
  const { user, logout } = useUser();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-30 border-b border-white/5 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-2 px-4 py-3">
          <NavLink to="/" className="mr-auto flex items-center gap-2 font-bold tracking-tight">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white">
              ア
            </span>
            <span className="hidden sm:inline">AnimeReco</span>
          </NavLink>
          <NavLink to="/" end className={navClass}>
            Rechercher
          </NavLink>
          {user && (
            <NavLink to="/profil" className={navClass}>
              Mon profil
            </NavLink>
          )}
          <NavLink to="/rating" className={navClass}>
            Noter
          </NavLink>
          <NavLink to="/about" className={navClass}>
            À propos
          </NavLink>
          {user && (
            <div className="ml-2 flex items-center gap-2 border-l border-white/10 pl-3 text-sm">
              <span className="hidden text-slate-300 sm:inline">{user.username}</span>
              <button
                onClick={() => {
                  logout();
                  navigate("/");
                }}
                className="text-slate-500 transition-colors hover:text-white"
              >
                Déconnexion
              </button>
            </div>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-10">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
