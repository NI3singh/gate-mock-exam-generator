import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";

import api from "../services/api";
import Navbar from "../components/layout/Navbar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ProgressBar from "../components/common/ProgressBar";

/* ── Types ── */
interface ProgressData {
  total: number;
  completed: number;
  failed: number;
  batch?: string | null;
  error?: string | null;
}

interface StatusResponse {
  exam_id: string;
  status: string;
  progress: ProgressData;
}

type Phase =
  | "polling"      // Generation in progress
  | "completed"    // Successfully generated
  | "failed"       // Generation failed
  | "not_found";   // Exam ID invalid

/* ── Constants ── */
const POLL_INTERVAL_MS = 3000;
const ESTIMATED_SECONDS_PER_QUESTION = 5; // rough estimate

export default function ExamProgress() {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();

  const [phase, setPhase] = useState<Phase>("polling");
  const [progress, setProgress] = useState<ProgressData>({
    total: 65,
    completed: 0,
    failed: 0,
  });
  const [startTime] = useState(() => Date.now());
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  /* ── Poll for status ── */
  const pollStatus = useCallback(async () => {
    if (!examId) return;

    try {
      const { data } = await api.get<StatusResponse>(
        `/exams/${examId}/status`,
        { suppressErrorToast: true }
      );

      setProgress(data.progress);

      if (data.status === "generated") {
        setPhase("completed");
        // Stop polling
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } else if (data.progress.error) {
        setPhase("failed");
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setPhase("not_found");
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
      // Other errors: keep polling (transient network issues)
    }
  }, [examId]);

  /* ── Start polling on mount ── */
  useEffect(() => {
    // Initial poll immediately
    pollStatus();

    // Then poll every 3 seconds
    intervalRef.current = setInterval(pollStatus, POLL_INTERVAL_MS);

    // Elapsed time ticker
    timerRef.current = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [pollStatus, startTime]);

  /* ── Stop timer when generation completes ── */
  useEffect(() => {
    if (phase === "completed" || phase === "failed" || phase === "not_found") {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }, [phase]);

  /* ── Derived values ── */
  const pct =
    progress.total > 0
      ? Math.round((progress.completed / progress.total) * 100)
      : 0;

  const remaining =
    progress.completed > 0
      ? Math.max(
          0,
          Math.round(
            ((progress.total - progress.completed) /
              progress.completed) *
              elapsedSeconds
          )
        )
      : progress.total * ESTIMATED_SECONDS_PER_QUESTION;

  const formatTime = (secs: number): string => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  };

  const handleStartExam = () => {
    toast.success("Navigating to exam...");
    navigate(`/exam/${examId}`);
  };

  /* ── Render ── */
  return (
    <div className="min-h-screen">
      <Navbar />

      <main className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
        {/* ── POLLING: Generation in progress ── */}
        {phase === "polling" && (
          <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
            {/* Header */}
            <div className="text-center">
              <div className="mx-auto flex justify-center">
                <LoadingSpinner size="lg" text="GENERATING QUESTIONS" />
              </div>
              <h1 className="mt-6 text-2xl font-bold text-gray-900">
                Generating Your Exam
              </h1>
              <p className="mt-2 text-sm text-gray-500">
                AI is crafting original GATE-style questions. This usually takes
                3–7 minutes.
              </p>
            </div>

            {/* Progress bar */}
            <div className="mt-8">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700">
                  Generating questions...
                </span>
                <span className="font-semibold text-blue-600">
                  {progress.completed}/{progress.total}
                </span>
              </div>
              <ProgressBar value={pct} color="blue" size="lg" animate />
              <div className="mt-2 text-right text-xs text-gray-400">
                {pct}% complete
              </div>
            </div>

            {/* Stats row */}
            <div className="mt-6 grid grid-cols-3 gap-4">
              <div className="rounded-lg bg-gray-50 p-3 text-center">
                <p className="text-xs text-gray-500">Elapsed</p>
                <p className="mt-1 text-sm font-semibold text-gray-900">
                  {formatTime(elapsedSeconds)}
                </p>
              </div>
              <div className="rounded-lg bg-gray-50 p-3 text-center">
                <p className="text-xs text-gray-500">Est. Remaining</p>
                <p className="mt-1 text-sm font-semibold text-gray-900">
                  {progress.completed > 0
                    ? `~${formatTime(remaining)}`
                    : "Calculating..."}
                </p>
              </div>
              <div className="rounded-lg bg-gray-50 p-3 text-center">
                <p className="text-xs text-gray-500">Batch</p>
                <p className="mt-1 text-sm font-semibold text-gray-900">
                  {progress.batch || "—"}
                </p>
              </div>
            </div>

            {/* Failed questions warning */}
            {progress.failed > 0 && (
              <div className="mt-4 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">
                <span className="font-medium">Note:</span>{" "}
                {progress.failed} question(s) failed validation and will be
                retried or skipped. This is normal.
              </div>
            )}

            {/* Live steps */}
            <div className="mt-6 space-y-2">
              <Step
                done={progress.completed > 0}
                active={progress.completed === 0}
                label="Initializing question generation pipeline"
              />
              <Step
                done={progress.completed >= 10}
                active={progress.completed > 0 && progress.completed < 10}
                label="Generating General Aptitude questions (10)"
              />
              <Step
                done={progress.completed >= progress.total}
                active={progress.completed >= 10 && progress.completed < progress.total}
                label={`Generating Subject questions (${Math.max(0, progress.completed - 10)}/55)`}
              />
              <Step
                done={false}
                active={false}
                label="Assembling final exam paper"
              />
            </div>

            {/* Exam ID */}
            <div className="mt-6 rounded-lg bg-gray-50 p-3 text-center">
              <p className="text-xs text-gray-400">
                Exam ID:{" "}
                <code className="rounded bg-gray-200 px-1.5 py-0.5 text-gray-600">
                  {examId}
                </code>
              </p>
            </div>
          </div>
        )}

        {/* ── COMPLETED: Generation successful ── */}
        {phase === "completed" && (
          <div className="rounded-xl border border-green-200 bg-white p-8 shadow-sm">
            <div className="text-center">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-50">
                <svg
                  className="h-10 w-10 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h1 className="mt-6 text-2xl font-bold text-gray-900">
                Exam Ready! 🎉
              </h1>
              <p className="mt-2 text-gray-500">
                Your GATE mock test has been generated successfully.
              </p>
            </div>

            {/* Summary */}
            <div className="mt-6">
              <ProgressBar value={100} color="green" size="lg" animate={false} />
            </div>

            <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
              <SummaryCard label="Questions" value={String(progress.completed)} />
              <SummaryCard label="Total Marks" value="100" />
              <SummaryCard label="Duration" value="3 hours" />
              <SummaryCard
                label="Generated In"
                value={formatTime(elapsedSeconds)}
              />
            </div>

            {progress.failed > 0 && (
              <div className="mt-4 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">
                <span className="font-medium">Note:</span>{" "}
                {progress.failed} question(s) failed validation and were
                skipped. Your exam may have slightly fewer questions.
              </div>
            )}

            {/* Actions */}
            <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
              <button
                onClick={handleStartExam}
                className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-8 py-3.5 text-base font-semibold text-white shadow-sm hover:bg-blue-700 sm:w-auto"
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Start Exam
              </button>

              <Link
                to="/dashboard"
                className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-6 py-3.5 text-sm font-medium text-gray-700 hover:bg-gray-50 sm:w-auto"
              >
                Save for Later
              </Link>
            </div>

            <p className="mt-4 text-center text-xs text-gray-400">
              You can also start this exam later from your Dashboard.
            </p>
          </div>
        )}

        {/* ── FAILED: Generation error ── */}
        {phase === "failed" && (
          <div className="rounded-xl border border-red-200 bg-white p-8 shadow-sm">
            <div className="text-center">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-50">
                <svg
                  className="h-10 w-10 text-red-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
              </div>
              <h1 className="mt-6 text-2xl font-bold text-gray-900">
                Generation Failed
              </h1>
              <p className="mt-2 text-gray-500">
                Something went wrong while generating your exam.
              </p>
            </div>

            {/* Error detail */}
            {progress.error && (
              <div className="mt-6 rounded-lg bg-red-50 p-4">
                <p className="text-sm font-medium text-red-800">Error details:</p>
                <p className="mt-1 text-sm text-red-600">{progress.error}</p>
              </div>
            )}

            {/* Partial progress */}
            {progress.completed > 0 && (
              <div className="mt-4">
                <p className="mb-2 text-sm text-gray-500">
                  Progress before failure:
                </p>
                <ProgressBar
                  value={Math.round(
                    (progress.completed / progress.total) * 100
                  )}
                  color="red"
                  size="md"
                  animate={false}
                />
                <p className="mt-1 text-xs text-gray-400">
                  {progress.completed}/{progress.total} questions generated
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
              <Link
                to="/generate-exam"
                className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 sm:w-auto"
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Try Again
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex w-full items-center justify-center rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 sm:w-auto"
              >
                Back to Dashboard
              </Link>
            </div>
          </div>
        )}

        {/* ── NOT FOUND ── */}
        {phase === "not_found" && (
          <div className="rounded-xl border border-gray-200 bg-white p-8 text-center shadow-sm">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
              <span className="text-3xl">🔍</span>
            </div>
            <h1 className="mt-6 text-2xl font-bold text-gray-900">
              Exam Not Found
            </h1>
            <p className="mt-2 text-gray-500">
              The exam ID <code className="rounded bg-gray-100 px-1.5 py-0.5 text-sm text-gray-600">{examId}</code>{" "}
              doesn't exist or doesn't belong to your account.
            </p>
            <Link
              to="/dashboard"
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700"
            >
              Back to Dashboard
            </Link>
          </div>
        )}

        {/* ── Tips (shown during polling) ── */}
        {phase === "polling" && (
          <div className="mt-8 rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-700">
              💡 While you wait...
            </h3>
            <ul className="mt-3 space-y-2 text-sm text-gray-500">
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-blue-500">•</span>
                Each question is uniquely generated by AI — no two exams are alike.
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-blue-500">•</span>
                Questions go through validation to ensure correctness.
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-blue-500">•</span>
                The exam follows the official GATE 2027 pattern: 65 Qs, 100 marks, 3 hours.
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-blue-500">•</span>
                MCQs have negative marking (−⅓ or −⅔). MSQ and NAT have no negative marking.
              </li>
            </ul>
          </div>
        )}
      </main>
    </div>
  );
}

/* ── Sub-components ── */

function Step({
  done,
  active,
  label,
}: {
  done: boolean;
  active: boolean;
  label: string;
}) {
  return (
    <div className="flex items-center gap-3">
      {done ? (
        <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-green-100">
          <svg
            className="h-4 w-4 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
      ) : active ? (
        <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-blue-100">
          <div className="h-3 w-3 animate-spin rounded-full border-2 border-blue-300 border-t-blue-600" />
        </div>
      ) : (
        <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-gray-100">
          <div className="h-2 w-2 rounded-full bg-gray-300" />
        </div>
      )}
      <span
        className={`text-sm ${
          done
            ? "text-green-700"
            : active
              ? "font-medium text-blue-700"
              : "text-gray-400"
        }`}
      >
        {label}
      </span>
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-green-50 p-3 text-center">
      <p className="text-xs text-green-600">{label}</p>
      <p className="mt-1 text-sm font-bold text-green-800">{value}</p>
    </div>
  );
}
