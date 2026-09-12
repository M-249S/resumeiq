import { useEffect, useState, useCallback, type ReactNode } from "react";
import { AuthContext } from "@/context/AuthContext";
import { loginUser, registerUser, getCurrentUser } from "@/services/auth";
import type { User, RegisterPayload } from "@/types/auth";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  // Only start "loading" if a token is actually present — avoids a
  // synchronous setState-in-effect just to turn loading back off when
  // there was nothing to fetch in the first place.
  const [loading, setLoading] = useState(
    () => Boolean(localStorage.getItem("access_token")),
  );

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    // Re-fetch the real user from the backend instead of trusting a
    // locally-cached copy — /auth/me is the source of truth.
    getCurrentUser()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await loginUser(email, password);
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);

    const currentUser = await getCurrentUser();
    setUser(currentUser);
  }, []);

  const register = useCallback(
    async (payload: RegisterPayload) => {
      await registerUser(payload);
      // Registration doesn't return tokens — log in immediately after so
      // the sign-up flow doesn't dead-end at a login screen.
      await login(payload.email, payload.password);
    },
    [login],
  );

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, isAuthenticated: Boolean(user), login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}
