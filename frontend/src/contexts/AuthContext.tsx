import {
  createContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
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
  const fetchProfile = useCallback(async (): Promise<DbUser | null> => {
    try {
      const { data } = await api.get<DbUser>("/auth/me");
      setDbUser(data);
      return data;
    } catch {
      setDbUser(null);
      return null;
    }
  }, []);

  /* ── Listen for Firebase auth-state changes ── */
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setFirebaseUser(user);

      if (user) {
        // User is signed-in → try to load their DB profile
        await fetchProfile();
      } else {
        setDbUser(null);
      }

      setLoading(false);
    });

    return () => unsubscribe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* ── Signup (Firebase + backend registration) ── */
  const signup = useCallback(
    async (email: string, password: string, displayName: string) => {
      // 1. Create Firebase account (auto signs-in)
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      setFirebaseUser(cred.user);

      // 2. Register in our PostgreSQL database
      const token = await cred.user.getIdToken();
      const { data } = await api.post<DbUser>(
        "/auth/register",
        { display_name: displayName },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setDbUser(data);
    },
    []
  );

  /* ── Login ── */
  const login = useCallback(async (email: string, password: string) => {
    const cred = await signInWithEmailAndPassword(auth, email, password);
    setFirebaseUser(cred.user);

    // Eagerly fetch profile instead of waiting for onAuthStateChanged
    const token = await cred.user.getIdToken();
    try {
      const { data } = await api.get<DbUser>("/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDbUser(data);
    } catch {
      /* profile will arrive via onAuthStateChanged fallback */
    }
  }, []);

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