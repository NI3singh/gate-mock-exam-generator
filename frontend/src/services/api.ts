import axios from "axios";
import { auth } from "../config/firebase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

/*
 * Automatically attach the Firebase JWT to every outgoing request.
 * `getIdToken()` returns a cached token or transparently refreshes it.
 */
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/*
 * If the backend ever returns 401 (token expired / revoked),
 * sign the user out so the UI drops back to the login screen.
 */
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      // Avoid an infinite loop during login / register
      const url: string = error.config?.url ?? "";
      if (!url.includes("/auth/register") && !url.includes("/auth/me")) {
        await auth.signOut();
      }
    }
    return Promise.reject(error);
  }
);

export default api;