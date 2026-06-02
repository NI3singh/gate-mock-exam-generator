import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import Navbar from "../components/layout/Navbar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import StatsCard from "../components/dashboard/StatsCard";
import api from "../services/api";
import type {
  AnalyticsDashboardData,
  TopicPerformanceItem,
  TopicPerformanceResponse,
} from "../types";

const icons = {
  exams: (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
    </svg>
  ),
  average: (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  ),
  best: (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  ),
  worst: (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M12 8v4m0 4h.01M4.93 19h14.14c1.54 0 2.5-1.67 1.73-3L13.73 3c-.77-1.33-2.69-1.33-3.46 0L3.2 16c-.77 1.33.19 3 1.73 3z" />
    </svg>
  ),
  improvement: (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M7 17l9.2-9.2M17 17V7H7" />
    </svg>
  ),
};

function formatValue(value: number | null): string {
  if (value === null || value === undefined) return "—";
  return value.toFixed(1);
}

function formatChartDate(value: string): string {
  const date = new Date(value);
  return date.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

function TopicList({
  title,
  topics,
  tone,
}: {
  title: string;
  topics: TopicPerformanceItem[];
  tone: "green" | "red";
}) {
  const toneClasses =
    tone === "green"
      ? {
          chip: "bg-green-100 text-green-700",
          border: "border-green-100",
          value: "text-green-700",
        }
      : {
          chip: "bg-red-100 text-red-700",
          border: "border-red-100",
          value: "text-red-700",
        };

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${toneClasses.chip}`}>
          {topics.length} topic{topics.length === 1 ? "" : "s"}
        </span>
      </div>

      {topics.length === 0 ? (
        <p className="text-sm text-gray-500">No topic data available yet.</p>
      ) : (
        <div className="space-y-3">
          {topics.map((topic) => (
            <div
              key={`${topic.section_name}-${topic.topic}`}
              className={`rounded-xl border ${toneClasses.border} bg-gray-50 px-4 py-3`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium text-gray-900">{topic.topic}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    {topic.section_name} · {topic.correct} correct / {topic.total_questions} total
                  </p>
                </div>
                <div className={`text-right text-sm font-bold ${toneClasses.value}`}>
                  {topic.accuracy.toFixed(1)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Analytics() {
  const [dashboard, setDashboard] = useState<AnalyticsDashboardData | null>(null);
  const [topicPerformance, setTopicPerformance] = useState<TopicPerformanceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [{ data: dashboardData }, { data: topicData }] = await Promise.all([
          api.get<AnalyticsDashboardData>("/analytics/dashboard"),
          api.get<TopicPerformanceResponse>("/analytics/topic-performance"),
        ]);

        setDashboard(dashboardData);
        setTopicPerformance(topicData.topics);
      } catch {
        setDashboard(null);
        setTopicPerformance([]);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const chartTopics = useMemo(() => {
    return [...topicPerformance]
      .sort((a, b) => b.total_questions - a.total_questions || b.accuracy - a.accuracy)
      .slice(0, 10)
      .map((topic) => ({
        ...topic,
        shortTopic:
          topic.topic.length > 26 ? `${topic.topic.slice(0, 26).trim()}...` : topic.topic,
      }))
      .reverse();
  }, [topicPerformance]);

  if (loading) {
    return <LoadingSpinner size="xl" text="ANALYZING PERFORMANCE" fullPage />;
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <main className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="rounded-xl border border-red-200 bg-white p-10 text-center shadow-sm">
            <h1 className="text-2xl font-bold text-gray-900">Could Not Load Analytics</h1>
            <p className="mt-3 text-gray-500">
              Something went wrong while loading your analytics dashboard.
            </p>
            <Link
              to="/dashboard"
              className="mt-8 inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </main>
      </div>
    );
  }

  if (dashboard.total_exams_taken === 0) {
    return (
      <div className="min-h-screen">
        <Navbar />

        <main className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6 lg:px-8">
          <div className="rounded-xl border border-gray-200 bg-white p-12 shadow-sm">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-purple-50">
              <span className="text-3xl">📊</span>
            </div>

            <h1 className="mt-6 text-2xl font-bold text-gray-900">
              Performance Analytics
            </h1>
            <p className="mx-auto mt-3 max-w-md text-gray-500">
              Your topic-wise accuracy, score trends, and weak-area analysis will
              appear here once you've taken at least one exam.
            </p>

            <div className="mt-8 flex justify-center gap-3">
              <Link
                to="/generate-exam"
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
              >
                + Generate Exam
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                ← Back to Dashboard
              </Link>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const trendTone =
    dashboard.improvement_percentage > 0
      ? "text-green-600"
      : dashboard.improvement_percentage < 0
        ? "text-red-600"
        : "text-gray-600";

  return (
    <div className="min-h-screen">
      <Navbar />

      <main className="app-shell mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Performance Analytics
            </h1>
            <p className="mt-2 max-w-3xl text-gray-500">
              Track score trends, topic-wise accuracy, and the areas where your
              preparation is strongest or needs more attention.
            </p>
          </div>
          <div className="rounded-xl border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-800">
            {dashboard.total_questions_attempted} questions attempted across{" "}
            {dashboard.total_exams_taken} exam{dashboard.total_exams_taken === 1 ? "" : "s"}
          </div>
        </div>

        <div className="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-5">
          <StatsCard
            label="Total Exams"
            value={String(dashboard.total_exams_taken)}
            subtitle="completed mock tests"
            icon={icons.exams}
            color="blue"
          />
          <StatsCard
            label="Average Score"
            value={formatValue(dashboard.average_score)}
            subtitle="average out of 100"
            icon={icons.average}
            color="green"
          />
          <StatsCard
            label="Best Score"
            value={formatValue(dashboard.best_score)}
            subtitle="highest score so far"
            icon={icons.best}
            color="purple"
          />
          <StatsCard
            label="Worst Score"
            value={formatValue(dashboard.worst_score)}
            subtitle="lowest score so far"
            icon={icons.worst}
            color="orange"
          />
          <StatsCard
            label="Improvement"
            value={`${dashboard.improvement_percentage >= 0 ? "+" : ""}${dashboard.improvement_percentage.toFixed(1)}%`}
            subtitle="latest vs first exam"
            icon={icons.improvement}
            color="blue"
          />
        </div>

        <div className="mt-8 grid gap-6 xl:grid-cols-[1.25fr_1fr]">
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Score Trend</h2>
                <p className="mt-1 text-sm text-gray-500">
                  Percentage trend across all submitted exams
                </p>
              </div>
              <div className={`text-sm font-semibold ${trendTone}`}>
                {dashboard.improvement_percentage >= 0 ? "+" : ""}
                {dashboard.improvement_percentage.toFixed(1)} points
              </div>
            </div>

            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dashboard.score_history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="submitted_at"
                    tickFormatter={formatChartDate}
                    stroke="#94a3b8"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    domain={[0, 100]}
                    stroke="#94a3b8"
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    formatter={(value) => [`${Number(value ?? 0).toFixed(1)}%`, "Score"]}
                    labelFormatter={(label) => formatChartDate(String(label))}
                  />
                  <Line
                    type="monotone"
                    dataKey="percentage"
                    stroke="#2563eb"
                    strokeWidth={3}
                    dot={{ r: 4, fill: "#2563eb" }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <h2 className="text-lg font-semibold text-gray-900">Topic-wise Accuracy</h2>
              <p className="mt-1 text-sm text-gray-500">
                Most attempted topics ranked by accuracy
              </p>
            </div>

            <div
              className="min-h-[320px]"
              style={{ height: `${Math.max(320, chartTopics.length * 48)}px` }}
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartTopics} layout="vertical" margin={{ left: 16, right: 16 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" tick={{ fontSize: 12 }} />
                  <YAxis
                    type="category"
                    dataKey="shortTopic"
                    width={150}
                    stroke="#94a3b8"
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    formatter={(value) => [`${Number(value ?? 0).toFixed(1)}%`, "Accuracy"]}
                    labelFormatter={(_, payload) => payload?.[0]?.payload?.topic ?? ""}
                  />
                  <Bar dataKey="accuracy" fill="#7c3aed" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <TopicList title="Weak Topics" topics={dashboard.weak_topics} tone="red" />
          <TopicList title="Strong Topics" topics={dashboard.strong_topics} tone="green" />
        </div>

        <div className="mt-8 flex justify-start">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            ← Back to Dashboard
          </Link>
        </div>
      </main>
    </div>
  );
}
