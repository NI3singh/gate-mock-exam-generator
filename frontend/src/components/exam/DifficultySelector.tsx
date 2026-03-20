interface Props {
  value: "easy" | "medium" | "hard" | "auto";
  onChange: (difficulty: "easy" | "medium" | "hard" | "auto") => void;
}

const levels = [
  {
    code: "easy" as const,
    label: "Easy",
    desc: "Foundational concepts, straightforward problems",
    color: "green",
    icon: "🟢",
  },
  {
    code: "medium" as const,
    label: "Medium",
    desc: "Standard GATE difficulty, multi-step reasoning",
    color: "yellow",
    icon: "🟡",
  },
  {
    code: "hard" as const,
    label: "Hard",
    desc: "Challenging problems, deep conceptual understanding",
    color: "red",
    icon: "🔴",
  },
  {
    code: "auto" as const,
    label: "Auto (Mixed)",
    desc: "AI selects a realistic mix of difficulties",
    color: "blue",
    icon: "🔵",
  },
];

const borderMap: Record<string, string> = {
  green: "border-green-500 bg-green-50 ring-green-200",
  yellow: "border-yellow-500 bg-yellow-50 ring-yellow-200",
  red: "border-red-500 bg-red-50 ring-red-200",
  blue: "border-blue-500 bg-blue-50 ring-blue-200",
};

const textMap: Record<string, string> = {
  green: "text-green-700",
  yellow: "text-yellow-700",
  red: "text-red-700",
  blue: "text-blue-700",
};

export default function DifficultySelector({ value, onChange }: Props) {
  return (
    <div>
      <label className="mb-3 block text-sm font-semibold text-gray-700">
        Difficulty Level
      </label>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {levels.map((l) => {
          const selected = value === l.code;
          return (
            <button
              key={l.code}
              type="button"
              onClick={() => onChange(l.code)}
              className={`rounded-xl border-2 p-4 text-left transition-all ${
                selected
                  ? `${borderMap[l.color]} ring-1`
                  : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-lg">{l.icon}</span>
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
              <p
                className={`mt-2 font-semibold ${
                  selected ? textMap[l.color] : "text-gray-900"
                }`}
              >
                {l.label}
              </p>
              <p className="mt-1 text-xs text-gray-500">{l.desc}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}