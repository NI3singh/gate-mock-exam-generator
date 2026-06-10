import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../theme";
import { LogoMark } from "../components/LogoMark";

export const LogoScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({ frame, fps, config: { damping: 13, stiffness: 110 } });

  const wordIn = spring({
    frame: frame - 40,
    fps,
    config: { damping: 200 },
    durationInFrames: 30,
  });
  const wordY = interpolate(wordIn, [0, 1], [26, 0]);

  return (
    <AbsoluteFill
      style={{ alignItems: "center", justifyContent: "center", flexDirection: "column" }}
    >
      <div style={{ transform: `scale(${0.8 + pop * 0.2})`, opacity: pop }}>
        <LogoMark size={300} />
      </div>

      <div
        style={{
          marginTop: 28,
          opacity: wordIn,
          transform: `translateY(${wordY}px)`,
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: 76, fontWeight: 800, color: COLORS.ink, letterSpacing: "-0.02em" }}>
          Mock-Exam <span style={{ color: COLORS.blue }}>AI</span>
        </div>
        <div
          style={{
            marginTop: 10,
            fontSize: 22,
            fontWeight: 600,
            letterSpacing: "0.42em",
            textTransform: "uppercase",
            color: COLORS.muted,
          }}
        >
          for GATE 2027
        </div>
      </div>
    </AbsoluteFill>
  );
};
