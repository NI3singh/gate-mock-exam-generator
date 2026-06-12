import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Background } from "../../components/Background";
import { COLORS, fontFamily } from "../../theme";
import { SHOTS } from "../config";
import { BrowserFrame, FRAME_HEADER_H } from "../components/BrowserFrame";
import { PagePan } from "../components/PagePan";
import { Callout } from "../components/Callout";

const FRAME_W = 1330;
const FRAME_H = 920;
const FRAME_X = (1920 - FRAME_W) / 2;

/** Scrolls through the entire landing page while feature callouts pop in
 * beside the window. */
export const LandingScroll: React.FC = () => {
  const frame = useCurrentFrame();
  const title = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${COLORS.bgTop}, ${COLORS.bgBottom})` }}>
      <Background />
      <AbsoluteFill style={{ alignItems: "center", fontFamily }}>
        <h2
          style={{
            margin: "38px 0 0",
            fontSize: 40,
            fontWeight: 800,
            letterSpacing: "-0.01em",
            color: COLORS.ink,
            opacity: title,
          }}
        >
          Everything you need — in one place
        </h2>
        <div style={{ marginTop: 24 }}>
          <BrowserFrame width={FRAME_W} height={FRAME_H} urlPath="" riseDelay={4}>
            <PagePan
              shot={SHOTS.landingFull.file}
              imgW={SHOTS.landingFull.w}
              imgH={SHOTS.landingFull.h}
              innerW={FRAME_W}
              innerH={FRAME_H - FRAME_HEADER_H}
              startHold={24}
              endHold={30}
            />
          </BrowserFrame>
        </div>
      </AbsoluteFill>

      {/* Floating feature callouts, timed to the scroll */}
      <Callout label="Full-length mocks" icon="📝" delay={34} x={FRAME_X - 210} y={300} />
      <Callout label="AI-generated questions" icon="🤖" delay={66} x={FRAME_X + FRAME_W - 110} y={420} />
      <Callout label="Authentic exam UI" icon="🖥️" delay={102} x={FRAME_X - 230} y={620} />
      <Callout label="Deep analytics" icon="📊" delay={138} x={FRAME_X + FRAME_W - 90} y={760} />
    </AbsoluteFill>
  );
};
