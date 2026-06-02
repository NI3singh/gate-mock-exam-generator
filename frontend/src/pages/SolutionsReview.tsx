import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import katex from "katex";
import Prism from "prismjs";
import "prismjs/components/prism-c";
import "prismjs/components/prism-python";

import api, { getApiErrorMessage } from "../services/api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import type {
  AttemptDetailResponse,
  MCQAnswer,
  MSQAnswer,
  NATAnswer,
  SolutionItem,
} from "../types";

type ReviewStatus = "correct" | "wrong" | "skipped";
type ReviewSection = "all" | "GA" | "Subject";
type NATReviewAnswer = { value: string | number; tolerance?: number };

function getReviewStatus(solution: SolutionItem): ReviewStatus {
  if (solution.user_answer === null) return "skipped";
  return solution.is_correct ? "correct" : "wrong";
}

function MathText({ text }: { text: string }) {
  const rendered = useMemo(() => {
    try {
      const parts: Array<{ type: "text" | "display" | "inline"; content: string }> = [];
      const displaySplit = text.split(/(\$\$[\s\S]*?\$\$)/g);

      for (const chunk of displaySplit) {
        if (chunk.startsWith("$$") && chunk.endsWith("$$") && chunk.length > 4) {
          parts.push({ type: "display", content: chunk.slice(2, -2) });
          continue;
        }

        const inlineSplit = chunk.split(/(\$[^$\n]+?\$)/g);
        for (const piece of inlineSplit) {
          if (piece.startsWith("$") && piece.endsWith("$") && piece.length > 2) {
            parts.push({ type: "inline", content: piece.slice(1, -1) });
          } else {
            parts.push({ type: "text", content: piece });
          }
        }
      }

      return parts
        .map((part) => {
          if (part.type === "display") {
            return katex.renderToString(part.content, {
              displayMode: true,
              throwOnError: false,
              trust: false,
            });
          }
          if (part.type === "inline") {
            return katex.renderToString(part.content, {
              displayMode: false,
              throwOnError: false,
              trust: false,
            });
          }

          return part.content
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\n/g, "<br/>");
        })
        .join("");
    } catch {
      return null;
    }
  }, [text]);

  if (rendered !== null) {
    return (
      <span
        className="leading-relaxed"
        dangerouslySetInnerHTML={{ __html: rendered }}
      />
    );
  }

  return <span className="whitespace-pre-wrap leading-relaxed">{text}</span>;
}

function CodeBlock({ code, language }: { code: string; language: string | null }) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (ref.current) {
      Prism.highlightElement(ref.current);
    }
  }, [code]);

  const langClass = language === "python" ? "language-python" : "language-c";

  return (
    <div className="my-4 overflow-x-auto rounded-lg border border-gray-200 bg-gray-900">
      <div className="border-b border-gray-700 px-4 py-2">
        <span className="text-xs font-medium uppercase tracking-wide text-gray-400">
          {language ?? "code"}
        </span>
      </div>
      <pre className="overflow-x-auto p-4 text-sm">
        <code ref={ref} className={langClass}>
          {code}
        </code>
      </pre>
    </div>
  );
}

function ReviewPalette({
  solutions,
  activeSection,
  currentQno,
  onNavigate,
  onSectionChange,
}: {
  solutions: SolutionItem[];
  activeSection: ReviewSection;
  currentQno: number;
  onNavigate: (qno: number) => void;
  onSectionChange: (section: ReviewSection) => void;
}) {
  const gaSolutions = solutions.filter((solution) => solution.section === "GA");
  const subjectSolutions = solutions.filter((solution) => solution.section === "Subject");

  const filteredSolutions =
    activeSection === "GA"
      ? gaSolutions
      : activeSection === "Subject"
        ? subjectSolutions
        : solutions;

  const counts = useMemo(() => {
    let correct = 0;
    let wrong = 0;
    let skipped = 0;

    for (const solution of solutions) {
      const status = getReviewStatus(solution);
      if (status === "correct") correct += 1;
      else if (status === "wrong") wrong += 1;
      else skipped += 1;
    }

    return { correct, wrong, skipped };
  }, [solutions]);

  const statusBg: Record<ReviewStatus, string> = {
    correct: "bg-green-500 text-white hover:bg-green-600",
    wrong: "bg-red-500 text-white hover:bg-red-600",
    skipped: "bg-gray-200 text-gray-700 hover:bg-gray-300",
  };

  return (
    <div className="flex h-full w-72 flex-shrink-0 flex-col border-l border-gray-200 bg-white">
      <div className="flex border-b border-gray-200 text-xs font-medium">
        {(["all", "GA", "Subject"] as const).map((section) => (
          <button
            key={section}
            onClick={() => onSectionChange(section)}
            className={`flex-1 py-2 transition-colors ${
              activeSection === section
                ? "border-b-2 border-blue-600 bg-blue-50 text-blue-700"
                : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            {section === "all"
              ? "All"
              : section === "GA"
                ? `GA (${gaSolutions.length})`
                : `Subject (${subjectSolutions.length})`}
          </button>
        ))}
      </div>

      <div className="space-y-2 border-b border-gray-100 px-4 py-4 text-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-green-700">
            <div className="h-4 w-4 rounded bg-green-500" />
            <span>Correct</span>
          </div>
          <span className="font-semibold">{counts.correct}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-red-700">
            <div className="h-4 w-4 rounded bg-red-500" />
            <span>Wrong</span>
          </div>
          <span className="font-semibold">{counts.wrong}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-gray-700">
            <div className="h-4 w-4 rounded bg-gray-200" />
            <span>Skipped</span>
          </div>
          <span className="font-semibold">{counts.skipped}</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="grid grid-cols-5 gap-2">
          {filteredSolutions.map((solution) => {
            const status = getReviewStatus(solution);
            const isCurrent = solution.qno === currentQno;

            return (
              <button
                key={solution.qno}
                onClick={() => onNavigate(solution.qno)}
                className={`h-10 w-10 rounded text-xs font-semibold transition-all ${
                  statusBg[status]
                } ${isCurrent ? "ring-2 ring-gray-800 ring-offset-1 scale-110" : ""}`}
                title={`Q${solution.qno} - ${status}`}
              >
                {solution.qno}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function ChoiceReview({
  choice,
  index,
  solution,
}: {
  choice: string;
  index: number;
  solution: SolutionItem;
}) {
  const correctAnswer = solution.correct_answer as MCQAnswer | MSQAnswer;
  const userAnswer = solution.user_answer as MCQAnswer | MSQAnswer | null;

  const isCorrectChoice =
    solution.question_type === "MCQ"
      ? (correctAnswer as MCQAnswer).index === index
      : (correctAnswer as MSQAnswer).indices.includes(index);

  const isUserChoice =
    userAnswer !== null &&
    (solution.question_type === "MCQ"
      ? (userAnswer as MCQAnswer).index === index
      : (userAnswer as MSQAnswer).indices.includes(index));

  const rowClass = isCorrectChoice
    ? "border-green-400 bg-green-50 text-green-900"
    : isUserChoice
      ? "border-red-400 bg-red-50 text-red-900"
      : "border-gray-200 bg-gray-50 text-gray-700";

  return (
    <div className={`flex items-start gap-3 rounded-lg border-2 p-3 ${rowClass}`}>
      <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-white text-xs font-semibold">
        {String.fromCharCode(65 + index)}
      </div>
      <div className="min-w-0 flex-1 text-sm">
        <MathText text={choice} />
      </div>
      <div className="flex flex-col items-end gap-1 text-xs font-semibold">
        {isCorrectChoice && <span className="text-green-700">Correct answer</span>}
        {isUserChoice && !isCorrectChoice && <span className="text-red-700">Your answer</span>}
      </div>
    </div>
  );
}

export default function SolutionsReview() {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [result, setResult] = useState<AttemptDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentQno, setCurrentQno] = useState(1);
  const [activeSection, setActiveSection] = useState<ReviewSection>("all");

  useEffect(() => {
    if (!attemptId) return;

    const load = async () => {
      try {
        const { data } = await api.get<AttemptDetailResponse>(`/attempts/${attemptId}`);
        setResult(data);
      } catch (err: any) {
        const message = getApiErrorMessage(err, "Failed to load solutions review.");
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [attemptId]);

  const solutions = useMemo(
    () => [...(result?.solutions ?? [])].sort((a, b) => a.qno - b.qno),
    [result?.solutions]
  );

  const currentSolution = useMemo(
    () => solutions.find((solution) => solution.qno === currentQno) ?? null,
    [solutions, currentQno]
  );

  const currentIndex = useMemo(
    () => solutions.findIndex((solution) => solution.qno === currentQno),
    [solutions, currentQno]
  );

  useEffect(() => {
    if (solutions.length === 0) return;
    if (solutions.some((solution) => solution.qno === currentQno)) return;
    setCurrentQno(solutions[0].qno);
  }, [solutions, currentQno]);

  const counts = useMemo(() => {
    let correct = 0;
    let wrong = 0;
    let skipped = 0;

    for (const solution of solutions) {
      const status = getReviewStatus(solution);
      if (status === "correct") correct += 1;
      else if (status === "wrong") wrong += 1;
      else skipped += 1;
    }

    return { correct, wrong, skipped };
  }, [solutions]);

  const handlePrevious = useCallback(() => {
    if (currentIndex <= 0) return;
    setCurrentQno(solutions[currentIndex - 1].qno);
  }, [currentIndex, solutions]);

  const handleNext = useCallback(() => {
    if (currentIndex < 0 || currentIndex >= solutions.length - 1) return;
    setCurrentQno(solutions[currentIndex + 1].qno);
  }, [currentIndex, solutions]);

  if (loading) {
    return <LoadingSpinner size="xl" text="LOADING SOLUTIONS" fullPage />;
  }

  if (error || !result) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="max-w-md rounded-xl border border-red-200 bg-white p-8 text-center">
          <div className="mb-4 text-4xl">⚠️</div>
          <h2 className="mb-2 text-lg font-bold text-gray-900">Could Not Load Solutions</h2>
          <p className="mb-6 text-sm text-red-600">{error ?? "Unknown error"}</p>
          <button
            onClick={() => navigate("/dashboard")}
            className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (solutions.length === 0 || !currentSolution) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="max-w-md rounded-xl border border-amber-200 bg-white p-8 text-center">
          <div className="mb-4 text-4xl">⚠️</div>
          <h2 className="mb-2 text-lg font-bold text-gray-900">No Solutions Available</h2>
          <p className="mb-6 text-sm text-amber-700">
            This attempt did not return any solution data for review.
          </p>
          <button
            onClick={() => navigate(`/result/${attemptId}`)}
            className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            Back to Result
          </button>
        </div>
      </div>
    );
  }

  const reviewStatus = getReviewStatus(currentSolution);
  const reviewBadgeClass =
    reviewStatus === "correct"
      ? "bg-green-100 text-green-700"
      : reviewStatus === "wrong"
        ? "bg-red-100 text-red-700"
        : "bg-gray-100 text-gray-700";

  const userNatAnswer = currentSolution.user_answer as NATAnswer | null;
  const correctNatAnswer = currentSolution.correct_answer as NATReviewAnswer;

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-gray-100">
      <div className="flex flex-shrink-0 items-center justify-between bg-blue-800 px-4 py-3 text-white shadow-md">
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold">Solutions Review</span>
          <span className="text-blue-300">|</span>
          <span className="text-sm text-blue-200">
            Paper: <strong className="text-white">{result.paper}</strong>
          </span>
          <span className="text-blue-300">|</span>
          <span className="text-sm text-blue-200">
            Score: <strong className="text-white">{result.score.toFixed(2)}</strong> / {result.max_score}
          </span>
        </div>

        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-blue-900 px-3 py-1.5 text-xs font-semibold text-blue-100">
            {counts.correct} correct / {counts.wrong} wrong / {counts.skipped} skipped
          </div>
          <button
            onClick={() => navigate(`/result/${attemptId}`)}
            className="rounded-lg border border-blue-500 px-3 py-1.5 text-xs font-medium text-blue-100 hover:bg-blue-700"
          >
            Back to Result
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex flex-shrink-0 items-center gap-3 border-b border-gray-200 bg-white px-6 py-3">
            <span className="text-sm font-bold text-gray-800">
              Question {currentSolution.qno} of {solutions.length}
            </span>
            <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-700">
              {currentSolution.question_type}
            </span>
            <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-700">
              {currentSolution.marks} mark{currentSolution.marks > 1 ? "s" : ""}
            </span>
            <span className="rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700">
              {currentSolution.section_name}
            </span>
            <span className={`ml-auto rounded-full px-2.5 py-1 text-xs font-semibold ${reviewBadgeClass}`}>
              {reviewStatus === "correct"
                ? "Correct"
                : reviewStatus === "wrong"
                  ? "Wrong"
                  : "Skipped"}
            </span>
          </div>

          <div className="flex-1 overflow-y-auto px-6 py-5">
            <div className="text-base leading-relaxed text-gray-900">
              <MathText text={currentSolution.stem_tex} />
            </div>

            {currentSolution.code_snippet && (
              <CodeBlock
                code={currentSolution.code_snippet}
                language={currentSolution.code_language}
              />
            )}

            <div className="mt-6 space-y-3">
              {currentSolution.choices?.map((choice, index) => (
                <ChoiceReview
                  key={`${currentSolution.qno}-${index}`}
                  choice={choice}
                  index={index}
                  solution={currentSolution}
                />
              ))}

              {currentSolution.question_type === "NAT" && (
                <div className="space-y-3">
                  <div
                    className={`rounded-lg border-2 px-4 py-3 text-sm ${
                      userNatAnswer === null
                        ? "border-gray-200 bg-gray-50 text-gray-600"
                        : currentSolution.is_correct
                          ? "border-green-400 bg-green-50 text-green-900"
                          : "border-red-400 bg-red-50 text-red-900"
                    }`}
                  >
                    <span className="font-semibold">Your answer: </span>
                    {userNatAnswer?.value?.trim() ? userNatAnswer.value : "Not answered"}
                  </div>

                  <div className="rounded-lg border-2 border-green-400 bg-green-50 px-4 py-3 text-sm text-green-900">
                    <span className="font-semibold">Correct answer: </span>
                    {String(correctNatAnswer.value)}
                    {typeof correctNatAnswer.tolerance === "number" &&
                      ` (±${correctNatAnswer.tolerance})`}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-8 rounded-xl border border-blue-200 bg-blue-50 p-5">
              <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-blue-700">
                Step-by-step solution
              </h3>
              <div className="text-sm leading-7 text-gray-800">
                <MathText
                  text={
                    currentSolution.solution_tex?.trim() || "Solution not available for this question."
                  }
                />
              </div>
            </div>
          </div>

          <div className="flex flex-shrink-0 items-center gap-3 border-t border-gray-200 bg-white px-6 py-3">
            <button
              onClick={handlePrevious}
              disabled={currentIndex <= 0}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Previous
            </button>

            <div className="flex-1 text-center text-xs text-gray-500">
              Read-only review mode
            </div>

            <button
              onClick={handleNext}
              disabled={currentIndex < 0 || currentIndex >= solutions.length - 1}
              className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>

        <ReviewPalette
          solutions={solutions}
          activeSection={activeSection}
          currentQno={currentQno}
          onNavigate={setCurrentQno}
          onSectionChange={setActiveSection}
        />
      </div>
    </div>
  );
}
