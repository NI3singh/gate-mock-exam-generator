interface Props {
  value: "CS" | "DA";
  onChange: (paper: "CS" | "DA") => void;
}

const papers = [
  {
    code: "CS" as const,
    name: "Computer Science & IT",
    sections: "13 sections · ~140 topics",
    icon: "💻",
  },
  {
    code: "DA" as const,
    name: "Data Science & AI",
    sections: "7 sections · ~110 topics",
    icon: "🤖",
  },
];

export default function PaperSelector({ value, onChange }: Props) {
  return (
    <div>
      <label className="mb-3 block text-sm font-semibold text-gray-700">
        Select Paper
      </label>
      <div className="grid gap-4 sm:grid-cols-2">
        {papers.map((p) => {
          const selected = value === p.code;
          return (
            <button
              key={p.code}
              type="button"
              onClick={() => onChange(p.code)}
              className={`flex items-start gap-4 rounded-xl border-2 p-5 text-left transition-all ${
                selected
                  ? "border-blue-600 bg-blue-50 ring-1 ring-blue-200"
                  : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
              }`}
            >
              <span className="text-3xl">{p.icon}</span>
              <div>
                <p
                  className={`text-base font-semibold ${
                    selected ? "text-blue-700" : "text-gray-900"
                  }`}
                >
                  GATE {p.code}
                </p>
                <p className="mt-0.5 text-sm text-gray-500">{p.name}</p>
                <p className="mt-1 text-xs text-gray-400">{p.sections}</p>
              </div>

              {/* Radio indicator */}
              <div className="ml-auto mt-1">
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