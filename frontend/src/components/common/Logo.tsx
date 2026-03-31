// frontend/src/components/common/Logo.tsx

import React from "react";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  showName?: boolean;
}

const Logo: React.FC<LogoProps> = ({ size = "md", showName = true }) => {
  const cfg = {
    sm: { dim: 28, nameCls: "text-base" },
    md: { dim: 36, nameCls: "text-lg" },
    lg: { dim: 48, nameCls: "text-2xl" },
  };
  const { dim, nameCls } = cfg[size];

  return (
    <div className="flex items-center gap-2 select-none">
      {/* Logo mark with GATE */}
      <svg
        viewBox="0 0 100 100"
        width={dim}
        height={dim}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M 12,58 L 27,20 L 40,44 L 53,20 L 61,38 L 72,16"
          stroke="#1E40AF"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <text
          x="42"
          y="82"
          textAnchor="middle"
          fill="#1E40AF"
          fontSize="20"
          fontWeight="700"
          fontFamily="Georgia, serif"
          letterSpacing="0.15em"
        >
          GATE
        </text>
      </svg>

      {/* Site name text */}
      {showName && (
        <div className="flex flex-col leading-tight">
            <span className={`font-bold text-gray-900 ${nameCls}`}>
            Mock-Exam <span className="text-blue-600">AI</span>
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-[0.35em] text-gray-400">
            for GATE
            </span>
        </div>
        )}
    </div>
  );
};

export default Logo;