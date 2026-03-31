import { useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";

import LoadingSpinner from "../common/LoadingSpinner";
import api, { getApiErrorMessage } from "../../services/api";
import type { ExamHistoryItem } from "../../types";

interface Props {
  exams: ExamHistoryItem[];
  page: number;
  totalPages: number;
  loading?: boolean;
  onPageChange: (page: number) => void;
  onDeleted: () => void;
}

const statusConfig: Record<
  string,
  { label: string; dot: string; bg: string; text: string }
> = {
  generated: {
    label: "Ready",
    dot: "bg-blue-500",
    bg: "bg-blue-50",
    text: "text-blue-700",
  },
  generating: {
    label: "Generating",
    dot: "bg-indigo-500",
    bg: "bg-indigo-50",
    text: "text-indigo-700",
  },
  in_progress: {
    label: "In Progress",
    dot: "bg-yellow-500",
    bg: "bg-yellow-50",
    text: "text-yellow-700",
  },
  completed: {
    label: "Completed",
    dot: "bg-green-500",
    bg: "bg-green-50",
    text: "text-green-700",
  },
  failed: {
    label: "Failed",
    dot: "bg-red-500",
    bg: "bg-red-50",
    text: "text-red-700",
  },
  expired: {
    label: "Expired",
    dot: "bg-gray-400",
    bg: "bg-gray-50",
    text: "text-gray-600",
  },
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function getPrimaryAction(exam: ExamHistoryItem) {
  if (exam.status === "completed" && exam.attempt_id) {
    return {
      to: `/result/${exam.attempt_id}`,
      label: "View Result",
      className: "bg-green-600 hover:bg-green-700 text-white",
    };
  }

  if (exam.status === "in_progress") {
    return {
      to: `/exam/${exam.id}`,
      label: "Resume",
      className: "bg-yellow-500 hover:bg-yellow-600 text-white",
    };
  }

  if (exam.status === "generated") {
    return {
      to: `/exam/${exam.id}`,
      label: "Start Exam",
      className: "bg-blue-600 hover:bg-blue-700 text-white",
    };
  }

  if (exam.status === "generating") {
    return {
      to: `/exam/${exam.id}/progress`,
      label: "View Progress",
      className: "bg-indigo-600 hover:bg-indigo-700 text-white",
    };
  }

  return null;
}

export default function ExamHistoryList({
  exams,
  page,
  totalPages,
  loading = false,
  onPageChange,
  onDeleted,
}: Props) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (exam: ExamHistoryItem) => {
    const confirmed = window.confirm(
      `Delete this ${exam.paper} ${exam.scope === "full" ? "full-syllabus" : "topic-wise"} exam?`
    );
    if (!confirmed) return;

    try {
      setDeletingId(exam.id);
      await api.delete(`/exams/${exam.id}`, { suppressErrorToast: true });
      toast.success("Exam deleted");
      onDeleted();
    } catch (err: any) {
      toast.error(getApiErrorMessage(err, "Failed to delete exam"));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
      <div className="flex flex-col gap-3 border-b border-gray-100 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Exam History</h3>
          <p className="mt-1 text-sm text-gray-500">
            Review all exams, resume unfinished ones, or open completed results.
          </p>
        </div>
        <Link
          to="/question-bank"
          className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
        >
          Browse Question Bank
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center px-6 py-10">
          <LoadingSpinner size="lg" text="LOADING EXAM HISTORY" />
        </div>
      ) : exams.length === 0 ? (
        <div className="px-6 py-10 text-center text-sm text-gray-500">
          No exams found on this page.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-100">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Exam</th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Difficulty</th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Status</th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Score</th>
                <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wide text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {exams.map((exam) => {
                const st = statusConfig[exam.status] || statusConfig.generated;
                const action = getPrimaryAction(exam);

                return (
                  <tr key={exam.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {formatDate(exam.created_at)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-start gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">
                          {exam.paper}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-gray-900">
                            {exam.scope === "full" ? "Full Syllabus" : "Topic-wise"}
                          </p>
                          <p className="mt-1 text-xs text-gray-500">
                            {exam.total_questions} questions · {exam.total_marks} marks · {exam.duration_minutes} min
                          </p>
                          {exam.scope === "topic" && exam.selected_topics?.length ? (
                            <p className="mt-1 max-w-xs text-xs text-gray-400">
                              {exam.selected_topics.slice(0, 3).join(", ")}
                              {exam.selected_topics.length > 3 ? ` +${exam.selected_topics.length - 3} more` : ""}
                            </p>
                          ) : null}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm capitalize text-gray-700">
                      {exam.difficulty}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${st.bg} ${st.text}`}
                      >
                        <span className={`h-1.5 w-1.5 rounded-full ${st.dot}`} />
                        {st.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                      {exam.score !== null ? `${exam.score.toFixed(2)} / ${exam.max_score}` : "—"}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-end gap-2">
                        {action ? (
                          <Link
                            to={action.to}
                            className={`rounded-lg px-3 py-2 text-xs font-semibold transition-colors ${action.className}`}
                          >
                            {action.label}
                          </Link>
                        ) : (
                          <span className="rounded-lg border border-gray-200 px-3 py-2 text-xs text-gray-400">
                            No action
                          </span>
                        )}
                        <button
                          onClick={() => handleDelete(exam)}
                          disabled={deletingId === exam.id}
                          className="rounded-lg border border-red-200 px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {deletingId === exam.id ? "Deleting..." : "Delete"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-between border-t border-gray-100 px-6 py-4">
        <button
          onClick={() => onPageChange(Math.max(1, page - 1))}
          disabled={page <= 1}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Previous
        </button>
        <span className="text-sm text-gray-500">
          Page {totalPages === 0 ? 0 : page} of {totalPages}
        </span>
        <button
          onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          disabled={totalPages === 0 || page >= totalPages}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
