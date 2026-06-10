import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Background } from "../../components/Background";
import { COLORS, fontFamily, gradientText } from "../../theme";
import { SHOTS } from "../config";
import { BrowserFrame, FRAME_HEADER_H } from "../components/BrowserFrame";
import { PagePan } from "../components/PagePan";

const FRAME_W = 1500;
const FRAME_H = 850;

/** First look: the real landing page inside a browser window, with a short
 * headline above. */
export const HeroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const title = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 30 });
  const sub = interpolate(frame, [16, 38], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${COLORS.bgTop}, ${COLORS.bgBottom})` }}>
      <Background />
      <AbsoluteFill style={{ alignItems: "center", fontFamily }}>
        <h2
          style={{
            margin: "64px 0 0",
            fontSize: 52,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            color: COLORS.ink,
            opacity: title,
            transform: `translateY(${(1 - title) * 24}px)`,
          }}
        >
          Meet your <span style={gradientText}>GATE 2027</span> prep platform
        </h2>
        <p style={{ margin: "12px 0 0", fontSize: 24, color: COLORS.slate, opacity: sub }}>
          Full-length AI-generated mock exams for CS &amp; DA — in the real exam interface.
        </p>
        <div style={{ marginTop: 34 }}>
          <BrowserFrame width={FRAME_W} height={FRAME_H} urlPath="" riseDelay={10}>
            <PagePan
              shot={SHOTS.landingTop.file}
              imgW={SHOTS.landingTop.w}
              imgH={SHOTS.landingTop.h}
              innerW={FRAME_W}
              innerH={FRAME_H - FRAME_HEADER_H}
            />
          </BrowserFrame>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
