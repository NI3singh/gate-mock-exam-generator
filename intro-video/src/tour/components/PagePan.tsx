import {
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/**
 * Renders a captured page screenshot inside a fixed viewport and animates it.
 *
 * - Pages taller than the viewport: a smooth eased scroll from top to bottom
 *   (like a person browsing), with a hold at both ends.
 * - Pages that fit: a slow Ken Burns push-in instead.
 *
 * imgW/imgH are the real pixel dimensions of the PNG, so the scroll distance
 * is exact — no guessing, no over/under-scroll.
 */
export const PagePan: React.FC<{
  shot: string;
  imgW: number;
  imgH: number;
  innerW: number;
  innerH: number;
  startHold?: number;
  endHold?: number;
}> = ({ shot, imgW, imgH, innerW, innerH, startHold = 20, endHold = 28 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const renderedH = (innerW * imgH) / imgW;
  const maxScroll = Math.max(0, renderedH - innerH);

  const progress = interpolate(
    frame,
    [startHold, durationInFrames - endHold],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    }
  );

  let transform: string;
  if (maxScroll > 0) {
    transform = `translateY(${-maxScroll * progress}px)`;
  } else {
    // Page fits — slow push-in. Base scale guarantees full coverage.
    const cover = Math.max(1, innerH / renderedH) + 0.04;
    const scale = cover + progress * 0.07;
    transform = `translateY(${-progress * 14}px) scale(${scale})`;
  }

  return (
    <div style={{ width: innerW, height: innerH, overflow: "hidden", position: "relative" }}>
      <Img
        src={staticFile(shot)}
        style={{
          width: innerW,
          display: "block",
          transform,
          transformOrigin: "50% 0%",
        }}
      />
    </div>
  );
};
