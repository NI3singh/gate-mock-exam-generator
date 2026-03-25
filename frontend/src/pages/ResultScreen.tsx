/**
 * ResultScreen — Part 10 & 11
 *
 * Part 10: Score hero, section/type breakdown, topic analysis, anti-cheat badge.
 * Part 11: GET /attempts/{id} (page refresh works), negative marks deducted,
 *   anti-cheat per-event breakdown, topic accuracy %, View Solutions,
 *   Download PDF button.
 */

import { useEffect, useState } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";

import api from "../services/api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import type { AttemptDetailResponse, SolutionItem } from "../types";

/* ── Violations badge component ─────────────────────────────────────────── */

function ViolationBadge({ violations }: { violations: { event_type: string; count: number }[] }) {
  if (!violations.length) return null;
  const labels: Record<string, string> = {
    visibility_hidden: "Tab switches",
    fullscreen_exit:    "Fullscreen exits",
    right_click:        "Right-click attempts",
    copy_attempted:     "Copy blocked",
    paste_attempted:    "Paste blocked",
    shortcut_blocked:   "Shortcuts blocked",
    window_blur:        "Window blur",
    beforeunload:      "beforeunload",
  };
  return (
    <div className="bg-white rounded-2xl shadow-md p-6">
      <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-4">
        Anti-Cheat Violations
      </h2>
      <div className="space-y-2">
        {violations.map(({ event_type, count }) => (
          <div key={event_type} className="flex items-center justify-between text-sm">
            <span className="text-red-600 font-medium">
              ⚠ {labels[event_type] ?? event_type}
            </span>
            <span className="bg-red-100 text-red-700 font-bold px-3 py-0.5 rounded-full text-xs">
              {count}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Solution review modal ──────────────────────────────────────────────── */

function SolutionModal({
  solutions,
  onClose,
}: {
  solutions: SolutionItem[];
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/60 flex items-start justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl my-8 max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between px-8 py-5 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Solution Review</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 text-2xl leading-none"
          >
            ×
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-8 py-5 space-y-6">
          {solutions.map((sol) => (
            <div
              key={sol.qno}
              className={`rounded-xl border-2 p-5 ${
                sol.is_correct
                  ? "border-green-300 bg-green-50"
                  : sol.user_answer === null
                  ? "border-gray-300 bg-gray-50"
                  : "border-red-300 bg-red-50"
              }`}
            >
              <div className="flex items-center gap-3 mb-3 flex-wrap">
                <span className="font-bold text-gray-800">Q{sol.qno}</span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                  sol.question_type === "MCQ"
                    ? "bg-blue-100 text-blue-700"
                    : sol.question_type === "MSQ"
                    ? "bg-purple-100 text-purple-700"
                    : "bg-orange-100 text-orange-700"
                }`}>
                  {sol.question_type}
                </span>
                <span className="text-xs text-gray-500">{sol.marks} mark{sol.marks > 1 ? "s" : ""}</span>
                <span className="text-xs text-gray-500">{sol.section_name} · {sol.topic}</span>
                <span className={`ml-auto text-sm font-bold ${
                  sol.is_correct ? "text-green-600" : sol.user_answer === null ? "text-gray-500" : "text-red-600"
                }`}>
                  {sol.is_correct ? "✓ Correct" : sol.user_answer === null ? "— Unanswered" : "✗ Wrong"}
                </span>
              </div>
              {/* Question */}
              <p className="text-sm text-gray-800 mb-3 font-medium">{sol.stem_tex}</p>
              {/* Choices */}
              {sol.choices && sol.choices.length > 0 && (
                <div className="space-y-1.5 mb-3">
                  {sol.choices.map((choice, idx) => {
                    const isCorrectChoice = sol.correct_answer &&
                      (sol.question_type === "MCQ"
                        ? (sol.correct_answer as { index: number }).index === idx
                        : (sol.correct_answer as { indices: number[] }).indices.includes(idx));
                    const isUserChoice = sol.user_answer &&
                      (sol.question_type === "MCQ"
                        ? (sol.user_answer as { index: number }).index === idx
                        : (sol.user_answer as { indices: number[] }).indices.includes(idx));
                    return (
                      <div
                        key={idx}
                        className={`text-sm px-3 py-2 rounded-lg border flex items-center gap-2 ${
                          isCorrectChoice
                            ? "bg-green-100 border-green-400 text-green-800"
                            : isUserChoice && !isCorrectChoice
                            ? "bg-red-100 border-red-400 text-red-800"
                            : "bg-gray-50 border-gray-200 text-gray-600"
                        }`}
                      >
                        <span className="font-medium">{String.fromCharCode(65 + idx)}.</span>
                        <span>{choice}</span>
                        {isCorrectChoice && <span className="ml-auto text-green-600 font-bold">✓ Correct</span>}
                        {isUserChoice && !isCorrectChoice && <span className="ml-auto text-red-600 font-bold">Your answer</span>}
                      </div>
                    );
                  })}
                </div>
              )}
              {/* User NAT answer */}
              {sol.question_type === "NAT" && sol.user_answer && (
                <div className="text-sm mb-2 px-3 py-2 bg-red-100 border border-red-300 rounded-lg text-red-800">
                  Your answer: <strong>{String((sol.user_answer as unknown as { value: string }).value)}</strong>
                </div>
              )}
              {/* Correct answer */}
              {sol.question_type === "NAT" && (
                <div className="text-sm mb-3 px-3 py-2 bg-green-100 border border-green-300 rounded-lg text-green-800">
                  Correct answer: <strong>{String((sol.correct_answer as unknown as { value: number }).value)}</strong>
                  {(sol.correct_answer as unknown as { tolerance?: number }).tolerance !== undefined &&
                    ` (±${(sol.correct_answer as unknown as { value: number; tolerance: number }).tolerance})`}
                </div>
              )}
              {/* Solution */}
              {sol.solution_tex && (
                <div className="mt-3 text-sm text-gray-700 italic bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
                  💡 Solution: {sol.solution_tex}
                </div>
              )}
              {/* Score */}
              <div className="mt-3 text-right text-sm font-semibold text-gray-600">
                Score: <span className={sol.score >= 0 ? "text-green-600" : "text-red-600"}>
                  {sol.score >= 0 ? "+" : ""}{sol.score.toFixed(2)}
                </span>
              </div>
            </div>
          ))}
        </div>
        <div className="px-8 py-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full py-2.5 rounded-xl bg-gray-200 text-gray-700 font-semibold hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Main ResultScreen ─────────────────────────────────────────────────── */

export default function ResultScreen() {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [result, setResult] = useState<AttemptDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSolutions, setShowSolutions] = useState(searchParams.get("solutions") === "1");

  useEffect(() => {
    if (!attemptId) return;
    const load = async () => {
      try {
        const { data } = await api.get<AttemptDetailResponse>(
          `/attempts/${attemptId}`
        );
        setResult(data);
      } catch (err: any) {
        const msg = err?.response?.data?.detail ?? "Failed to load result.";
        setError(msg);
        toast.error(msg);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [attemptId]);

  const handleDownloadPdf = async () => {
    if (!attemptId) return;
    try {
      const response = await api.get(`/attempts/${attemptId}/pdf`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `GATE2026_Result_${attemptId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch {
      toast.error("PDF download failed. Make sure weasyprint is installed on the backend.");
    }
  };

  if (loading) return <LoadingSpinner fullScreen />;

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md p-8 bg-white rounded-xl border border-red-200">
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Could Not Load Result</h2>
          <p className="text-sm text-red-600 mb-6">{error ?? "Unknown error"}</p>
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

  const percentage = Math.round((result.score / result.max_score) * 100);
  const scoreColor =
    percentage >= 75 ? "text-green-600"
    : percentage >= 50 ? "text-yellow-600"
    : "text-red-600";

  const sectionBreakdown = result.section_scores ?? {};
  const typeBreakdown = result.score_breakdown?.type ?? {};

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      {/* Solutions modal */}
      {showSolutions && result.solutions && (
        <SolutionModal
          solutions={result.solutions}
          onClose={() => setShowSolutions(false)}
        />
      )}

      <div className="max-w-3xl mx-auto space-y-6">

        {/* ── Score Hero ── */}
        <div className="bg-white rounded-2xl shadow-md p-8 text-center">
          <h1 className="text-sm font-semibold uppercase tracking-widest text-gray-500 mb-2">
            Your Score
          </h1>
          <div className={`text-7xl font-black mb-1 ${scoreColor}`}>
            {result.score.toFixed(2)}
            <span className="text-3xl text-gray-400">/{result.max_score}</span>
          </div>
          <div className="text-xl font-bold text-gray-700 mb-1">{percentage}% Overall</div>
          <div className="inline-flex items-center gap-2 text-sm text-gray-500">
            <span
              className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                percentage >= 75 ? "bg-green-100 text-green-700"
                : percentage >= 50 ? "bg-yellow-100 text-yellow-700"
                : "bg-red-100 text-red-700"
              }`}
            >
              {percentage >= 75 ? "Excellent" : percentage >= 50 ? "Good" : "Needs Improvement"}
            </span>
            <span>
              {result.total_correct} correct · {result.total_wrong} wrong ·{" "}
              {result.total_unanswered} unanswered
            </span>
          </div>
          {/* Negative marks */}
          {result.negative_marks > 0 && (
            <div className="mt-3 text-red-600 font-semibold text-sm">
              −{result.negative_marks.toFixed(2)} marks deducted (negative marking on MCQs)
            </div>
          )}
        </div>

        {/* ── Exam Info ── */}
        <div className="bg-white rounded-2xl shadow-md p-6">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-4">
            Exam Details
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Paper",        value: result.paper },
              { label: "Difficulty",   value: result.difficulty },
              { label: "Duration",      value: `${result.duration_minutes} min` },
              { label: "Questions",    value: `${result.total_questions}` },
            ].map(({ label, value }) => (
              <div key={label} className="bg-gray-50 rounded-xl p-4 text-center">
                <p className="text-xs text-gray-500 mb-1">{label}</p>
                <p className="text-lg font-bold text-gray-900 capitalize">{value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── Section + Violations side by side ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Section Breakdown */}
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-4">
              Section Breakdown
            </h2>
            <div className="space-y-4">
              {(["GA", "Subject"] as const).map((section) => {
                const data = sectionBreakdown[section];
                if (!data) return null;
                const pct = data.max_score
                  ? Math.round((data.score / data.max_score) * 100)
                  : 0;
                return (
                  <div key={section}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-semibold text-gray-700">
                        {section === "GA" ? "General Aptitude" : "Subject"}
                      </span>
                      <span className="text-gray-600">
                        {data.score.toFixed(1)}/{data.max_score} ({pct}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all ${
                          pct >= 75 ? "bg-green-500" : pct >= 50 ? "bg-yellow-400" : "bg-red-500"
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <div className="flex gap-4 mt-1 text-xs text-gray-500">
                      <span>✓ {data.correct} correct</span>
                      <span>✗ {data.wrong} wrong</span>
                      <span>— {data.unanswered} unanswered</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Violations */}
          <ViolationBadge violations={result.violations} />
        </div>

        {/* ── Type Breakdown ── */}
        <div className="bg-white rounded-2xl shadow-md p-6">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-4">
            Question Type Breakdown
          </h2>
          <div className="grid grid-cols-3 gap-4">
            {(["MCQ", "MSQ", "NAT"] as const).map((qtype) => {
              const data = typeBreakdown[qtype];
              if (!data) return null;
              const total = data.correct + data.wrong + data.unanswered;
              const pct = total ? Math.round((data.correct / total) * 100) : 0;
              return (
                <div key={qtype} className="bg-gray-50 rounded-xl p-4 text-center">
                  <p className="text-xs font-semibold text-gray-500 mb-2 uppercase">{qtype}</p>
                  <p className="text-2xl font-black text-gray-900">{data.score.toFixed(1)}</p>
                  <p className="text-xs text-gray-400 mb-3">{pct}% accuracy</p>
                  <div className="flex justify-center gap-3 text-xs text-gray-600">
                    <span className="text-green-600">✓{data.correct}</span>
                    <span className="text-red-600">✗{data.wrong}</span>
                    <span className="text-gray-400">—{data.unanswered}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ── Topic Analysis with Accuracy % ── */}
        {result.topic_analysis && result.topic_analysis.length > 0 && (
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-4">
              Topic Analysis
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Topic</th>
                    <th className="text-center py-2 px-2 font-semibold text-gray-700">Total</th>
                    <th className="text-center py-2 px-2 font-semibold text-green-600">✓</th>
                    <th className="text-center py-2 px-2 font-semibold text-red-600">✗</th>
                    <th className="text-center py-2 px-2 font-semibold text-gray-500">—</th>
                    <th className="text-center py-2 px-2 font-semibold text-gray-700">Accuracy</th>
                    <th className="text-center py-2 px-2 font-semibold text-gray-700">Score</th>
                  </tr>
                </thead>
                <tbody>
                  {result.topic_analysis.map((item, i) => {
                    const accuracy = item.total
                      ? Math.round((item.correct / item.total) * 100)
                      : 0;
                    const accColor =
                      accuracy >= 75 ? "text-green-600"
                      : accuracy >= 50 ? "text-yellow-600"
                      : "text-red-600";
                    return (
                      <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-2 px-2">
                          <span className="font-medium text-gray-800">{item.topic}</span>
                          <span className="text-xs text-gray-400 ml-1">({item.section_name})</span>
                        </td>
                        <td className="text-center py-2 px-2 text-gray-600">{item.total}</td>
                        <td className="text-center py-2 px-2 text-green-600 font-semibold">{item.correct}</td>
                        <td className="text-center py-2 px-2 text-red-600 font-semibold">{item.wrong}</td>
                        <td className="text-center py-2 px-2 text-gray-400">{item.unanswered}</td>
                        <td className={`text-center py-2 px-2 font-bold ${accColor}`}>{accuracy}%</td>
                        <td className="text-center py-2 px-2 font-semibold text-gray-800">
                          {item.score.toFixed(1)}/{item.max_score}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ── Actions ── */}
        <div className="flex gap-4 justify-center flex-wrap">
          <button
            onClick={() => navigate("/dashboard")}
            className="px-8 py-3 rounded-xl bg-blue-700 text-white font-semibold hover:bg-blue-800 transition-colors"
          >
            Back to Dashboard
          </button>
          {result.solutions && result.solutions.length > 0 && (
            <button
              onClick={() => setShowSolutions(true)}
              className="px-8 py-3 rounded-xl bg-purple-600 text-white font-semibold hover:bg-purple-700 transition-colors"
            >
              View Solutions ({result.solutions.length})
            </button>
          )}
          <button
            onClick={handleDownloadPdf}
            className="px-8 py-3 rounded-xl border-2 border-gray-300 text-gray-700 font-semibold hover:bg-gray-100 transition-colors"
          >
            Download PDF
          </button>
        </div>
      </div>
    </div>
  );
}
