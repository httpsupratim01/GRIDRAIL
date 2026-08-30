import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { djangoApi, setAuthToken } from "../services/api";

type User = {
  id: number;
  username: string;
  email: string;
  role: "PASSENGER" | "ADMIN";
  phone?: string;
  address?: string;
  avatar_url?: string;
  frequent_journeys?: string[];
};

type AuthContextValue = {
  user: User | null;
  token: string | null;
  login: (identifier: string, password: string) => Promise<void>;
  register: (data: { username: string; email: string; password: string; phone?: string }) => Promise<void>;
  refreshUser: () => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => JSON.parse(localStorage.getItem("railway_user") || "null"));
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("railway_token"));

  useEffect(() => {
    setAuthToken(token || undefined);
  }, [token]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      async login(identifier, password) {
        const { data } = await djangoApi.post("/auth/login", { identifier, password });
        setUser(data.user);
        setToken(data.access);
        localStorage.setItem("railway_user", JSON.stringify(data.user));
        localStorage.setItem("railway_token", data.access);
      },
      async register(payload) {
        const { data } = await djangoApi.post("/auth/register", payload);
        setUser(data.user);
        setToken(data.access);
        localStorage.setItem("railway_user", JSON.stringify(data.user));
        localStorage.setItem("railway_token", data.access);
      },
      async refreshUser() {
        const { data } = await djangoApi.get("/auth/profile");
        setUser(data);
        localStorage.setItem("railway_user", JSON.stringify(data));
      },
      logout() {
        setUser(null);
        setToken(null);
        localStorage.removeItem("railway_user");
        localStorage.removeItem("railway_token");
      }
    }),
    [user, token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
