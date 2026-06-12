import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, gradientText } from "../theme";

const Word: React.FC<{
  children: React.ReactNode;
  delay: number;
  style?: React.CSSProperties;
}> = ({ children, delay, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 28 });
  const y = interpolate(s, [0, 1], [46, 0]);
  return (
    <span
      style={{ display: "inline-block", opacity: s, transform: `translateY(${y}px)`, ...style }}
    >
      {children}
    </span>
  );
};

export const HeadlineScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const underline = spring({
    frame: frame - 46,
    fps,
    config: { damping: 200 },
    durationInFrames: 26,
  });

  const subIn = spring({
    frame: frame - 58,
    fps,
    config: { damping: 200 },
    durationInFrames: 28,
  });

  return (
    <AbsoluteFill
      style={{ alignItems: "center", justifyContent: "center", flexDirection: "column" }}
    >
      <div
        style={{
          fontSize: 116,
          fontWeight: 800,
          letterSpacing: "-0.03em",
          lineHeight: 1.05,
          textAlign: "center",
        }}
      >
        <Word delay={0} style={{ color: COLORS.ink }}>
          Master&nbsp;
        </Word>
        <span style={{ position: "relative", display: "inline-block" }}>
          <Word delay={10} style={gradientText}>
            GATE&nbsp;2027
          </Word>
          <div
            style={{
              position: "absolute",
              left: 6,
              right: 6,
              bottom: -4,
              height: 8,
              borderRadius: 8,
              transformOrigin: "left center",
              transform: `scaleX(${underline})`,
              background: `linear-gradient(90deg, ${COLORS.blue}, ${COLORS.blueLight})`,
              opacity: 0.85,
            }}
          />
        </span>
      </div>

      <div
        style={{
          marginTop: 40,
          maxWidth: 1080,
          textAlign: "center",
          fontSize: 32,
          fontWeight: 500,
          lineHeight: 1.5,
          color: COLORS.slate,
          opacity: subIn,
          transform: `translateY(${interpolate(subIn, [0, 1], [20, 0])}px)`,
        }}
      >
        AI-powered, full-length mock tests for{" "}
        <span style={{ color: COLORS.ink, fontWeight: 700 }}>Computer Science</span> and{" "}
        <span style={{ color: COLORS.ink, fontWeight: 700 }}>Data Science &amp; AI</span>.
      </div>
    </AbsoluteFill>
  );
};
