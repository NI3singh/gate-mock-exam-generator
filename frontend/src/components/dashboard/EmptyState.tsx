import { Link } from "react-router-dom";

export default function EmptyState() {
  return (
    <div className="rounded-xl border-2 border-dashed border-gray-300 bg-white px-6 py-16 text-center">
      {/* Illustration */}
      <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-blue-50">
        <span className="text-4xl">🎯</span>
      </div>

      <h3 className="mt-6 text-xl font-semibold text-gray-900">
        No exams yet
      </h3>
      <p className="mx-auto mt-2 max-w-md text-sm text-gray-500">
        Generate your first AI-powered GATE mock test and start your
        preparation journey. Each test is unique and follows the exact GATE
        2026 pattern.
      </p>

      <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <Link
          to="/generate-exam"
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          Generate Your First Exam
        </Link>
      </div>

      {/* Tips */}
      <div className="mx-auto mt-10 grid max-w-2xl gap-4 sm:grid-cols-3">
        {[
          {
            icon: "📄",
            title: "Choose Your Paper",
            desc: "CS or DA — pick the one you're preparing for",
          },
          {
            icon: "⚙️",
            title: "Configure Difficulty",
            desc: "Easy, Medium, Hard, or let AI decide",
          },
          {
            icon: "📊",
            title: "Track Progress",
            desc: "Detailed analytics after every attempt",
          },
        ].map((tip) => (
          <div
            key={tip.title}
            className="rounded-lg bg-gray-50 p-4 text-left"
          >
            <span className="text-xl">{tip.icon}</span>
            <p className="mt-2 text-sm font-medium text-gray-700">
              {tip.title}
            </p>
            <p className="mt-1 text-xs text-gray-400">{tip.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}