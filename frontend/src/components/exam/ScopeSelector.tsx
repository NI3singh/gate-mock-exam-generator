interface Props {
  value: "full" | "topic";
  onChange: (scope: "full" | "topic") => void;
}

const scopes = [
  {
    code: "full" as const,
    name: "Full Syllabus",
    desc: "Questions from all sections — mimics the real GATE exam.",
    icon: "📚",
  },
  {
    code: "topic" as const,
    name: "Select Topics",
    desc: "Choose specific topics to focus your practice session.",
    icon: "🎯",
  },
];

export default function ScopeSelector({ value, onChange }: Props) {
  return (
    <div>
      <label className="mb-3 block text-sm font-semibold text-gray-700">
        Exam Scope
      </label>
      <div className="grid gap-4 sm:grid-cols-2">
        {scopes.map((s) => {
          const selected = value === s.code;
          return (
            <button
              key={s.code}
              type="button"
              onClick={() => onChange(s.code)}
              className={`flex items-start gap-3 rounded-xl border-2 p-4 text-left transition-all ${
                selected
                  ? "border-blue-600 bg-blue-50 ring-1 ring-blue-200"
                  : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
              }`}
            >
              <span className="text-2xl">{s.icon}</span>
              <div className="flex-1">
                <p
                  className={`font-semibold ${
                    selected ? "text-blue-700" : "text-gray-900"
                  }`}
                >
                  {s.name}
                </p>
                <p className="mt-0.5 text-xs text-gray-500">{s.desc}</p>
              </div>
              <div className="mt-0.5">
                <div
                  className={`flex h-5 w-5 items-center justify-center rounded-full border-2 ${
                    selected
                      ? "border-blue-600 bg-blue-600"
                      : "border-gray-300"
                  }`}
                >
                  {selected && (
                    <div className="h-2 w-2 rounded-full bg-white" />
                  )}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}