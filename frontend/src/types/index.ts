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

/* ── Exam Screen (Part 8) ── */

export type QuestionType = "MCQ" | "MSQ" | "NAT";
export type QuestionSection = "GA" | "Subject";

/** Status of a question in the palette */
export type QuestionStatus =
  | "not_visited"      // gray  — never opened
  | "not_answered"     // red   — visited but no answer
  | "answered"         // green — has an answer
  | "marked"           // purple — marked for review, no answer
  | "answered_marked"; // blue  — answered AND marked for review

/** Single question item returned by GET /exams/{id} — NO answer field */
export interface QuestionItem {
  id: string;
  qno: number;
  question_type: QuestionType;
  marks: number;
  section: QuestionSection;
  section_name: string;
  topic: string;
  stem_tex: string;
  code_snippet: string | null;
  code_language: string | null;
  choices: string[] | null;
  estimated_time_seconds: number | null;
}

/** Full exam data returned by GET /exams/{id} */
export interface ExamScreenData {
  exam_id: string;
  paper: string;
  difficulty: string;
  total_questions: number;
  total_marks: number;
  duration_minutes: number;
  questions: QuestionItem[];
}

/** Response from POST /exams/{id}/start */
export interface AttemptData {
  attempt_id: string;
  exam_id: string;
  start_time: string;       // ISO 8601
  remaining_seconds: number;
  responses: Record<string, MCQAnswer | MSQAnswer | NATAnswer>;
  question_statuses: Record<string, QuestionStatus>;
  submitted: boolean;
  is_resume: boolean;
}

/** Answer types */
export interface MCQAnswer {
  index: number;
}
export interface MSQAnswer {
  indices: number[];
}
export interface NATAnswer {
  value: string; // stored as string, parsed on submission
}

export type AnyAnswer = MCQAnswer | MSQAnswer | NATAnswer;

/* ── Attempt save & events (Part 9) ── */
export interface AttemptSaveRequest {
  responses: Record<string, AnyAnswer>;
  question_statuses: Record<string, QuestionStatus>;
}

export interface AttemptSaveResponse {
  saved: boolean;
  timestamp: string;
}

export interface AttemptEventRequest {
  event_type: string;
  detail: string | null;
  timestamp: string;
}

export interface AttemptEventResponse {
  logged: boolean;
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

/* ── Result / Submission (Part 10) ── */
export interface AttemptSubmitResponse {
  attempt_id: string;
  exam_id: string;
  paper: string;
  difficulty: string;
  total_questions: number;
  total_marks: number;
  duration_minutes: number;
  score: number;
  max_score: number;
  total_correct: number;
  total_wrong: number;
  total_unanswered: number;
  score_breakdown: {
    section: Record<string, SectionScore>;
    type: Record<string, TypeScore>;
  };
  section_scores: Record<string, SectionScore>;
  topic_analysis: TopicAnalysisItem[];
  violations_count: number;
}

export interface SectionScore {
  correct: number;
  wrong: number;
  unanswered: number;
  score: number;
  max_score: number;
}

export interface TypeScore {
  correct: number;
  wrong: number;
  unanswered: number;
  score: number;
}

export interface TopicAnalysisItem {
  topic: string;
  section_name: string;
  total: number;
  correct: number;
  wrong: number;
  unanswered: number;
  score: number;
  max_score: number;
}