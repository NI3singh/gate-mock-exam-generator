// frontend/src/components/common/LoadingSpinner.tsx

import React from "react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg" | "xl";
  showText?: boolean;
  text?: string;
  fullPage?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = "md",
  showText = true,
  text,
  fullPage = false,
}) => {
  const cfg = {
    sm:  { dim: 40,  textCls: "text-xs",   gap: "gap-2" },
    md:  { dim: 64,  textCls: "text-sm",   gap: "gap-3" },
    lg:  { dim: 100, textCls: "text-base", gap: "gap-4" },
    xl:  { dim: 140, textCls: "text-lg",   gap: "gap-5" },
  };
  const { dim, textCls, gap } = cfg[size];
  const label = text ?? "Loading";

  const R = 44;
  const C = 2 * Math.PI * R;
  const arc = +(C * 0.26).toFixed(2);
  const space = +(C - arc).toFixed(2);

  const spinner = (
    <div className={`flex flex-col items-center justify-center ${gap}`}>
      <style>{css}</style>

      <div className="relative" style={{ width: dim, height: dim }}>

        {/* ① Light track ring */}
        <svg className="absolute inset-0" viewBox="0 0 100 100" fill="none">
          <circle cx="50" cy="50" r={R} stroke="#E5E7EB" strokeWidth="2.5" />
        </svg>

        {/* ② Rotating arc */}
        <svg className="absolute inset-0 mx-spin" viewBox="0 0 100 100" fill="none">
          <circle
            cx="50"
            cy="50"
            r={R}
            stroke="#2563EB"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeDasharray={`${arc} ${space}`}
          />
        </svg>

        {/* ③ M✓ logo mark + GATE text (centered, breathing) */}
        <svg className="absolute inset-0 mx-breathe" viewBox="0 0 100 100" fill="none">
          {/* M✓ mark */}
          <path
            d="M 22,60 L 37,22 L 50,46 L 63,22 L 71,40 L 82,18"
            stroke="#1E40AF"
            strokeWidth="4.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* GATE text (Georgia serif) */}
          <text
            x="50"
            y="80"
            textAnchor="middle"
            fill="#1E40AF"
            fontSize="14"
            fontWeight="700"
            fontFamily="'Georgia', 'Palatino Linotype', 'Book Antiqua', serif"
            letterSpacing="0.2em"
          >
            GATE  
          </text>
        </svg>
      </div>

      {/* ④ Animated loading text with dots */}
      {showText && (
        <p
          className={`
            font-semibold tracking-[0.25em] uppercase select-none
            text-gray-400 ${textCls}
          `}
        >
          {label}
          <span className="mx-dot" style={{ animationDelay: "0s" }}>.</span>
          <span className="mx-dot" style={{ animationDelay: "0.2s" }}>.</span>
          <span className="mx-dot" style={{ animationDelay: "0.4s" }}>.</span>
        </p>
      )}
    </div>
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/90 backdrop-blur-sm">
        {spinner}
      </div>
    );
  }

  return spinner;
};

const css = `
  .mx-spin {
    animation: mx-rotate 1.1s linear infinite;
  }
  @keyframes mx-rotate {
    to { transform: rotate(360deg); }
  }

  .mx-breathe {
    animation: mx-breathe-kf 2.4s ease-in-out infinite;
  }
  @keyframes mx-breathe-kf {
    0%, 100% { opacity: 0.55; transform: scale(1);    }
    50%      { opacity: 1;    transform: scale(1.05); }
  }

  .mx-dot {
    display: inline-block;
    animation: mx-dot-kf 1.4s ease-in-out infinite;
    opacity: 0;
  }
  @keyframes mx-dot-kf {
    0%, 60%, 100% { opacity: 0; transform: translateY(0);    }
    30%           { opacity: 1; transform: translateY(-2px); }
  }
`;

export default LoadingSpinner;