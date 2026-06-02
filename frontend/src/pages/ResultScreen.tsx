/**
 * ResultScreen — Part 10 & 11
 *
 * Part 10: Score hero, section/type breakdown, topic analysis, anti-cheat badge.
 * Part 11: GET /attempts/{id} (page refresh works), negative marks deducted,
 *   anti-cheat per-event breakdown, topic accuracy %, View Solutions route,
 *   Download PDF button.
 */

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import api, { getApiErrorMessage } from "../services/api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import type { AttemptDetailResponse } from "../types";

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

/* ── Main ResultScreen ─────────────────────────────────────────────────── */

export default function ResultScreen() {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [result, setResult] = useState<AttemptDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!attemptId) return;
    const load = async () => {
      try {
        const { data } = await api.get<AttemptDetailResponse>(
          `/attempts/${attemptId}`
        );
        setResult(data);
      } catch (err: any) {
        const msg = getApiErrorMessage(err, "Failed to load result.");
        setError(msg);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [attemptId]);

  const handleDownloadPdf = async () => {
    if (!attemptId) return;
    try {
      setDownloadingPdf(true);
      const response = await api.get(`/attempts/${attemptId}/solutions-pdf`, {
        responseType: "blob",
        suppressErrorToast: true,
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `GATE2027_Solution_Key_${attemptId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      let message = getApiErrorMessage(
        err,
        "PDF download failed. Make sure the backend can reach LaTeX.online."
      );
      const data = err?.response?.data;

      if (data instanceof Blob) {
        try {
          const text = await data.text();
          const parsed = JSON.parse(text);
          if (parsed?.detail) {
            message = parsed.detail;
          }
        } catch {
          // Keep the generic fallback when the error body is not JSON.
        }
      } else if (data?.detail) {
        message = data.detail;
      }

      toast.error(message.length > 240 ? `${message.slice(0, 237)}...` : message);
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="xl" text="LOADING RESULT" fullPage />;
  }

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

  const percentage =
    result.max_score > 0
      ? Math.round((result.score / result.max_score) * 100)
      : 0;
  const scoreColor =
    percentage >= 75 ? "text-green-600"
    : percentage >= 50 ? "text-yellow-600"
    : "text-red-600";

  const sectionBreakdown = result.section_scores ?? {};
  const typeBreakdown = result.score_breakdown?.type ?? {};

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      {downloadingPdf && (
        <LoadingSpinner size="xl" text="BUILDING SOLUTIONS PDF" fullPage />
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
            className="px-8 py-3 rounded-xl bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-colors"
          >
            Back to Dashboard
          </button>
          {result.solutions && result.solutions.length > 0 && (
            <button
              onClick={() => navigate(`/result/${attemptId}/solutions`)}
              className="px-8 py-3 rounded-xl bg-purple-600 text-white font-semibold hover:bg-purple-700 transition-colors"
            >
              View Solutions ({result.solutions.length})
            </button>
          )}
          <button
            onClick={handleDownloadPdf}
            disabled={downloadingPdf}
            className="px-8 py-3 rounded-xl border-2 border-gray-300 text-gray-700 font-semibold hover:bg-gray-100 transition-colors"
          >
            {downloadingPdf ? "Preparing PDF..." : "Download PDF"}
          </button>
        </div>
      </div>
    </div>
  );
}
