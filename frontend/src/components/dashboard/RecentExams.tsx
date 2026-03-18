import type { RecentExam } from "../../types";

interface Props {
  exams: RecentExam[];
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

export default function RecentExams({ exams }: Props) {
  if (exams.length === 0) return null;

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Exams</h3>
        <span className="text-sm text-gray-400">{exams.length} exam(s)</span>
      </div>

      {/* List */}
      <ul className="divide-y divide-gray-100">
        {exams.map((exam) => {
          const st = statusConfig[exam.status] || statusConfig.generated;

          return (
            <li
              key={exam.id}
              className="flex items-center justify-between px-6 py-4 transition-colors hover:bg-gray-50"
            >
              {/* Left */}
              <div className="flex items-center gap-4">
                {/* Paper badge */}
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">
                  {exam.paper}
                </div>

                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {exam.paper} — {exam.scope === "full" ? "Full Syllabus" : "Topic-wise"}{" "}
                    <span className="text-gray-400">·</span>{" "}
                    <span className="capitalize text-gray-500">
                      {exam.difficulty}
                    </span>
                  </p>
                  <p className="mt-0.5 text-xs text-gray-400">
                    {formatDate(exam.created_at)} · {exam.total_questions} Qs ·{" "}
                    {exam.total_marks} marks
                  </p>
                </div>
              </div>

              {/* Right */}
              <div className="flex items-center gap-4">
                {/* Score (if completed) */}
                {exam.status === "completed" && exam.score !== null && (
                  <span className="text-sm font-semibold text-gray-900">
                    {exam.score} / {exam.max_score}
                  </span>
                )}

                {/* Status badge */}
                <span
                  className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${st.bg} ${st.text}`}
                >
                  <span className={`h-1.5 w-1.5 rounded-full ${st.dot}`} />
                  {st.label}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}