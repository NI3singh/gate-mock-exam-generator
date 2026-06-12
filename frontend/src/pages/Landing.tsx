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
    desc: "Fresh, original questions every time — powered by state-of-the-art LLMs with syllabus-aware generation.",
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

const stats = [
  { value: "65", label: "Questions per test" },
  { value: "100", label: "Total marks" },
  { value: "3hr", label: "Timed exam" },
  { value: "∞", label: "Unlimited tests" },
];

export default function Landing() {
  const { dbUser, loading } = useAuth();

  if (!loading && dbUser) return <Navigate to="/dashboard" replace />;

  return (
    <div className="grid-bg min-h-screen bg-gray-50">
      {/* Grid pattern background style */}
      <style>{`
        .grid-bg {
          background-color: #ffffff;
          background-image:
            linear-gradient(rgba(0,0,0,0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,0,0,0.08) 1px, transparent 1px);
          background-size: 20px 20px;
        }
        .dot-bg {
          background-image: radial-gradient(circle, rgba(0,0,0,0.06) 1px, transparent 1px);
          background-size: 24px 24px;
        }
      `}</style>

      <Navbar />

      {/* ────── HERO ────── */}
      <section className="relative overflow-hidden px-4 pb-24 pt-20 sm:px-6 lg:px-8">
        {/* Decorative gradient blobs */}
        <div className="animate-blob pointer-events-none absolute -left-40 -top-40 h-[500px] w-[500px] rounded-full bg-blue-100 opacity-40 blur-3xl" />
        <div className="animate-blob-slow pointer-events-none absolute -right-32 top-20 h-[400px] w-[400px] rounded-full bg-indigo-100 opacity-50 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 left-1/2 h-[300px] w-[600px] -translate-x-1/2 rounded-full bg-sky-100 opacity-30 blur-3xl" />

        <div className="relative mx-auto max-w-4xl text-center">

          <h1 className="animate-fade-in-up text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
            Master{" "}
            <span className="bg-gradient-to-r from-blue-600 to-blue-500 bg-clip-text text-transparent">
              GATE 2027
            </span>
          </h1>
          <p className="animate-fade-in-up anim-delay-100 mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-gray-600">
            AI-powered, full-length mock tests for{" "}
            <strong>Computer Science</strong> and{" "}
            <strong>Data Science &amp; AI</strong>. Practice with questions that
            match real GATE style, difficulty, and format — every single time.
          </p>
          <div className="animate-fade-in-up anim-delay-200 mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              to="/signup"
              className="group w-full rounded-lg bg-blue-600 px-8 py-3.5 text-base font-semibold text-white shadow-md shadow-blue-200 transition-all hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-200 sm:w-auto"
            >
              Get Started — It's Free
              <span className="ml-2 inline-block transition-transform group-hover:translate-x-1">
                →
              </span>
            </Link>
            <a
              href="#features"
              className="w-full rounded-lg border border-gray-300 bg-white px-8 py-3.5 text-base font-semibold text-gray-700 shadow-sm transition-all hover:border-gray-400 hover:bg-gray-50 sm:w-auto"
            >
              Learn More ↓
            </a>
          </div>

          {/* Stats row */}
          <div className="animate-fade-in-up anim-delay-300 mx-auto mt-16 grid max-w-xl grid-cols-4 gap-4">
            {stats.map((s) => (
              <div key={s.label}>
                <div className="text-2xl font-bold text-blue-600 sm:text-3xl">
                  {s.value}
                </div>
                <div className="mt-1 text-xs text-gray-400 sm:text-sm">
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ────── FEATURES ────── */}
      <section id="features" className="grid-bg relative bg-white py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-center text-3xl font-bold text-gray-900">
            Everything you need to ace GATE
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-center text-gray-500">
            Built by GATE aspirants, for GATE aspirants.
          </p>

          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((f) => (
              <div
                key={f.title}
                className="group rounded-xl border border-gray-100 bg-white p-6 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-blue-100 hover:shadow-md"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-50 text-2xl transition-colors group-hover:bg-blue-100">
                  {f.icon}
                </div>
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
      <section className="dot-bg py-24">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-center text-3xl font-bold text-gray-900">
            How It Works
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-center text-gray-500">
            Three simple steps to your next mock test.
          </p>

          <div className="relative mt-14 grid gap-10 sm:grid-cols-3">
            {/* Connector line (hidden on mobile) */}
            <div className="pointer-events-none absolute left-0 right-0 top-7 hidden h-px bg-gradient-to-r from-transparent via-blue-200 to-transparent sm:block" />

            {steps.map((s) => (
              <div key={s.num} className="relative text-center">
                <div className="relative mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-xl font-bold text-white shadow-md shadow-blue-200 ring-4 ring-white">
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

      {/* ────── SUPPORTED PAPERS ────── */}
      <section className="grid-bg relative bg-white py-24">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-center text-3xl font-bold text-gray-900">
            Supported GATE Papers
          </h2>
          <div className="mt-12 grid gap-6 sm:grid-cols-2">
            {/* CS Card */}
            <div className="rounded-xl border border-gray-200 bg-gradient-to-br from-white to-gray-50 p-8 transition-all hover:border-blue-200 hover:shadow-md">
              <div className="inline-flex rounded-lg bg-blue-100 px-3 py-1 text-sm font-bold text-blue-700">
                CS
              </div>
              <h3 className="mt-4 text-xl font-bold text-gray-900">
                Computer Science & IT
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-gray-500">
                10 sections including Data Structures, Algorithms, OS, DBMS,
                Networks, TOC, Compiler Design, Digital Logic, and more.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {["DSA", "OS", "DBMS", "CN", "TOC", "COA"].map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* DA Card */}
            <div className="rounded-xl border border-gray-200 bg-gradient-to-br from-white to-gray-50 p-8 transition-all hover:border-blue-200 hover:shadow-md">
              <div className="inline-flex rounded-lg bg-blue-100 px-3 py-1 text-sm font-bold text-blue-700">
                DA
              </div>
              <h3 className="mt-4 text-xl font-bold text-gray-900">
                Data Science & AI
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-gray-500">
                7 sections covering Probability, Linear Algebra, ML, AI, Python
                Programming, Databases, and Optimization.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {["ML", "AI", "Probability", "Python", "DBMS", "LA"].map(
                  (tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600"
                    >
                      {tag}
                    </span>
                  )
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ────── CTA ────── */}
      <section className="relative overflow-hidden bg-blue-600 py-20 text-center text-white">
        {/* Subtle grid overlay */}
        <div
          className="pointer-events-none absolute inset-0 opacity-10"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.15) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        />
        <div className="relative">
          <h2 className="text-3xl font-bold sm:text-4xl">
            Ready to ace GATE 2027?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-blue-100">
            Join your peers and start taking unlimited AI-generated mock tests
            today.
          </p>
          <Link
            to="/signup"
            className="mt-8 inline-block rounded-lg bg-white px-8 py-3.5 text-base font-semibold text-blue-600 shadow transition-all hover:bg-blue-50 hover:shadow-lg"
          >
            Create Free Account
          </Link>
        </div>
      </section>{/*  */}

      {/* ────── FOOTER ────── */}
      <footer className="border-t border-gray-200 bg-white py-8 text-center text-sm text-gray-400">
        © Mock-Exam AI · Built for GATE 2027
        aspirants
      </footer>
    </div>
  );
}