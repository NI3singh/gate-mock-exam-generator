import type { TypesRatio } from "../../types";

interface Props {
  value: TypesRatio;
}

const types = [
  {
    key: "MCQ" as const,
    label: "MCQ",
    fullName: "Multiple Choice (single correct)",
    color: "bg-blue-500",
    lightBg: "bg-blue-50",
    text: "text-blue-700",
  },
  {
    key: "MSQ" as const,
    label: "MSQ",
    fullName: "Multiple Select (one or more correct)",
    color: "bg-purple-500",
    lightBg: "bg-purple-50",
    text: "text-purple-700",
  },
  {
    key: "NAT" as const,
    label: "NAT",
    fullName: "Numerical Answer Type",
    color: "bg-orange-500",
    lightBg: "bg-orange-50",
    text: "text-orange-700",
  },
];

export default function TypeRatioDisplay({ value }: Props) {
  return (
    <div>
      <label className="mb-3 block text-sm font-semibold text-gray-700">
        Question Type Ratio
      </label>

      {/* Visual bar */}
      <div className="mb-4 flex h-4 overflow-hidden rounded-full bg-gray-100">
        {types.map((t) => (
          <div
            key={t.key}
            className={`${t.color} transition-all`}
            style={{ width: `${value[t.key] * 100}%` }}
          />
        ))}
      </div>

      {/* Legend */}
      <div className="grid gap-3 sm:grid-cols-3">
        {types.map((t) => {
          const pct = Math.round(value[t.key] * 100);
          // Approximate question count out of 55 subject questions
          const approxCount = Math.round(value[t.key] * 55);

          return (
            <div
              key={t.key}
              className={`rounded-lg ${t.lightBg} p-3`}
            >
              <div className="flex items-center justify-between">
                <span className={`text-sm font-semibold ${t.text}`}>
                  {t.label}
                </span>
                <span className={`text-lg font-bold ${t.text}`}>{pct}%</span>
              </div>
              <p className="mt-1 text-xs text-gray-500">{t.fullName}</p>
              <p className="mt-0.5 text-xs text-gray-400">
                ~{approxCount} questions (subject section)
              </p>
            </div>
          );
        })}
      </div>

      <p className="mt-3 text-xs text-gray-400">
        Standard GATE distribution. GA section (10 Qs) is always MCQ. Ratio
        applies to the 55 subject questions only.
      </p>
    </div>
  );
}