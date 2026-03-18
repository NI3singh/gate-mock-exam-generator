interface StatsCardProps {
  label: string;
  value: string;
  subtitle?: string;
  icon: React.ReactNode;
  color: "blue" | "green" | "purple" | "orange";
}

const colorMap = {
  blue: {
    bg: "bg-blue-50",
    icon: "text-blue-600",
    ring: "ring-blue-100",
  },
  green: {
    bg: "bg-green-50",
    icon: "text-green-600",
    ring: "ring-green-100",
  },
  purple: {
    bg: "bg-purple-50",
    icon: "text-purple-600",
    ring: "ring-purple-100",
  },
  orange: {
    bg: "bg-orange-50",
    icon: "text-orange-600",
    ring: "ring-orange-100",
  },
};

export default function StatsCard({
  label,
  value,
  subtitle,
  icon,
  color,
}: StatsCardProps) {
  const c = colorMap[color];

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs text-gray-400">{subtitle}</p>
          )}
        </div>
        <div
          className={`rounded-lg ${c.bg} p-3 ring-1 ${c.ring}`}
        >
          <div className={c.icon}>{icon}</div>
        </div>
      </div>
    </div>
  );
}