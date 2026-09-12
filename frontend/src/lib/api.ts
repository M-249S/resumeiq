import axios from "axios";

// Falls back to the local backend dev server so `npm run dev` keeps
// working out of the box. Set VITE_API_URL in a .env file to point at
// a deployed backend.
const baseURL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export const api = axios.create({ baseURL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
