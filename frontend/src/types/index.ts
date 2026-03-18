/* ── User ── */
export interface DbUser {
  id: string;
  firebase_uid: string;
  email: string;
  display_name: string | null;
  preferred_paper: "CS" | "DA" | null;
  created_at: string;
  updated_at: string;
}

/* ── Dashboard ── */
export interface RecentExam {
  id: string;
  paper: string;
  scope: string;
  difficulty: string;
  total_questions: number;
  total_marks: number;
  status: string;
  score: number | null;
  max_score: number;
  created_at: string;
}

export interface DashboardStats {
  total_exams_taken: number;
  average_score: number | null;
  best_score: number | null;
  worst_score: number | null;
  total_questions_attempted: number;
  recent_exams: RecentExam[];
}

/* ── Auth context value ── */
export interface AuthContextValue {
  firebaseUser: import("firebase/auth").User | null;
  dbUser: DbUser | null;
  loading: boolean;
  signup: (
    email: string,
    password: string,
    displayName: string
  ) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}