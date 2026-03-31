import axios from "axios";
import toast from "react-hot-toast";
import { auth } from "../config/firebase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

const ERROR_TOAST_DEDUPE_MS = 1500;
let lastErrorToast = {
  message: "",
  timestamp: 0,
};

export function getApiErrorMessage(
  error: unknown,
  fallback = "Something went wrong. Please try again."
): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;

    if (typeof data === "string" && data.trim()) {
      return data.trim();
    }

    if (typeof data?.detail === "string" && data.detail.trim()) {
      return data.detail.trim();
    }

    if (typeof data?.message === "string" && data.message.trim()) {
      return data.message.trim();
    }

    if (Array.isArray(data?.error?.fields) && data.error.fields.length > 0) {
      const firstField = data.error.fields[0];
      if (typeof firstField?.message === "string" && firstField.message.trim()) {
        return firstField.message.trim();
      }
    }

    if (typeof error.message === "string" && error.message.trim()) {
      return error.message.trim();
    }
  }

  if (error instanceof Error && error.message.trim()) {
    return error.message.trim();
  }

  return fallback;
}

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
    const url: string = error.config?.url ?? "";
    const skipAuthRedirect =
      url.includes("/auth/register") || url.includes("/auth/me");

    if (error.response?.status === 401 && !skipAuthRedirect) {
      await auth.signOut();
    }

    if (!error.config?.suppressErrorToast && !(error.response?.status === 401 && skipAuthRedirect)) {
      const message = getApiErrorMessage(error);
      const trimmedMessage =
        message.length > 220 ? `${message.slice(0, 217)}...` : message;
      const now = Date.now();

      if (
        lastErrorToast.message !== trimmedMessage ||
        now - lastErrorToast.timestamp > ERROR_TOAST_DEDUPE_MS
      ) {
        lastErrorToast = {
          message: trimmedMessage,
          timestamp: now,
        };
        toast.error(trimmedMessage);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
