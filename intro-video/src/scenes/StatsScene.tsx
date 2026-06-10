import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, gradientText } from "../theme";
import { Counter } from "../components/Counter";

type Stat = { value: React.ReactNode; label: string };

export const StatsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleIn = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 24 });

  const stats: Stat[] = [
    { value: <Counter to={65} duration={70} delay={14} />, label: "Questions" },
    { value: <Counter to={100} duration={70} delay={18} />, label: "Marks" },
    { value: <Counter to={180} duration={70} delay={22} />, label: "Minutes" },
    { value: "∞", label: "Mock Tests" },
  ];

  return (
    <AbsoluteFill
      style={{ alignItems: "center", justifyContent: "center", flexDirection: "column" }}
    >
      <div
        style={{
          opacity: titleIn,
          transform: `translateY(${interpolate(titleIn, [0, 1], [-16, 0])}px)`,
          fontSize: 40,
          fontWeight: 700,
          color: COLORS.slate,
          marginBottom: 56,
        }}
      >
        Built to mirror the <span style={{ color: COLORS.ink, fontWeight: 800 }}>real exam</span>
      </div>

      <div style={{ display: "flex", gap: 96, justifyContent: "center", alignItems: "flex-start" }}>
        {stats.map((s, i) => {
          const cellIn = spring({
            frame: frame - 8 - i * 6,
            fps,
            config: { damping: 18, stiffness: 120 },
          });
          return (
            <div
              key={s.label}
              style={{
                textAlign: "center",
                opacity: cellIn,
                transform: `scale(${interpolate(cellIn, [0, 1], [0.7, 1])})`,
              }}
            >
              <div style={{ fontSize: 128, fontWeight: 800, lineHeight: 1, ...gradientText }}>
                {s.value}
              </div>
              <div
                style={{
                  marginTop: 16,
                  fontSize: 24,
                  fontWeight: 600,
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                  color: COLORS.muted,
                }}
              >
                {s.label}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
