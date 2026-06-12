import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Background } from "../../components/Background";
import { LogoMark } from "../../components/LogoMark";
import { COLORS, fontFamily, gradientText } from "../../theme";

const CHIPS = ["65 questions", "100 marks", "180 minutes", "Unlimited tests"];

/** Closing card: logo, call to action, fact chips. */
export const TourOutro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const title = spring({ frame: frame - 14, fps, config: { damping: 200 }, durationInFrames: 32 });
  const sub = interpolate(frame, [34, 54], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${COLORS.bgTop}, ${COLORS.bgBottom})` }}>
      <Background />
      <AbsoluteFill
        style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", fontFamily }}
      >
        <LogoMark size={190} showGate={false} />
        <h1
          style={{
            margin: 0,
            fontSize: 84,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            color: COLORS.ink,
            opacity: title,
            transform: `translateY(${(1 - title) * 30}px)`,
          }}
        >
          Start practicing <span style={gradientText}>today</span>.
        </h1>
        <p style={{ margin: "20px 0 0", fontSize: 27, color: COLORS.slate, opacity: sub }}>
          AI-powered GATE 2027 mock exams — built by aspirants, for aspirants.
        </p>
        <div style={{ display: "flex", gap: 18, marginTop: 44 }}>
          {CHIPS.map((chip, i) => {
            const pop = spring({
              frame: frame - 52 - i * 7,
              fps,
              config: { damping: 18, stiffness: 170 },
              durationInFrames: 30,
            });
            return (
              <div
                key={chip}
                style={{
                  background: "rgba(255,255,255,0.9)",
                  border: "1px solid rgba(37,99,235,0.18)",
                  boxShadow: "0 10px 28px rgba(37,99,235,0.10)",
                  borderRadius: 999,
                  padding: "13px 28px",
                  fontSize: 22,
                  fontWeight: 700,
                  color: COLORS.blueDark,
                  opacity: Math.min(1, pop * 1.2),
                  transform: `translateY(${(1 - pop) * 22}px) scale(${0.85 + pop * 0.15})`,
                }}
              >
                {chip}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
