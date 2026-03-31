import { FormEvent, useEffect, useMemo, useState } from "react";
import katex from "katex";

import Navbar from "../components/layout/Navbar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import api from "../services/api";
import type {
  QuestionBankBrowserItem,
  QuestionBankBrowserResponse,
} from "../types";

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
    return <span dangerouslySetInnerHTML={{ __html: rendered }} />;
  }

  return <span className="whitespace-pre-wrap">{text}</span>;
}

type Filters = {
  paper: string;
  topic: string;
  difficulty: string;
  type: string;
};

const emptyFilters: Filters = {
  paper: "",
  topic: "",
  difficulty: "",
  type: "",
};

function formatCorrectAnswer(item: QuestionBankBrowserItem): string {
  if (item.question_type === "MCQ") {
    const index = Number(item.answer.index);
    return Number.isInteger(index) ? `Option ${String.fromCharCode(65 + index)}` : "N/A";
  }

  if (item.question_type === "MSQ") {
    const indices = Array.isArray(item.answer.indices) ? item.answer.indices : [];
    return indices.length
      ? `Options ${indices.map((index) => String.fromCharCode(65 + Number(index))).join(", ")}`
      : "N/A";
  }

  const value = item.answer.value;
  const tolerance = item.answer.tolerance;
  return tolerance !== undefined ? `${String(value)} (±${String(tolerance)})` : String(value ?? "N/A");
}

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function QuestionBankBrowser() {
  const [items, setItems] = useState<QuestionBankBrowserItem[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>(emptyFilters);
  const [draftFilters, setDraftFilters] = useState<Filters>(emptyFilters);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          page: String(page),
          page_size: "12",
        });

        if (filters.paper) params.set("paper", filters.paper);
        if (filters.topic.trim()) params.set("topic", filters.topic.trim());
        if (filters.difficulty) params.set("difficulty", filters.difficulty);
        if (filters.type) params.set("type", filters.type);

        const { data } = await api.get<QuestionBankBrowserResponse>(
          `/question-bank?${params.toString()}`
        );

        setItems(data.items);
        setTotalPages(data.total_pages);
        setTotal(data.total);
      } catch {
        setItems([]);
        setTotalPages(0);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [page, filters]);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    setPage(1);
    setFilters(draftFilters);
  };

  const resetFilters = () => {
    setDraftFilters(emptyFilters);
    setFilters(emptyFilters);
    setPage(1);
    setExpandedId(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="app-shell mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-700">
              Question Bank Browser
            </div>
            <h1 className="mt-3 text-3xl font-bold text-gray-900">
              Review Generated Questions
            </h1>
            <p className="mt-2 max-w-3xl text-gray-500">
              Filter the question bank by paper, topic, difficulty, and question type to inspect generated content quality.
            </p>
          </div>
          <div className="rounded-xl border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-800">
            {total} question{total === 1 ? "" : "s"} matched
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="mt-8 grid gap-4 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm md:grid-cols-5"
        >
          <select
            value={draftFilters.paper}
            onChange={(event) =>
              setDraftFilters((value) => ({ ...value, paper: event.target.value }))
            }
            className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-700"
          >
            <option value="">All Papers</option>
            <option value="CS">CS</option>
            <option value="DA">DA</option>
            <option value="GA">GA</option>
          </select>

          <input
            type="text"
            value={draftFilters.topic}
            onChange={(event) =>
              setDraftFilters((value) => ({ ...value, topic: event.target.value }))
            }
            placeholder="Filter by topic"
            className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-700"
          />

          <select
            value={draftFilters.difficulty}
            onChange={(event) =>
              setDraftFilters((value) => ({ ...value, difficulty: event.target.value }))
            }
            className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-700"
          >
            <option value="">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>

          <select
            value={draftFilters.type}
            onChange={(event) =>
              setDraftFilters((value) => ({ ...value, type: event.target.value }))
            }
            className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-700"
          >
            <option value="">All Types</option>
            <option value="MCQ">MCQ</option>
            <option value="MSQ">MSQ</option>
            <option value="NAT">NAT</option>
          </select>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
            >
              {loading ? "Applying..." : "Apply Filters"}
            </button>
            <button
              type="button"
              onClick={resetFilters}
              disabled={loading}
              className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50"
            >
              Reset
            </button>
          </div>
        </form>

        {loading ? (
          <div className="mt-10 flex justify-center rounded-2xl border border-gray-200 bg-white px-6 py-14 shadow-sm">
            <LoadingSpinner size="lg" text="LOADING QUESTION BANK" />
          </div>
        ) : items.length === 0 ? (
          <div className="mt-10 rounded-2xl border border-gray-200 bg-white px-6 py-12 text-center shadow-sm">
            <h2 className="text-xl font-semibold text-gray-900">No Questions Found</h2>
            <p className="mt-2 text-gray-500">
              Try adjusting the filters to browse more of the question bank.
            </p>
          </div>
        ) : (
          <div className="mt-10 space-y-5">
            {items.map((item) => {
              const expanded = expandedId === item.id;

              return (
                <div
                  key={item.id}
                  className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
                >
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-2">
                        <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
                          {item.paper}
                        </span>
                        <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-semibold text-purple-700">
                          {item.question_type}
                        </span>
                        <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-700">
                          {item.difficulty}
                        </span>
                        <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-semibold text-orange-700">
                          {item.marks} mark{item.marks > 1 ? "s" : ""}
                        </span>
                      </div>

                      <div>
                        <p className="text-sm font-semibold text-gray-900">
                          {item.topic}
                          <span className="ml-2 text-xs font-normal text-gray-500">
                            ({item.section_name})
                          </span>
                        </p>
                        <p className="mt-2 text-sm leading-7 text-gray-800">
                          <MathText text={item.stem_tex} />
                        </p>
                      </div>

                      <div className="text-xs text-gray-400">
                        Generated: {formatDate(item.generated_at)}
                      </div>
                    </div>

                    <button
                      onClick={() => setExpandedId(expanded ? null : item.id)}
                      className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
                    >
                      {expanded ? "Hide Solution" : "Show Solution"}
                    </button>
                  </div>

                  {expanded ? (
                    <div className="mt-6 space-y-4 border-t border-gray-100 pt-5">
                      {item.code_snippet ? (
                        <pre className="overflow-x-auto rounded-xl bg-gray-900 p-4 text-sm text-gray-100">
                          <code>{item.code_snippet}</code>
                        </pre>
                      ) : null}

                      {item.choices?.length ? (
                        <div className="space-y-2">
                          {item.choices.map((choice, index) => (
                            <div
                              key={`${item.id}-${index}`}
                              className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700"
                            >
                              <span className="mr-2 font-semibold text-gray-900">
                                {String.fromCharCode(65 + index)}.
                              </span>
                              <MathText text={choice} />
                            </div>
                          ))}
                        </div>
                      ) : null}

                      <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-900">
                        <span className="font-semibold">Correct Answer: </span>
                        {formatCorrectAnswer(item)}
                      </div>

                      <div className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-4">
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-blue-700">
                          Solution
                        </h3>
                        <div className="mt-3 text-sm leading-7 text-gray-800">
                          <MathText text={item.solution_tex} />
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-8 flex items-center justify-between">
          <button
            onClick={() => setPage((value) => Math.max(1, value - 1))}
            disabled={page <= 1}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-gray-500">
            Page {totalPages === 0 ? 0 : page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
            disabled={totalPages === 0 || page >= totalPages}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </main>
    </div>
  );
}
