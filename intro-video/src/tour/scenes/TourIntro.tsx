import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Background } from "../../components/Background";
import { LogoMark } from "../../components/LogoMark";
import { COLORS, fontFamily, gradientText } from "../../theme";

/** Opening card: logo draws on, wordmark + "platform tour" kicker settle in. */
export const TourIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const word = spring({ frame: frame - 22, fps, config: { damping: 200 }, durationInFrames: 32 });
  const kicker = interpolate(frame, [44, 64], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${COLORS.bgTop}, ${COLORS.bgBottom})` }}>
      <Background />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          fontFamily,
        }}
      >
        <LogoMark size={230} showGate={false} />
        <h1
          style={{
            margin: "6px 0 0",
            fontSize: 76,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            color: COLORS.ink,
            opacity: word,
            transform: `translateY(${(1 - word) * 30}px)`,
          }}
        >
          Mock-Exam <span style={gradientText}>AI</span>
        </h1>
        <p
          style={{
            margin: "22px 0 0",
            fontSize: 24,
            fontWeight: 700,
            letterSpacing: "0.34em",
            color: COLORS.muted,
            opacity: kicker,
          }}
        >
          A&nbsp;TOUR&nbsp;OF&nbsp;THE&nbsp;PLATFORM
        </p>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
