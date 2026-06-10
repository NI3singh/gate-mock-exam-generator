import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../theme";

/**
 * The M✓ brand mark from the website's Logo component, animated:
 * the stroke draws itself on, then "GATE" fades in beneath it.
 */
export const LogoMark: React.FC<{ size?: number; showGate?: boolean; delay?: number }> = ({
  size = 320,
  showGate = true,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const draw = spring({
    frame: frame - delay,
    fps,
    config: { damping: 200 },
    durationInFrames: 42,
  });

  const gate = interpolate(frame - delay, [34, 56], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      style={{ filter: "drop-shadow(0 12px 28px rgba(37,99,235,0.25))" }}
    >
      <path
        d="M 12,58 L 27,20 L 40,44 L 53,20 L 61,38 L 72,16"
        stroke={COLORS.blueDarker}
        strokeWidth={6}
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - draw}
      />
      {showGate && (
        <text
          x="42"
          y="84"
          textAnchor="middle"
          fill={COLORS.blueDarker}
          fontSize="18"
          fontWeight={800}
          fontFamily="Georgia, 'Times New Roman', serif"
          letterSpacing="0.18em"
          opacity={gate}
        >
          GATE
        </text>
      )}
    </svg>
  );
};
