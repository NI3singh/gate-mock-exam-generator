import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";

import { useAuth } from "../hooks/useAuth";
import api from "../services/api";
import type { DashboardStats } from "../types";

import Navbar from "../components/layout/Navbar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import StatsCard from "../components/dashboard/StatsCard";
import RecentExams from "../components/dashboard/RecentExams";
import EmptyState from "../components/dashboard/EmptyState";

/* ── SVG icons (inline for simplicity) ── */
const icons = {
  exam: (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
    </svg>
  ),
  score: (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  ),
  trophy: (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  ),
  questions: (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
};

/* ── Greeting based on time of day ── */
function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

export default function Dashboard() {
  const { dbUser } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const { data } = await api.get<DashboardStats>("/dashboard/summary");
        setStats(data);
      } catch {
        toast.error("Failed to load dashboard data");
        // Set defaults so the page still renders
        setStats({
          total_exams_taken: 0,
          average_score: null,
          best_score: null,
          worst_score: null,
          total_questions_attempted: 0,
          recent_exams: [],
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (!dbUser || loading) return <LoadingSpinner fullScreen />;

  const hasExams = stats !== null && stats.total_exams_taken > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* ── Greeting Row ── */}
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
              {getGreeting()},{" "}
              {dbUser.display_name || dbUser.email.split("@")[0]} 👋
            </h1>
            <p className="mt-1 text-gray-500">
              {hasExams
                ? "Here's your preparation overview."
                : "Let's kickstart your GATE 2026 preparation!"}
            </p>
          </div>

          {/* Quick actions */}
          <div className="flex gap-3">
            <Link
              to="/generate-exam"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
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
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Generate New Exam
            </Link>
            <Link
              to="/analytics"
              className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50"
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
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              View Analytics
            </Link>
          </div>
        </div>

        {/* ── Stats Cards ── */}
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            label="Tests Taken"
            value={String(stats?.total_exams_taken ?? 0)}
            subtitle="mock exams completed"
            icon={icons.exam}
            color="blue"
          />
          <StatsCard
            label="Average Score"
            value={
              stats?.average_score !== null && stats?.average_score !== undefined
                ? `${stats.average_score.toFixed(1)}%`
                : "—"
            }
            subtitle="across all exams"
            icon={icons.score}
            color="green"
          />
          <StatsCard
            label="Best Score"
            value={
              stats?.best_score !== null && stats?.best_score !== undefined
                ? `${stats.best_score.toFixed(1)}`
                : "—"
            }
            subtitle="personal best (out of 100)"
            icon={icons.trophy}
            color="purple"
          />
          <StatsCard
            label="Questions Attempted"
            value={String(stats?.total_questions_attempted ?? 0)}
            subtitle="total questions answered"
            icon={icons.questions}
            color="orange"
          />
        </div>

        {/* ── Main Content Area ── */}
        <div className="mt-10">
          {hasExams && stats ? (
            <RecentExams exams={stats.recent_exams} />
          ) : (
            <EmptyState />
          )}
        </div>

        {/* ── GATE 2026 Info Bar ── */}
        <div className="mt-10 rounded-xl border border-blue-100 bg-blue-50 p-6">
          <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
            <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-blue-100">
              <span className="text-2xl">📅</span>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900">
                GATE 2026 Preparation
              </h3>
              <p className="mt-1 text-sm text-blue-700">
                Each mock test follows the exact GATE pattern: 65 questions, 100
                marks, 3 hours. Includes MCQ, MSQ, and NAT questions with
                negative marking for MCQs.
              </p>
            </div>
            {dbUser.preferred_paper && (
              <div className="flex-shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white">
                Paper: {dbUser.preferred_paper}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}