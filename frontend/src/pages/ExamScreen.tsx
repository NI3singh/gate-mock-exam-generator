/**
 * ExamScreen — Part 8
 *
 * Full exam-taking UI:
 *  • Two-panel layout  (question display left + palette right)
 *  • Section tabs      (GA / Subject)
 *  • Question palette  (color-coded by status)
 *  • KaTeX math        (via katex npm package)
 *  • Prism.js code     (syntax highlighting)
 *  • MCQ / MSQ / NAT   (radio / checkbox / numeric)
 *  • Navigation         (Previous, Save & Next, Mark for Review, Clear)
 *  • POST /exams/{id}/start   → creates / resumes attempt
 *  • GET  /exams/{id}         → loads questions (no answers)
 *
 * Part 9 additions:
 *  • Server-authoritative countdown timer (red at < 10 min)
 *  • Debounced auto-save (PUT /attempts/{id}/save every 5 s)
 *  • Anti-cheat: fullscreen, right-click/Ctrl block, visibility/blur,
 *    beforeunload, event logging, violation counter
 */

import { useEffect, useState, useCallback, useMemo, useRef, Component, ReactNode } from "react";
import { useParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

// ── Static imports — always available on first render ─────────────────────────
import katex from "katex";
import "katex/dist/katex.min.css";
import Prism from "prismjs";
import "prismjs/components/prism-python";
import "prismjs/components/prism-c";

import api from "../services/api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import type {
  QuestionItem,
  QuestionStatus,
  QuestionSection,
  ExamScreenData,
  AttemptData,
  MCQAnswer,
  MSQAnswer,
  NATAnswer,
  AnyAnswer,
  AttemptSaveRequest,
} from "../types";

/* ── Error Boundary ─────────────────────────────────────────────────────── */

interface ErrorBoundaryState { hasError: boolean; errorMessage: string }
interface ErrorBoundaryProps { children: ReactNode; fallbackMessage?: string }

class ExamErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, errorMessage: "" };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, errorMessage: error.message };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    console.error("[ExamScreen] Render error:", error, info.componentStack);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
          <div className="text-center max-w-lg p-8 bg-white rounded-2xl border border-red-200 shadow-lg">
            <div className="text-5xl mb-4">⚠️</div>
            <h2 className="text-xl font-bold text-gray-900 mb-3">Something went wrong</h2>
            <p className="text-sm text-red-600 mb-2 font-mono bg-red-50 p-3 rounded-lg">
              {this.state.errorMessage}
            </p>
            <p className="text-xs text-gray-500 mb-6">
              Try refreshing the page. If the problem persists, your exam session is
              auto-saved and you can resume it.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

// ── Status colours ─────────────────────────────────────────────────────────────

const STATUS_BG: Record<QuestionStatus, string> = {
  not_visited:     "bg-gray-200 text-gray-700 hover:bg-gray-300",
  not_answered:    "bg-red-500  text-white   hover:bg-red-600",
  answered:        "bg-green-500 text-white  hover:bg-green-600",
  marked:          "bg-purple-500 text-white hover:bg-purple-600",
  answered_marked: "bg-blue-500 text-white   hover:bg-blue-600",
};

const STATUS_LEGEND: { status: QuestionStatus; label: string; bg: string }[] = [
  { status: "answered",        label: "Answered",          bg: "bg-green-500"  },
  { status: "not_answered",    label: "Not Answered",      bg: "bg-red-500"    },
  { status: "marked",          label: "Marked for Review", bg: "bg-purple-500" },
  { status: "answered_marked", label: "Answered & Marked", bg: "bg-blue-500"   },
  { status: "not_visited",     label: "Not Visited",       bg: "bg-gray-200 border border-gray-400"   },
];

// ── Math renderer ─────────────────────────────────────────────────────────────

function MathText({ text }: { text: string }) {
  const rendered = useMemo(() => {
    try {
      // Split on $$...$$ (display) then $...$ (inline)
      const parts: Array<{ type: "text" | "display" | "inline"; content: string }> = [];

      // Step 1: split on display math $$...$$
      const displaySplit = text.split(/(\$\$[\s\S]*?\$\$)/g);
      const stage1: Array<{ type: "text" | "display"; content: string }> = [];
      for (const chunk of displaySplit) {
        if (chunk.startsWith("$$") && chunk.endsWith("$$") && chunk.length > 4) {
          stage1.push({ type: "display", content: chunk.slice(2, -2) });
        } else {
          stage1.push({ type: "text", content: chunk });
        }
      }

      // Step 2: split text chunks on inline math $...$
      for (const s1 of stage1) {
        if (s1.type === "display") {
          parts.push(s1);
        } else {
          const inlineSplit = s1.content.split(/(\$[^$\n]+?\$)/g);
          for (const chunk of inlineSplit) {
            if (chunk.startsWith("$") && chunk.endsWith("$") && chunk.length > 2) {
              parts.push({ type: "inline", content: chunk.slice(1, -1) });
            } else {
              parts.push({ type: "text", content: chunk });
            }
          }
        }
      }

      // Step 3: render
      const htmlParts: string[] = parts.map((p) => {
        if (p.type === "display") {
          try {
            return katex.renderToString(p.content, {
              displayMode: true,
              throwOnError: false,
              trust: false,
            });
          } catch {
            return `<span class="text-red-500">[Math Error]</span>`;
          }
        } else if (p.type === "inline") {
          try {
            return katex.renderToString(p.content, {
              displayMode: false,
              throwOnError: false,
              trust: false,
            });
          } catch {
            return `<span class="text-red-500">[Math Error]</span>`;
          }
        } else {
          // Preserve newlines as <br>
          return p.content
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\n/g, "<br/>");
        }
      });

      return htmlParts.join("");
    } catch {
      return null;
    }
  }, [text]);

  if (rendered !== null) {
    return (
      <span
        className="math-text leading-relaxed"
        dangerouslySetInnerHTML={{ __html: rendered }}
      />
    );
  }

  // Fallback: plain text
  return <span className="leading-relaxed whitespace-pre-wrap">{text}</span>;
}

// ── Code block ─────────────────────────────────────────────────────────────────

function CodeBlock({ code, language }: { code: string; language: string | null }) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (Prism && ref.current) {
      Prism.highlightElement(ref.current);
    }
  }, [code]);

  const langClass = language === "python" ? "language-python" : "language-c";

  return (
    <div className="my-4 overflow-x-auto rounded-lg border border-gray-200 bg-gray-900">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
          {language ?? "code"}
        </span>
      </div>
      <pre className="p-4 overflow-x-auto text-sm">
        <code ref={ref} className={langClass}>
          {code}
        </code>
      </pre>
    </div>
  );
}

// ── Answer components ──────────────────────────────────────────────────────────

function MCQOptions({
  choices,
  selected,
  onChange,
}: {
  choices: string[];
  selected: number | null;
  onChange: (idx: number) => void;
}) {
  const labels = ["(A)", "(B)", "(C)", "(D)"];
  return (
    <div className="space-y-3 mt-4">
      {choices.map((choice, idx) => (
        <label
          key={idx}
          className={`flex items-start gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
            selected === idx
              ? "border-blue-500 bg-blue-50"
              : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
          }`}
        >
          <div className="flex-shrink-0 mt-0.5">
            <div
              className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                selected === idx
                  ? "border-blue-500 bg-blue-500"
                  : "border-gray-400"
              }`}
            >
              {selected === idx && (
                <div className="w-2 h-2 rounded-full bg-white" />
              )}
            </div>
          </div>
          <input
            type="radio"
            className="sr-only"
            checked={selected === idx}
            onChange={() => onChange(idx)}
          />
          <span className="flex gap-2 text-sm text-gray-800">
            <span className="font-medium text-gray-500 flex-shrink-0">{labels[idx]}</span>
            <MathText text={choice} />
          </span>
        </label>
      ))}
    </div>
  );
}

function MSQOptions({
  choices,
  selected,
  onChange,
}: {
  choices: string[];
  selected: number[];
  onChange: (indices: number[]) => void;
}) {
  const labels = ["(A)", "(B)", "(C)", "(D)"];

  const toggle = (idx: number) => {
    if (selected.includes(idx)) {
      onChange(selected.filter((i) => i !== idx));
    } else {
      onChange([...selected, idx].sort((a, b) => a - b));
    }
  };

  return (
    <div className="space-y-3 mt-4">
      <p className="text-xs text-purple-700 font-medium bg-purple-50 border border-purple-200 px-3 py-1.5 rounded-lg inline-block">
        Select one or more correct answers
      </p>
      {choices.map((choice, idx) => (
        <label
          key={idx}
          className={`flex items-start gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
            selected.includes(idx)
              ? "border-purple-500 bg-purple-50"
              : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
          }`}
        >
          <div className="flex-shrink-0 mt-0.5">
            <div
              className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                selected.includes(idx)
                  ? "border-purple-500 bg-purple-500"
                  : "border-gray-400"
              }`}
            >
              {selected.includes(idx) && (
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </div>
          <input
            type="checkbox"
            className="sr-only"
            checked={selected.includes(idx)}
            onChange={() => toggle(idx)}
          />
          <span className="flex gap-2 text-sm text-gray-800">
            <span className="font-medium text-gray-500 flex-shrink-0">{labels[idx]}</span>
            <MathText text={choice} />
          </span>
        </label>
      ))}
    </div>
  );
}

function NATInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="mt-4">
      <p className="text-xs text-orange-700 font-medium bg-orange-50 border border-orange-200 px-3 py-1.5 rounded-lg inline-block mb-3">
        Numerical Answer Type — enter a numeric value
      </p>
      <div className="flex items-center gap-3">
        <input
          type="number"
          step="any"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Enter your answer..."
          className="w-64 px-4 py-2.5 rounded-lg border-2 border-gray-300 text-sm font-mono
                     focus:border-orange-400 focus:ring-1 focus:ring-orange-400 focus:outline-none
                     placeholder-gray-400"
        />
        {value && (
          <span className="text-sm text-gray-500">
            Your answer: <strong className="text-gray-900">{value}</strong>
          </span>
        )}
      </div>
    </div>
  );
}

// ── Question palette ───────────────────────────────────────────────────────────

function QuestionPalette({
  questions,
  questionStatuses,
  currentQno,
  activeSection,
  onNavigate,
  onSectionChange,
  onSubmit,
  responses,
}: {
  questions: QuestionItem[];
  questionStatuses: Record<string, QuestionStatus>;
  currentQno: number;
  activeSection: "all" | QuestionSection;
  onNavigate: (qno: number) => void;
  onSectionChange: (section: "all" | QuestionSection) => void;
  onSubmit: () => void;
  responses: Record<string, AnyAnswer>;
}) {
  const gaQuestions = questions.filter((q) => q.section === "GA");
  const subjectQuestions = questions.filter((q) => q.section === "Subject");

  const filteredQuestions =
    activeSection === "GA"
      ? gaQuestions
      : activeSection === "Subject"
      ? subjectQuestions
      : questions;

  // Compute summary counts
  const counts = useMemo(() => {
    let answered = 0, notAnswered = 0, marked = 0, answeredMarked = 0, notVisited = 0;
    for (const q of questions) {
      const st = questionStatuses[q.id] ?? "not_visited";
      if (st === "answered") answered++;
      else if (st === "not_answered") notAnswered++;
      else if (st === "marked") marked++;
      else if (st === "answered_marked") answeredMarked++;
      else notVisited++;
    }
    return { answered, notAnswered, marked, answeredMarked, notVisited };
  }, [questions, questionStatuses]);

  return (
    <div className="w-64 flex-shrink-0 flex flex-col bg-white border-l border-gray-200 h-full">
      {/* Section tabs */}
      <div className="flex border-b border-gray-200 text-xs font-medium">
        {(["all", "GA", "Subject"] as const).map((sec) => (
          <button
            key={sec}
            onClick={() => onSectionChange(sec)}
            className={`flex-1 py-2 transition-colors ${
              activeSection === sec
                ? "border-b-2 border-blue-600 text-blue-700 bg-blue-50"
                : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            {sec === "all" ? "All" : sec === "GA" ? `GA (${gaQuestions.length})` : `Subject (${subjectQuestions.length})`}
          </button>
        ))}
      </div>

      {/* Summary legend */}
      <div className="px-3 py-3 border-b border-gray-100 space-y-1.5">
        {STATUS_LEGEND.map(({ status, label, bg }) => {
          const count =
            status === "answered" ? counts.answered
            : status === "not_answered" ? counts.notAnswered
            : status === "marked" ? counts.marked
            : status === "answered_marked" ? counts.answeredMarked
            : counts.notVisited;
          return (
            <div key={status} className="flex items-center gap-2 text-xs text-gray-700">
              <div className={`w-5 h-5 rounded flex-shrink-0 ${bg}`} />
              <span className="flex-1">{label}</span>
              <span className="font-semibold">{count}</span>
            </div>
          );
        })}
      </div>

      {/* Question grid */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="grid grid-cols-5 gap-1">
          {filteredQuestions.map((q) => {
            const status = questionStatuses[q.id] ?? "not_visited";
            const isCurrent = q.qno === currentQno;
            return (
              <button
                key={q.id}
                onClick={() => onNavigate(q.qno)}
                title={`Q${q.qno} — ${q.question_type} — ${q.marks}M — ${status.replace("_", " ")}`}
                className={`
                  w-10 h-10 rounded text-xs font-semibold transition-all
                  ${STATUS_BG[status]}
                  ${isCurrent ? "ring-2 ring-offset-1 ring-gray-800 scale-110" : ""}
                `}
              >
                {q.qno}
              </button>
            );
          })}
        </div>
      </div>

      {/* Submit button */}
      <div className="p-3 border-t border-gray-200">
        <button
          onClick={onSubmit}
          className="w-full bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors"
        >
          Submit Exam
        </button>
        <p className="text-xs text-gray-400 text-center mt-1.5">
          {counts.answered + counts.answeredMarked}/{questions.length} answered
        </p>
      </div>
    </div>
  );
}

// ── Main ExamScreen component ─────────────────────────────────────────────────

export default function ExamScreen() {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();

  // ── Data state ──────────────────────────────────────────────────────────────
  const [exam, setExam] = useState<ExamScreenData | null>(null);
  const [attempt, setAttempt] = useState<AttemptData | null>(null);
  const [loadingExam, setLoadingExam] = useState(true);
  const [loadingStart, setLoadingStart] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ── Answer / navigation state ───────────────────────────────────────────────
  const [currentQno, setCurrentQno] = useState(1);
  const [responses, setResponses] = useState<Record<string, AnyAnswer>>({});
  const [questionStatuses, setQuestionStatuses] = useState<Record<string, QuestionStatus>>({});
  const [activeSection, setActiveSection] = useState<"all" | QuestionSection>("all");
  const [showSubmitModal, setShowSubmitModal] = useState(false);

  // ── Timer state (Part 9) ───────────────────────────────────────────────────
  const [remainingSeconds, setRemainingSeconds] = useState<number>(0);
  const [violationCount, setViolationCount] = useState(0);

  // ── Auto-save refs (Part 9) ──────────────────────────────────────────────
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastSavedRef = useRef<{ responses: Record<string, AnyAnswer>; statuses: Record<string, QuestionStatus> } | null>(null);

  // ── Save attempt callback (Part 9) ──────────────────────────────────────
  const saveAttempt = useCallback(
    async (resp: Record<string, AnyAnswer>, statuses: Record<string, QuestionStatus>) => {
      if (!attempt?.attempt_id) return;
      // Skip if nothing changed
      if (
        lastSavedRef.current?.responses === resp &&
        lastSavedRef.current?.statuses === statuses
      )
        return;
      try {
        const payload: AttemptSaveRequest = { responses: resp, question_statuses: statuses };
        await api.put(`/attempts/${attempt.attempt_id}/save`, payload);
        lastSavedRef.current = { responses: resp, statuses };
      } catch {
        // Silent fail — auto-save should not interrupt the user
      }
    },
    [attempt?.attempt_id]
  );

  // ── Submit handlers (Part 10) ──────────────────────────────────────────
  const handleConfirmSubmit = useCallback(async () => {
    if (!attempt?.attempt_id) return;
    setShowSubmitModal(false);
    try {
      await api.post(`/attempts/${attempt.attempt_id}/submit`);
      navigate(`/result/${attempt.attempt_id}`);
    } catch (err: any) {
      toast.error("Submission failed. Please try again.");
    }
  }, [attempt?.attempt_id, navigate]);

  const handleAutoSubmit = useCallback(async () => {
    if (!attempt?.attempt_id) return;
    toast.error("Time's up! Submitting your exam...");
    try {
      await api.post(`/attempts/${attempt.attempt_id}/submit`);
      navigate(`/result/${attempt.attempt_id}`);
    } catch {
      // Fallback: navigate anyway so user sees result
      navigate(`/result/${attempt.attempt_id}`);
    }
  }, [attempt?.attempt_id, navigate]);

  // ── Load exam questions ─────────────────────────────────────────────────────
  useEffect(() => {
    if (!examId) return;
    const load = async () => {
      try {
        const { data } = await api.get<ExamScreenData>(`/exams/${examId}`);
        setExam(data);
      } catch (err: any) {
        const msg = err?.response?.data?.detail ?? "Failed to load exam questions.";
        setError(msg);
        toast.error(msg);
      } finally {
        setLoadingExam(false);
      }
    };
    load();
  }, [examId]);

  // ── Start / resume attempt ──────────────────────────────────────────────────
  useEffect(() => {
    if (!examId || loadingExam || error) return;
    const start = async () => {
      try {
        const { data } = await api.post<AttemptData>(`/exams/${examId}/start`, {});
        setAttempt(data);

        // Restore saved responses & statuses (resume)
        if (data.responses && Object.keys(data.responses).length > 0) {
          setResponses(data.responses as Record<string, AnyAnswer>);
        }
        if (data.question_statuses && Object.keys(data.question_statuses).length > 0) {
          setQuestionStatuses(data.question_statuses as Record<string, QuestionStatus>);
        }

        if (data.is_resume) {
          toast.success("Resuming your exam session.", { icon: "🔄" });
        }
      } catch (err: any) {
        const msg = err?.response?.data?.detail ?? "Failed to start exam attempt.";
        setError(msg);
        toast.error(msg);
      } finally {
        setLoadingStart(false);
      }
    };
    start();
  }, [examId, loadingExam, error]);

  // ── Server-authoritative timer (Part 9) ───────────────────────────────────
  useEffect(() => {
    if (!attempt?.start_time || !exam) return;

    const startMs = new Date(attempt.start_time).getTime();
    const durationMs = exam.duration_minutes * 60 * 1000;
    const endMs = startMs + durationMs;

    // Initialize remaining seconds
    const initial = Math.max(
      0,
      Math.ceil((endMs - Date.now()) / 1000)
    );
    setRemainingSeconds(initial);

    const tick = () => {
      const remaining = Math.max(
        0,
        Math.ceil((endMs - Date.now()) / 1000)
      );
      setRemainingSeconds(remaining);
      if (remaining === 0) {
        handleAutoSubmit();
      }
    };

    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [attempt?.start_time, exam?.duration_minutes, handleAutoSubmit]);

  // ── Debounced auto-save every 5 seconds (Part 9) ─────────────────────────
  useEffect(() => {
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    saveTimeoutRef.current = setTimeout(() => {
      saveAttempt(responses, questionStatuses);
    }, 5000);
    return () => {
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    };
  }, [responses, questionStatuses, saveAttempt]);

  // ── Derived values ──────────────────────────────────────────────────────────
  const questions = useMemo(
    () => [...(exam?.questions ?? [])].sort((a, b) => a.qno - b.qno),
    [exam?.questions]
  );

  const currentQuestion = useMemo(
    () => questions.find((q) => q.qno === currentQno) ?? null,
    [questions, currentQno]
  );

  const summaryForModal = useMemo(() => {
    let answered = 0, notAnswered = 0, notVisited = 0, marked = 0;
    for (const q of questions) {
      const st = questionStatuses[q.id] ?? "not_visited";
      if (st === "answered" || st === "answered_marked") answered++;
      else if (st === "not_answered") notAnswered++;
      else if (st === "marked") marked++;
      else notVisited++;
    }
    return { answered, notAnswered, notVisited, marked };
  }, [questions, questionStatuses]);

  useEffect(() => {
    if (questions.length === 0) return;
    if (questions.some((q) => q.qno === currentQno)) return;
    setCurrentQno(questions[0].qno);
  }, [questions, currentQno]);

  // ── Mark question as visited when navigating to it ─────────────────────────
  const markVisited = useCallback(
    (question: QuestionItem) => {
      setQuestionStatuses((prev) => {
        const current = prev[question.id] ?? "not_visited";
        if (current === "not_visited") {
          return { ...prev, [question.id]: "not_answered" };
        }
        return prev;
      });
    },
    []
  );

  // When currentQno changes, mark the new question as visited
  useEffect(() => {
    if (currentQuestion) markVisited(currentQuestion);
  }, [currentQno, currentQuestion, markVisited]);

  // ── Answer handlers ─────────────────────────────────────────────────────────

  const handleAnswerMCQ = useCallback(
    (idx: number) => {
      if (!currentQuestion) return;
      const qid = currentQuestion.id;
      const answer: MCQAnswer = { index: idx };
      setResponses((prev) => ({ ...prev, [qid]: answer }));
      setQuestionStatuses((prev) => {
        const current = prev[qid] ?? "not_visited";
        const next = current === "marked" || current === "answered_marked"
          ? "answered_marked"
          : "answered";
        return { ...prev, [qid]: next };
      });
    },
    [currentQuestion]
  );

  const handleAnswerMSQ = useCallback(
    (indices: number[]) => {
      if (!currentQuestion) return;
      const qid = currentQuestion.id;
      if (indices.length === 0) {
        // Treat as cleared
        setResponses((prev) => {
          const next = { ...prev };
          delete next[qid];
          return next;
        });
        setQuestionStatuses((prev) => {
          const current = prev[qid] ?? "not_answered";
          const next = current === "answered_marked" ? "marked" : "not_answered";
          return { ...prev, [qid]: next };
        });
      } else {
        const answer: MSQAnswer = { indices };
        setResponses((prev) => ({ ...prev, [qid]: answer }));
        setQuestionStatuses((prev) => {
          const current = prev[qid] ?? "not_visited";
          const next = current === "marked" || current === "answered_marked"
            ? "answered_marked"
            : "answered";
          return { ...prev, [qid]: next };
        });
      }
    },
    [currentQuestion]
  );

  const handleAnswerNAT = useCallback(
    (value: string) => {
      if (!currentQuestion) return;
      const qid = currentQuestion.id;
      if (value.trim() === "") {
        setResponses((prev) => {
          const next = { ...prev };
          delete next[qid];
          return next;
        });
        setQuestionStatuses((prev) => {
          const current = prev[qid] ?? "not_answered";
          const next = current === "answered_marked" ? "marked" : "not_answered";
          return { ...prev, [qid]: next };
        });
      } else {
        const answer: NATAnswer = { value };
        setResponses((prev) => ({ ...prev, [qid]: answer }));
        setQuestionStatuses((prev) => {
          const current = prev[qid] ?? "not_visited";
          const next = current === "marked" || current === "answered_marked"
            ? "answered_marked"
            : "answered";
          return { ...prev, [qid]: next };
        });
      }
    },
    [currentQuestion]
  );

  // ── Anti-cheat: log event helper (Part 9) ───────────────────────────────
  const logEvent = useCallback(
    async (eventType: string, detail?: string) => {
      if (!attempt?.attempt_id) return;
      setViolationCount((c) => c + 1);
      try {
        await api.post(`/attempts/${attempt.attempt_id}/event`, {
          event_type: eventType,
          detail: detail ?? null,
          timestamp: new Date().toISOString(),
        });
      } catch {
        // Silent — anti-cheat logging should not interrupt the user
      }
    },
    [attempt?.attempt_id]
  );

  // ── Anti-cheat: fullscreen request on mount (Part 9) ────────────────────
  useEffect(() => {
    const req = document.documentElement.requestFullscreen;
    if (req) {
      req.call(document.documentElement).catch(() => {
        // Fullscreen may be blocked by browser policy — silently ignore
      });
    }
  }, []);

  // ── Anti-cheat: right-click disable (Part 9) ────────────────────────────
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      e.preventDefault();
      logEvent("right_click");
    };
    document.addEventListener("contextmenu", handler);
    return () => document.removeEventListener("contextmenu", handler);
  }, [logEvent]);

  // ── Anti-cheat: Ctrl+C/V/A/X block (Part 9) ─────────────────────────────
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (!e.ctrlKey) return;
      const blocked = ["c", "v", "a", "x", "s", "p", "u"];
      if (blocked.includes(e.key.toLowerCase())) {
        e.preventDefault();
        const eventType =
          e.key.toLowerCase() === "c"
            ? "copy_attempted"
            : e.key.toLowerCase() === "v"
            ? "paste_attempted"
            : "shortcut_blocked";
        logEvent(eventType, e.key);
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [logEvent]);

  // ── Anti-cheat: visibility change (Part 9) ──────────────────────────────
  useEffect(() => {
    const handler = () => {
      if (document.hidden) logEvent("visibility_hidden");
    };
    document.addEventListener("visibilitychange", handler);
    return () => document.removeEventListener("visibilitychange", handler);
  }, [logEvent]);

  // ── Anti-cheat: window blur (Part 9) ─────────────────────────────────────
  useEffect(() => {
    const handler = () => logEvent("window_blur");
    window.addEventListener("blur", handler);
    return () => window.removeEventListener("blur", handler);
  }, [logEvent]);

  // ── Anti-cheat: beforeunload warning (Part 9) ────────────────────────────
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      logEvent("beforeunload");
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [logEvent]);

  // ── Navigation handlers ─────────────────────────────────────────────────────

  const handleNavigateTo = useCallback(
    (qno: number) => {
      setCurrentQno(qno);
    },
    []
  );

  const handlePrevious = useCallback(() => {
    if (currentQno > 1) {
      setCurrentQno((n) => n - 1);
    }
  }, [currentQno]);

  const handleSaveAndNext = useCallback(() => {
    const nextQno = currentQno + 1;
    if (nextQno <= questions.length) {
      setCurrentQno(nextQno);
    }
  }, [currentQno, questions.length]);

  const handleMarkForReview = useCallback(() => {
    if (!currentQuestion) return;
    const qid = currentQuestion.id;
    setQuestionStatuses((prev) => {
      const hasAnswer = !!responses[qid];
      const next: QuestionStatus = hasAnswer ? "answered_marked" : "marked";
      return { ...prev, [qid]: next };
    });
    // Navigate to next question
    const nextQno = currentQno + 1;
    if (nextQno <= questions.length) {
      setCurrentQno(nextQno);
    }
  }, [currentQuestion, responses, currentQno, questions.length]);

  const handleClearResponse = useCallback(() => {
    if (!currentQuestion) return;
    const qid = currentQuestion.id;
    setResponses((prev) => {
      const next = { ...prev };
      delete next[qid];
      return next;
    });
    setQuestionStatuses((prev) => {
      const current = prev[qid] ?? "not_answered";
      const next: QuestionStatus =
        current === "answered_marked" ? "marked" : "not_answered";
      return { ...prev, [qid]: next };
    });
  }, [currentQuestion]);

  // ── Submit ──────────────────────────────────────────────────────────────────

  const handleSubmit = useCallback(() => {
    setShowSubmitModal(true);
  }, []);

  // ── Loading / error states ──────────────────────────────────────────────────

  if (loadingExam || loadingStart) {
    return <LoadingSpinner fullScreen />;
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md p-8 bg-white rounded-xl border border-red-200">
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Cannot Start Exam</h2>
          <p className="text-sm text-red-600 mb-6">{error}</p>
          <button
            onClick={() => navigate("/dashboard")}
            className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!exam) {
    return <LoadingSpinner fullScreen />;
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md p-8 bg-white rounded-xl border border-amber-200">
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Exam Has No Questions</h2>
          <p className="text-sm text-amber-700 mb-6">
            The exam was created, but no renderable questions were returned to the exam screen.
          </p>
          <button
            onClick={() => navigate("/dashboard")}
            className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!currentQuestion) {
    return <LoadingSpinner fullScreen />;
  }

  // ── Current answer ──────────────────────────────────────────────────────────
  const currentAnswer = responses[currentQuestion.id];
  const mcqSelected =
    currentQuestion.question_type === "MCQ" && currentAnswer
      ? (currentAnswer as MCQAnswer).index
      : null;
  const msqSelected =
    currentQuestion.question_type === "MSQ" && currentAnswer
      ? (currentAnswer as MSQAnswer).indices ?? []
      : [];
  const natValue =
    currentQuestion.question_type === "NAT" && currentAnswer
      ? (currentAnswer as NATAnswer).value ?? ""
      : "";

  const currentStatus = questionStatuses[currentQuestion.id] ?? "not_visited";
  const isCurrentMarked =
    currentStatus === "marked" || currentStatus === "answered_marked";

  // ── Type badge ──────────────────────────────────────────────────────────────
  const typeBadgeClass =
    currentQuestion.question_type === "MCQ"
      ? "bg-blue-100 text-blue-700"
      : currentQuestion.question_type === "MSQ"
      ? "bg-purple-100 text-purple-700"
      : "bg-orange-100 text-orange-700";

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <ExamErrorBoundary>
    <div className="h-screen flex flex-col bg-gray-100 overflow-hidden">

      {/* ── Top bar ── */}
      <div className="flex-shrink-0 bg-blue-800 text-white px-4 py-2 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold">GATE 2026 Mock Test</span>
          <span className="text-blue-300">|</span>
          <span className="text-sm text-blue-200">
            Paper: <strong className="text-white">{exam.paper}</strong>
          </span>
          <span className="text-blue-300">|</span>
          <span className="text-sm text-blue-200">
            <strong className="text-white capitalize">{exam.difficulty}</strong> difficulty
          </span>
          <span className="text-blue-300">|</span>
          <span className="text-sm text-blue-200">
            <strong className="text-white">{exam.total_questions}</strong> Qs ·{" "}
            <strong className="text-white">{exam.total_marks}</strong> Marks
          </span>
        </div>

        {/* Timer + violations (Part 9) */}
        <div className="flex items-center gap-3">
          <div
            className={`px-3 py-1.5 rounded-lg text-sm font-mono font-bold tracking-wider ${
              remainingSeconds < 600
                ? "bg-red-600 text-red-100 animate-pulse"
                : "bg-blue-900 text-white"
            }`}
          >
            ⏱{" "}
            {String(Math.floor(remainingSeconds / 3600)).padStart(2, "0")}:
            {String(Math.floor((remainingSeconds % 3600) / 60)).padStart(2, "0")}:
            {String(remainingSeconds % 60).padStart(2, "0")}
          </div>

          {violationCount > 0 && (
            <div className="bg-red-600 px-2 py-1 rounded-lg text-xs font-bold text-white">
              ⚠ Violations: {violationCount}
            </div>
          )}

          <button
            onClick={() => navigate("/dashboard")}
            className="text-xs text-blue-300 hover:text-white transition-colors ml-1"
          >
            ✕ Exit
          </button>
        </div>
      </div>

      {/* ── Main body ── */}
      <div className="flex-1 flex overflow-hidden">

        {/* ── Left: Question display ── */}
        <div className="flex-1 flex flex-col overflow-hidden">

          {/* Question header */}
          <div className="flex-shrink-0 bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-3">
            <span className="text-sm font-bold text-gray-800">
              Question {currentQuestion.qno} of {questions.length}
            </span>
            <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${typeBadgeClass}`}>
              {currentQuestion.question_type}
            </span>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-gray-100 text-gray-700">
              {currentQuestion.marks} Mark{currentQuestion.marks > 1 ? "s" : ""}
            </span>
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700">
              {currentQuestion.section_name}
            </span>
            {currentQuestion.marks === 1 ? (
              <span className="text-xs text-red-600 ml-auto">
                Wrong answer: −{(1/3).toFixed(2)} marks
              </span>
            ) : currentQuestion.marks === 2 && currentQuestion.question_type === "MCQ" ? (
              <span className="text-xs text-red-600 ml-auto">
                Wrong answer: −{(2/3).toFixed(2)} marks
              </span>
            ) : (
              <span className="text-xs text-green-700 ml-auto">
                No negative marking
              </span>
            )}
          </div>

          {/* Question content (scrollable) */}
          <div className="flex-1 overflow-y-auto px-6 py-5">
            {/* Stem */}
            <div className="text-base text-gray-900 leading-relaxed">
              <MathText text={currentQuestion.stem_tex} />
            </div>

            {/* Code snippet */}
            {currentQuestion.code_snippet && (
              <CodeBlock
                code={currentQuestion.code_snippet}
                language={currentQuestion.code_language}
              />
            )}

            {/* Answer section */}
            <div className="mt-6">
              {currentQuestion.question_type === "MCQ" && currentQuestion.choices && (
                <MCQOptions
                  choices={currentQuestion.choices}
                  selected={mcqSelected}
                  onChange={handleAnswerMCQ}
                />
              )}

              {currentQuestion.question_type === "MSQ" && currentQuestion.choices && (
                <MSQOptions
                  choices={currentQuestion.choices}
                  selected={msqSelected}
                  onChange={handleAnswerMSQ}
                />
              )}

              {currentQuestion.question_type === "NAT" && (
                <NATInput value={natValue} onChange={handleAnswerNAT} />
              )}
            </div>
          </div>

          {/* ── Navigation bar ── */}
          <div className="flex-shrink-0 bg-white border-t border-gray-200 px-6 py-3 flex items-center gap-3">
            {/* Previous */}
            <button
              onClick={handlePrevious}
              disabled={currentQno === 1}
              className="px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700
                         hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              ← Previous
            </button>

            <div className="flex-1" />

            {/* Clear Response */}
            <button
              onClick={handleClearResponse}
              disabled={!responses[currentQuestion.id]}
              className="px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700
                         hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Clear Response
            </button>

            {/* Mark for Review & Next */}
            <button
              onClick={handleMarkForReview}
              className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                isCurrentMarked
                  ? "border-purple-400 bg-purple-50 text-purple-700 hover:bg-purple-100"
                  : "border-purple-300 text-purple-700 hover:bg-purple-50"
              }`}
            >
              {isCurrentMarked ? "✓ Marked" : "Mark for Review"} & Next
            </button>

            {/* Save & Next */}
            <button
              onClick={handleSaveAndNext}
              className="px-5 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold
                         hover:bg-blue-700 transition-colors"
            >
              {currentQno === questions.length ? "Save" : "Save & Next →"}
            </button>
          </div>
        </div>

        {/* ── Right: Question Palette ── */}
        <QuestionPalette
          questions={questions}
          questionStatuses={questionStatuses}
          currentQno={currentQno}
          activeSection={activeSection}
          onNavigate={handleNavigateTo}
          onSectionChange={setActiveSection}
          onSubmit={handleSubmit}
          responses={responses}
        />
      </div>

      {/* ── Submit confirmation modal ── */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold text-gray-900 mb-2">Submit Exam?</h2>
            <p className="text-sm text-gray-500 mb-6">
              Please review your attempt summary before submitting.
            </p>

            <div className="grid grid-cols-2 gap-3 mb-6">
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-green-700">{summaryForModal.answered}</p>
                <p className="text-xs text-green-600 mt-0.5">Answered</p>
              </div>
              <div className="bg-red-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-red-700">{summaryForModal.notAnswered}</p>
                <p className="text-xs text-red-600 mt-0.5">Not Answered</p>
              </div>
              <div className="bg-purple-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-purple-700">{summaryForModal.marked}</p>
                <p className="text-xs text-purple-600 mt-0.5">Marked for Review</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-gray-700">{summaryForModal.notVisited}</p>
                <p className="text-xs text-gray-500 mt-0.5">Not Visited</p>
              </div>
            </div>

            <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 px-3 py-2 rounded-lg mb-6">
              ⚠️ Once submitted, you cannot change your answers. Marked-for-review
              questions will also be evaluated.
            </p>

            <div className="flex gap-3">
              <button
                onClick={() => setShowSubmitModal(false)}
                className="flex-1 py-2.5 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel — Keep Attempting
              </button>
              <button
                onClick={handleConfirmSubmit}
                className="flex-1 py-2.5 rounded-lg bg-red-600 text-white text-sm font-semibold hover:bg-red-700 transition-colors"
              >
                Yes, Submit Now
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    </ExamErrorBoundary>
  );
}
