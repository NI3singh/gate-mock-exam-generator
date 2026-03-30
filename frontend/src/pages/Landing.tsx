import { Link } from "react-router-dom";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar";

const features = [
  {
    icon: "📄",
    title: "Full-Length Mock Tests",
    desc: "65 questions · 100 marks · 180 minutes — exactly like the real GATE exam.",
  },
  {
    icon: "🤖",
    title: "AI-Generated Questions",
    desc: "Fresh, original questions every time — powered by state-of-the-art LLMs with PYQ-aware generation.",
  },
  {
    icon: "🖥️",
    title: "GATE-Authentic Interface",
    desc: "Question palette, section tabs, mark-for-review, countdown timer — the real exam experience.",
  },
  {
    icon: "📊",
    title: "Detailed Analytics",
    desc: "Topic-wise accuracy, score trends, weak-area identification — know exactly where to improve.",
  },
];

const steps = [
  { num: "1", title: "Sign Up", desc: "Create your free account in seconds." },
  {
    num: "2",
    title: "Generate a Test",
    desc: "Choose CS or DA, pick topics or go full-syllabus, and let AI craft your exam.",
  },
  {
    num: "3",
    title: "Analyze Results",
    desc: "Get instant grading, step-by-step solutions, and performance analytics.",
  },
];

export default function Landing() {
  const { dbUser, loading } = useAuth();

  // If already logged in, go straight to dashboard
  if (!loading && dbUser) return <Navigate to="/dashboard" replace />;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      {/* ────── HERO ────── */}
      <section className="px-4 pb-20 pt-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
            Master{" "}
            <span className="text-blue-600">GATE 2026</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
            AI-powered, full-length mock tests for{" "}
            <strong>Computer Science</strong> and{" "}
            <strong>Data Science &amp; AI</strong>. Practice with questions that
            match real GATE style, difficulty, and format — every single time.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              to="/signup"
              className="w-full rounded-lg bg-blue-600 px-8 py-3.5 text-base font-semibold text-white shadow-sm hover:bg-blue-700 sm:w-auto"
            >
              Get Started — It's Free
            </Link>
            <a
              href="#features"
              className="w-full rounded-lg border border-gray-300 bg-white px-8 py-3.5 text-base font-semibold text-gray-700 shadow-sm hover:bg-gray-50 sm:w-auto"
            >
              Learn More ↓
            </a>
          </div>
        </div>
      </section>

      {/* ────── FEATURES ────── */}
      <section id="features" className="bg-white py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-center text-3xl font-bold text-gray-900">
            Everything you need to ace GATE
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-center text-gray-500">
            Built by GATE aspirants, for GATE aspirants.
          </p>

          <div className="mt-14 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((f) => (
              <div
                key={f.title}
                className="rounded-xl border border-gray-100 bg-gray-50 p-6 shadow-sm"
              >
                <span className="text-3xl">{f.icon}</span>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  {f.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-gray-500">
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ────── HOW IT WORKS ────── */}
      <section className="py-20">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-center text-3xl font-bold text-gray-900">
            How It Works
          </h2>

          <div className="mt-14 grid gap-10 sm:grid-cols-3">
            {steps.map((s) => (
              <div key={s.num} className="text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-xl font-bold text-white">
                  {s.num}
                </div>
                <h3 className="mt-5 text-lg font-semibold text-gray-900">
                  {s.title}
                </h3>
                <p className="mt-2 text-sm text-gray-500">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ────── CTA ────── */}
      <section className="bg-blue-600 py-16 text-center text-white">
        <h2 className="text-3xl font-bold">Ready to ace GATE 2026?</h2>
        <p className="mx-auto mt-4 max-w-xl text-blue-100">
          Join your peers and start taking unlimited AI-generated mock tests
          today.
        </p>
        <Link
          to="/signup"
          className="mt-8 inline-block rounded-lg bg-white px-8 py-3.5 text-base font-semibold text-blue-600 shadow hover:bg-blue-50"
        >
          Create Free Account
        </Link>
      </section>

      {/* ────── FOOTER ────── */}
      <footer className="border-t border-gray-200 bg-white py-8 text-center text-sm text-gray-400">
        © {new Date().getFullYear()} GATE MockTest · Built for GATE 2026 aspirants
      </footer>
    </div>
  );
}
