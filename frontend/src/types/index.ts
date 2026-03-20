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

/* ── Syllabus ── */
export interface TopicFlat {
  id: number;
  section_name: string;
  topic: string;
}

export interface TopicListResponse {
  paper: string;
  total_topics: number;
  topics: TopicFlat[];
}

/* ── Exam Config ── */
export interface TypesRatio {
  MCQ: number;
  MSQ: number;
  NAT: number;
}

export interface ExamConfig {
  paper: "CS" | "DA";
  scope: "full" | "topic";
  selected_topics: string[];
  difficulty: "easy" | "medium" | "hard" | "auto";
  types_ratio: TypesRatio;
}

export interface ExamGenerateResponse {
  exam_id: string;
  status: string;
  message: string;
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