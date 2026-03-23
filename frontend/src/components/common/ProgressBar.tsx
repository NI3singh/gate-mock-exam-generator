interface Props {
  value: number; // 0–100
  color?: "blue" | "green" | "red" | "yellow";
  size?: "sm" | "md" | "lg";
  animate?: boolean;
}

const colorMap = {
  blue: "bg-blue-600",
  green: "bg-green-500",
  red: "bg-red-500",
  yellow: "bg-yellow-500",
};

const trackMap = {
  blue: "bg-blue-100",
  green: "bg-green-100",
  red: "bg-red-100",
  yellow: "bg-yellow-100",
};

const sizeMap = {
  sm: "h-2",
  md: "h-3",
  lg: "h-4",
};

export default function ProgressBar({
  value,
  color = "blue",
  size = "md",
  animate = true,
}: Props) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div className={`w-full overflow-hidden rounded-full ${trackMap[color]} ${sizeMap[size]}`}>
      <div
        className={`${sizeMap[size]} rounded-full ${colorMap[color]} transition-all duration-500 ease-out ${
          animate && clamped < 100 ? "animate-pulse" : ""
        }`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}