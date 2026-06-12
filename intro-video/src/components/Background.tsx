import { AbsoluteFill, useCurrentFrame } from "remotion";
import { COLORS } from "../theme";

type BlobProps = {
  color: string;
  size: number;
  baseX: number;
  baseY: number;
  ax: number;
  ay: number;
  speed: number;
  phase: number;
  opacity: number;
};

const Blob: React.FC<BlobProps> = ({
  color,
  size,
  baseX,
  baseY,
  ax,
  ay,
  speed,
  phase,
  opacity,
}) => {
  const frame = useCurrentFrame();
  const t = frame / speed + phase;
  // Deterministic, frame-driven drift (no CSS animation).
  const x = baseX + Math.sin(t) * ax;
  const y = baseY + Math.cos(t * 0.8) * ay;
  const scale = 1 + Math.sin(t * 0.6) * 0.06;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: size,
        height: size,
        borderRadius: "50%",
        background: color,
        filter: "blur(100px)",
        opacity,
        transform: `scale(${scale})`,
      }}
    />
  );
};

export const Background: React.FC = () => {
  return (
    <AbsoluteFill>
      {/* Soft drifting colour blobs */}
      <Blob color={COLORS.blue} size={620} baseX={-160} baseY={-180} ax={40} ay={30} speed={70} phase={0} opacity={0.18} />
      <Blob color={COLORS.indigo} size={560} baseX={1280} baseY={120} ax={50} ay={36} speed={85} phase={2} opacity={0.16} />
      <Blob color={COLORS.sky} size={520} baseX={620} baseY={620} ax={46} ay={28} speed={95} phase={4} opacity={0.16} />
      <Blob color={COLORS.blueLight} size={420} baseX={1180} baseY={640} ax={34} ay={24} speed={110} phase={1} opacity={0.14} />

      {/* Faint grid, like the Landing page */}
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(rgba(37,99,235,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(37,99,235,0.05) 1px, transparent 1px)`,
          backgroundSize: "52px 52px",
        }}
      />

      {/* Centre vignette to keep focus on the content */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 50% 46%, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 42%, rgba(238,243,255,0.65) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};
