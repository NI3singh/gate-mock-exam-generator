import { AbsoluteFill } from "remotion";
import { Background } from "../../components/Background";
import { COLORS, fontFamily } from "../../theme";
import { BrowserFrame, FRAME_HEADER_H } from "../components/BrowserFrame";
import { PagePan } from "../components/PagePan";
import { SidePanel } from "../components/SidePanel";

const FRAME_W = 1190;
const FRAME_H = 870;

/** Generic app-page scene: text panel on the left, the live page scrolling
 * inside a browser window on the right. */
export const AppScene: React.FC<{
  shot: string;
  imgW: number;
  imgH: number;
  urlPath: string;
  kicker: string;
  title: string;
  highlight?: string;
  bullets: string[];
}> = ({ shot, imgW, imgH, urlPath, kicker, title, highlight, bullets }) => {
  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${COLORS.bgTop}, ${COLORS.bgBottom})` }}>
      <Background />
      <AbsoluteFill style={{ flexDirection: "row", fontFamily }}>
        <SidePanel kicker={kicker} title={title} highlight={highlight} bullets={bullets} />
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            paddingRight: 64,
          }}
        >
          <BrowserFrame width={FRAME_W} height={FRAME_H} urlPath={urlPath} riseDelay={6}>
            <PagePan
              shot={shot}
              imgW={imgW}
              imgH={imgH}
              innerW={FRAME_W}
              innerH={FRAME_H - FRAME_HEADER_H}
            />
          </BrowserFrame>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
