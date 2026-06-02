import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import api, { getApiErrorMessage } from "../../services/api";
import type { TopicFlat, TopicListResponse } from "../../types";
import LoadingSpinner from "../common/LoadingSpinner";

interface Props {
  paper: "CS" | "DA";
  selected: string[];
  onChange: (topics: string[]) => void;
}

export default function TopicPicker({ paper, selected, onChange }: Props) {
  const [topics, setTopics] = useState<TopicFlat[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const fetchTopics = async () => {
      setLoading(true);
      try {
        const { data } = await api.get<TopicListResponse>(
          `/syllabus/${paper}/topics`,
          { suppressErrorToast: true }
        );
        setTopics(data.topics);
      } catch (error) {
        toast.error(
          getApiErrorMessage(
            error,
            `Failed to load topics for ${paper}. Make sure syllabus data is loaded.`
          )
        );
        setTopics([]);
      } finally {
        setLoading(false);
      }
    };
    fetchTopics();
  }, [paper]);

  // Group topics by section
  const grouped: Record<string, TopicFlat[]> = {};
  for (const t of topics) {
    if (!grouped[t.section_name]) grouped[t.section_name] = [];
    grouped[t.section_name].push(t);
  }

  // Filter by search
  const filteredGrouped: Record<string, TopicFlat[]> = {};
  const q = searchQuery.toLowerCase().trim();
  for (const [section, items] of Object.entries(grouped)) {
    const filtered = q
      ? items.filter(
          (t) =>
            t.topic.toLowerCase().includes(q) ||
            section.toLowerCase().includes(q)
        )
      : items;
    if (filtered.length > 0) filteredGrouped[section] = filtered;
  }

  const toggle = (topic: string) => {
    if (selected.includes(topic)) {
      onChange(selected.filter((t) => t !== topic));
    } else {
      onChange([...selected, topic]);
    }
  };

  const toggleSection = (sectionTopics: TopicFlat[]) => {
    const sectionNames = sectionTopics.map((t) => t.topic);
    const allSelected = sectionNames.every((t) => selected.includes(t));

    if (allSelected) {
      onChange(selected.filter((t) => !sectionNames.includes(t)));
    } else {
      const merged = new Set([...selected, ...sectionNames]);
      onChange(Array.from(merged));
    }
  };

  const selectAll = () => {
    onChange(topics.map((t) => t.topic));
  };

  const clearAll = () => {
    onChange([]);
  };

  if (loading) return <LoadingSpinner size="sm" />;

  if (topics.length === 0) {
    return (
      <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-700">
        No topics are available for {paper} yet. Please try again later or
        contact support if this persists.
      </div>
    );
  }

  return (
    <div>
      <label className="mb-3 block text-sm font-semibold text-gray-700">
        Select Topics ({selected.length} of {topics.length} selected)
      </label>

      {/* Search + bulk actions */}
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <input
          type="text"
          placeholder="Search topics..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:max-w-xs"
        />
        <div className="flex gap-2">
          <button
            type="button"
            onClick={selectAll}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
          >
            Select All
          </button>
          <button
            type="button"
            onClick={clearAll}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
          >
            Clear All
          </button>
        </div>
      </div>

      {/* Sections and topics */}
      <div className="max-h-[400px] space-y-4 overflow-y-auto rounded-lg border border-gray-200 bg-white p-4">
        {Object.entries(filteredGrouped).map(([section, items]) => {
          const sectionNames = items.map((t) => t.topic);
          const allSelected = sectionNames.every((t) => selected.includes(t));
          const someSelected =
            !allSelected && sectionNames.some((t) => selected.includes(t));

          return (
            <div key={section}>
              {/* Section header */}
              <div className="mb-2 flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el) => {
                    if (el) el.indeterminate = someSelected;
                  }}
                  onChange={() => toggleSection(items)}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-semibold text-gray-800">
                  {section}
                </span>
                <span className="text-xs text-gray-400">
                  ({items.length} topics)
                </span>
              </div>

              {/* Topics grid */}
              <div className="ml-6 grid gap-1.5 sm:grid-cols-2">
                {items.map((t) => (
                  <label
                    key={t.id}
                    className={`flex cursor-pointer items-center gap-2 rounded-lg px-3 py-1.5 text-sm transition-colors ${
                      selected.includes(t.topic)
                        ? "bg-blue-50 text-blue-700"
                        : "text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selected.includes(t.topic)}
                      onChange={() => toggle(t.topic)}
                      className="h-3.5 w-3.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="truncate">{t.topic}</span>
                  </label>
                ))}
              </div>
            </div>
          );
        })}

        {Object.keys(filteredGrouped).length === 0 && (
          <p className="py-4 text-center text-sm text-gray-400">
            No topics match "{searchQuery}"
          </p>
        )}
      </div>
    </div>
  );
}
