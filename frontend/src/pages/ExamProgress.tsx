import { useParams, Link } from "react-router-dom";
import Navbar from "../components/layout/Navbar";

export default function ExamProgress() {
  const { examId } = useParams<{ examId: string }>();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="mx-auto max-w-2xl px-4 py-16 text-center sm:px-6 lg:px-8">
        <div className="rounded-xl border border-gray-200 bg-white p-12 shadow-sm">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-blue-50">
            <span className="text-3xl">⏳</span>
          </div>

          <h1 className="mt-6 text-2xl font-bold text-gray-900">
            Exam Generation In Progress
          </h1>
          <p className="mx-auto mt-3 max-w-md text-gray-500">
            AI is generating your exam questions. This page will show a live
            progress bar in the next module.
          </p>

          <div className="mt-4 rounded-lg bg-gray-50 p-3">
            <p className="text-xs text-gray-400">
              Exam ID: <code className="text-gray-600">{examId}</code>
            </p>
          </div>

          <div className="mt-8 flex justify-center gap-3">
            <Link
              to="/dashboard"
              className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}