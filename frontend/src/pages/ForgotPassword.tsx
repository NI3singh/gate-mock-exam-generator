import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import {
  getEmailValidationError,
  normalizeEmail,
} from "../utils/validation";

export default function ForgotPassword() {
  const { resetPassword } = useAuth();

  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    const normalizedEmail = normalizeEmail(email);
    const emailError = getEmailValidationError(normalizedEmail);
    if (emailError) {
      setError(emailError);
      return;
    }

    setSubmitting(true);

    try {
      await resetPassword(normalizedEmail);
      setEmail(normalizedEmail);
      setSent(true);
    } catch (err: any) {
      const code: string = err?.code ?? "";
      if (code === "auth/user-not-found") {
        setError("No account found with this email.");
      } else {
        setError(err?.message ?? "Failed to send reset email. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {submitting && (
        <LoadingSpinner size="lg" text="SENDING RESET LINK" fullPage />
      )}
      <Navbar />

      <div className="flex items-center justify-center px-4 py-16">
        <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
          <h2 className="text-center text-2xl font-bold text-gray-900">
            Reset your password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-500">
            Enter your email and we'll send a reset link.
          </p>

          {sent ? (
            <div className="mt-6 rounded-lg bg-green-50 p-4 text-center text-sm text-green-700">
              <p className="font-semibold">Check your inbox!</p>
              <p className="mt-1">
                We've sent a password-reset link to <strong>{email}</strong>.
              </p>
              <Link
                to="/login"
                className="mt-4 inline-block font-medium text-blue-600 hover:text-blue-500"
              >
                ← Back to Login
              </Link>
            </div>
          ) : (
            <>
              {error && (
                <div className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="mt-6 space-y-5">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Email
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoComplete="email"
                    className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    placeholder="you@example.com"
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {submitting ? "Sending…" : "Send Reset Link"}
                </button>
              </form>

              <p className="mt-6 text-center text-sm text-gray-500">
                <Link
                  to="/login"
                  className="font-medium text-blue-600 hover:text-blue-500"
                >
                  ← Back to Login
                </Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
