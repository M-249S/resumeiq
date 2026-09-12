import api from "@/lib/api";
import type { TokenResponse, User, RegisterPayload } from "@/types/auth";

export async function registerUser(payload: RegisterPayload): Promise<User> {
  const response = await api.post<User>("/auth/register", payload);
  return response.data;
}

/**
 * The backend's /auth/login endpoint uses FastAPI's OAuth2PasswordRequestForm,
 * which requires `application/x-www-form-urlencoded` with a `username` field
 * (mapped to email here) — not JSON. This is a real backend contract detail,
 * not a stylistic choice, so it has to match exactly.
 */
export async function loginUser(email: string, password: string): Promise<TokenResponse> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const response = await api.post<TokenResponse>("/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>("/auth/me");
  return response.data;
}
