import {
  createContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import axios from "axios";
import {
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signOut,
  type User as FirebaseUser,
} from "firebase/auth";

import { auth } from "../config/firebase";
import api from "../services/api";
import type { AuthContextValue, DbUser } from "../types";

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [dbUser, setDbUser] = useState<DbUser | null>(null);
  const [loading, setLoading] = useState(true);

  /* ── Fetch the PostgreSQL profile for the signed-in user ── */
  const getAuthHeaders = useCallback(async (user: FirebaseUser) => {
    const token = await user.getIdToken(true);
    return { Authorization: `Bearer ${token}` };
  }, []);

  const registerProfile = useCallback(
    async (
      user: FirebaseUser,
      profile?: {
        displayName?: string | null;
        preferredPaper?: DbUser["preferred_paper"];
      }
    ): Promise<DbUser> => {
      const headers = await getAuthHeaders(user);
      const fallbackDisplayName =
        profile?.displayName?.trim() ||
        user.displayName?.trim() ||
        user.email?.split("@")[0] ||
        null;

      const { data } = await api.post<DbUser>(
        "/auth/register",
        {
          display_name: fallbackDisplayName,
          preferred_paper: profile?.preferredPaper ?? null,
        },
        { headers }
      );

      setDbUser(data);
      return data;
    },
    [getAuthHeaders]
  );

  const syncProfile = useCallback(
    async (user: FirebaseUser): Promise<DbUser> => {
      const headers = await getAuthHeaders(user);

      try {
        const { data } = await api.get<DbUser>("/auth/me", { headers });
        setDbUser(data);
        return data;
      } catch (error) {
        const detail =
          axios.isAxiosError(error) &&
          typeof error.response?.data?.detail === "string"
            ? error.response.data.detail
            : "";

        const shouldRegister =
          axios.isAxiosError(error) &&
          error.response?.status === 401 &&
          detail.includes("User not registered");

        if (!shouldRegister) {
          setDbUser(null);
          throw error;
        }

        return registerProfile(user);
      }
    },
    [getAuthHeaders, registerProfile]
  );

  /* ── Listen for Firebase auth-state changes ── */
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setLoading(true);
      setFirebaseUser(user);

      if (user) {
        // User is signed-in → try to load their DB profile
        try {
          await syncProfile(user);
        } catch {
          setDbUser(null);
        }
      } else {
        setDbUser(null);
      }

      setLoading(false);
    });

    return () => unsubscribe();
  }, [syncProfile]);

  /* ── Signup (Firebase + backend registration) ── */
  const signup = useCallback(
    async (email: string, password: string, displayName: string) => {
      // 1. Create Firebase account (auto signs-in)
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      setFirebaseUser(cred.user);

      // 2. Register in our PostgreSQL database
      try {
        await registerProfile(cred.user, { displayName });
      } catch (error) {
        await signOut(auth);
        setFirebaseUser(null);
        setDbUser(null);
        throw error;
      }
    },
    [registerProfile]
  );

  /* ── Login ── */
  const login = useCallback(
    async (email: string, password: string) => {
      const cred = await signInWithEmailAndPassword(auth, email, password);
      setFirebaseUser(cred.user);

      try {
        await syncProfile(cred.user);
      } catch (error) {
        await signOut(auth);
        setFirebaseUser(null);
        setDbUser(null);
        throw error;
      }
    },
    [syncProfile]
  );

  /* ── Logout ── */
  const logout = useCallback(async () => {
    await signOut(auth);
    setFirebaseUser(null);
    setDbUser(null);
  }, []);

  /* ── Password reset ── */
  const resetPassword = useCallback(async (email: string) => {
    await sendPasswordResetEmail(auth, email);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        firebaseUser,
        dbUser,
        loading,
        signup,
        login,
        logout,
        resetPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
