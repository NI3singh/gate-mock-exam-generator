import { Link } from "react-router-dom";

import Navbar from "../components/layout/Navbar";
import { useAuth } from "../hooks/useAuth";

export default function NotFound() {
  const { dbUser } = useAuth();

  return (
    <div className="min-h-screen">
      <Navbar />

      <main className="mx-auto flex max-w-4xl items-center justify-center px-4 py-20 sm:px-6 lg:px-8">
        <div className="w-full rounded-3xl border border-gray-200 bg-white p-10 text-center shadow-sm sm:p-14">
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-blue-50 text-3xl">
            404
          </div>

          <h1 className="mt-8 text-3xl font-bold text-gray-900">
            Page not found
          </h1>
          <p className="mx-auto mt-3 max-w-xl text-gray-500">
            The page you requested does not exist, may have moved, or needs a different route.
          </p>

          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              to={dbUser ? "/dashboard" : "/"}
              className="inline-flex w-full items-center justify-center rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 sm:w-auto"
            >
              {dbUser ? "Go to Dashboard" : "Go to Home"}
            </Link>
            <Link
              to="/generate-exam"
              className="inline-flex w-full items-center justify-center rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-50 sm:w-auto"
            >
              Generate Exam
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
