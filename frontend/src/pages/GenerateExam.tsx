import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { useAuth } from "../hooks/useAuth";
import api from "../services/api";
import type { ExamConfig, ExamGenerateResponse } from "../types";

import Navbar from "../components/layout/Navbar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import PaperSelector from "../components/exam/PaperSelector";
import ScopeSelector from "../components/exam/ScopeSelector";
import TopicPicker from "../components/exam/TopicPicker";
import DifficultySelector from "../components/exam/DifficultySelector";
import TypeRatioDisplay from "../components/exam/TypeRatioDisplay";

const DEFAULT_CONFIG: ExamConfig = {
  paper: "CS",
  scope: "full",
  selected_topics: [],
  difficulty: "auto",
  types_ratio: { MCQ: 0.6, MSQ: 0.2, NAT: 0.2 },
};

export default function GenerateExam() {
  const { dbUser } = useAuth();
  const navigate = useNavigate();

  const [config, setConfig] = useState<ExamConfig>(() => ({
    ...DEFAULT_CONFIG,
    paper: dbUser?.preferred_paper || "CS",
  }));
  const [submitting, setSubmitting] = useState(false);

  if (!dbUser) return <LoadingSpinner fullScreen />;

  const updateConfig = <K extends keyof ExamConfig>(
    key: K,
    value: ExamConfig[K]
  ) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const handlePaperChange = (paper: "CS" | "DA") => {
    setConfig((prev) => ({
      ...prev,
      paper,
      selected_topics: [], // Reset topics when paper changes
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // ── Client-side validation ──
    if (config.scope === "topic" && config.selected_topics.length === 0) {
      toast.error("Please select at least one topic.");
      return;
    }

    setSubmitting(true);
    try {
      const { data } = await api.post<ExamGenerateResponse>(
        "/exams/generate",
        {
          paper: config.paper,
          scope: config.scope,
          selected_topics:
            config.scope === "topic" ? config.selected_topics : null,
          difficulty: config.difficulty,
          types_ratio: config.types_ratio,
        }
      );

      toast.success("Exam configuration saved!");

      // Navigate to progress page (Part 7 — placeholder for now)
      navigate(`/exam/${data.exam_id}/progress`);
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail || "Failed to create exam. Please try again.";
      toast.error(detail);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
            Generate New Mock Test
          </h1>
          <p className="mt-2 text-gray-500">
            Configure your GATE 2026 mock exam. Each test follows the official
            pattern: 65 questions, 100 marks, 3 hours.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* ── Card 1: Paper Selection ── */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <PaperSelector value={config.paper} onChange={handlePaperChange} />
          </div>

          {/* ── Card 2: Scope ── */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <ScopeSelector
              value={config.scope}
              onChange={(scope) => updateConfig("scope", scope)}
            />

            {/* Topic picker — shown only when scope is "topic" */}
            {config.scope === "topic" && (
              <div className="mt-6 border-t border-gray-100 pt-6">
                <TopicPicker
                  paper={config.paper}
                  selected={config.selected_topics}
                  onChange={(topics) =>
                    updateConfig("selected_topics", topics)
                  }
                />
              </div>
            )}
          </div>

          {/* ── Card 3: Difficulty ── */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <DifficultySelector
              value={config.difficulty}
              onChange={(d) => updateConfig("difficulty", d)}
            />
          </div>

          {/* ── Card 4: Question Type Ratio ── */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <TypeRatioDisplay value={config.types_ratio} />
          </div>

          {/* ── Exam Summary ── */}
          <div className="rounded-xl border border-blue-100 bg-blue-50 p-6">
            <h3 className="text-sm font-semibold text-blue-900">
              Exam Summary
            </h3>
            <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
              <div>
                <span className="text-blue-600">Paper:</span>{" "}
                <span className="font-medium text-blue-900">
                  {config.paper}
                </span>
              </div>
              <div>
                <span className="text-blue-600">Questions:</span>{" "}
                <span className="font-medium text-blue-900">65</span>
              </div>
              <div>
                <span className="text-blue-600">Marks:</span>{" "}
                <span className="font-medium text-blue-900">100</span>
              </div>
              <div>
                <span className="text-blue-600">Duration:</span>{" "}
                <span className="font-medium text-blue-900">3 hours</span>
              </div>
              <div>
                <span className="text-blue-600">Scope:</span>{" "}
                <span className="font-medium text-blue-900">
                  {config.scope === "full"
                    ? "Full Syllabus"
                    : `${config.selected_topics.length} topic(s)`}
                </span>
              </div>
              <div>
                <span className="text-blue-600">Difficulty:</span>{" "}
                <span className="font-medium capitalize text-blue-900">
                  {config.difficulty}
                </span>
              </div>
              <div>
                <span className="text-blue-600">GA Section:</span>{" "}
                <span className="font-medium text-blue-900">
                  10 Qs (15 marks)
                </span>
              </div>
              <div>
                <span className="text-blue-600">Subject:</span>{" "}
                <span className="font-medium text-blue-900">
                  55 Qs (85 marks)
                </span>
              </div>
            </div>
          </div>

          {/* ── Submit Button ── */}
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              ← Cancel
            </button>

            <button
              type="submit"
              disabled={
                submitting ||
                (config.scope === "topic" &&
                  config.selected_topics.length === 0)
              }
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-8 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Saving Configuration…
                </>
              ) : (
                <>
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
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                  Generate Exam
                </>
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}