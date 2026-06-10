import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, gradientText } from "../theme";
import { LogoMark } from "../components/LogoMark";

export const CtaScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const kicker = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 22 });
  const title = spring({ frame: frame - 10, fps, config: { damping: 200 }, durationInFrames: 28 });
  const button = spring({ frame: frame - 28, fps, config: { damping: 14, stiffness: 120 } });
  const lockup = spring({ frame: frame - 44, fps, config: { damping: 200 }, durationInFrames: 28 });

  // Gentle continuous breathing on the button arrow.
  const arrow = Math.sin(frame / 9) * 6;

  return (
    <AbsoluteFill
      style={{ alignItems: "center", justifyContent: "center", flexDirection: "column" }}
    >
      <div
        style={{
          opacity: kicker,
          fontSize: 22,
          fontWeight: 700,
          letterSpacing: "0.4em",
          textTransform: "uppercase",
          color: COLORS.blue,
          marginBottom: 26,
        }}
      >
        Your GATE prep, reimagined
      </div>

      <div
        style={{
          opacity: title,
          transform: `translateY(${interpolate(title, [0, 1], [28, 0])}px)`,
          fontSize: 92,
          fontWeight: 800,
          letterSpacing: "-0.03em",
          textAlign: "center",
          lineHeight: 1.06,
          color: COLORS.ink,
        }}
      >
        Start practicing <span style={gradientText}>today</span>.
      </div>

      <div
        style={{
          marginTop: 48,
          opacity: button,
          transform: `scale(${interpolate(button, [0, 1], [0.8, 1])})`,
          display: "inline-flex",
          alignItems: "center",
          gap: 14,
          padding: "22px 46px",
          borderRadius: 16,
          background: COLORS.blue,
          color: COLORS.white,
          fontSize: 28,
          fontWeight: 700,
          boxShadow: "0 24px 50px -18px rgba(37,99,235,0.65)",
        }}
      >
        Get Started — It's Free
        <span style={{ display: "inline-block", transform: `translateX(${arrow}px)` }}>→</span>
      </div>

      <div
        style={{
          marginTop: 70,
          opacity: lockup,
          display: "flex",
          alignItems: "center",
          gap: 16,
        }}
      >
        <LogoMark size={70} showGate={false} delay={44} />
        <div style={{ fontSize: 30, fontWeight: 800, color: COLORS.ink }}>
          Mock-Exam <span style={{ color: COLORS.blue }}>AI</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
