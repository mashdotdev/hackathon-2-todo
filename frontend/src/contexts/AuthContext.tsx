"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import Cookies from "js-cookie";
import { api } from "@/lib/api";
import type { User, UserCreate, UserLogin } from "@/types";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: UserLogin) => Promise<void>;
  register: (data: UserCreate) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = Cookies.get("token");
      if (token) {
        try {
          const currentUser = await api.getCurrentUser();
          setUser(currentUser);
        } catch {
          Cookies.remove("token");
        }
      }
      setIsLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (data: UserLogin) => {
    const response = await api.login(data);
    Cookies.set("token", response.access_token, { expires: 1 });
    setUser(response.user);
  };

  const register = async (data: UserCreate) => {
    const response = await api.register(data);
    Cookies.set("token", response.access_token, { expires: 1 });
    setUser(response.user);
  };

  const logout = async () => {
    try {
      await api.logout();
    } finally {
      Cookies.remove("token");
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
