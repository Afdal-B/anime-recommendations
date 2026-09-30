import React, { createContext, useCallback, useContext, useState } from "react";

// L'utilisateur est conservé dans le localStorage (pas d'authentification réelle)
const readStoredUser = () => {
  try {
    const userId = localStorage.getItem("userId");
    const username = localStorage.getItem("username");
    return userId ? { userId: parseInt(userId, 10), username } : null;
  } catch {
    return null;
  }
};

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(readStoredUser);

  const login = useCallback(({ user_id, username }) => {
    try {
      localStorage.setItem("userId", user_id);
      localStorage.setItem("username", username);
    } catch {}
    setUser({ userId: user_id, username });
  }, []);

  const logout = useCallback(() => {
    try {
      localStorage.removeItem("userId");
      localStorage.removeItem("username");
    } catch {}
    setUser(null);
  }, []);

  return (
    <UserContext.Provider value={{ user, login, logout }}>{children}</UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
