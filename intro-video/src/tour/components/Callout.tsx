import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, fontFamily } from "../../theme";

/** A floating annotation card that pops in beside the browser frame and
 * gently bobs while visible. */
export const Callout: React.FC<{
  label: string;
  icon: string;
  delay: number;
  x: number;
  y: number;
}> = ({ label, icon, delay, x, y }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({
    frame: frame - delay,
    fps,
    config: { damping: 16, stiffness: 160 },
    durationInFrames: 34,
  });
  const bob = Math.sin((frame - delay) / 26) * 5;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        display: "flex",
        alignItems: "center",
        gap: 12,
        background: "rgba(255,255,255,0.94)",
        border: "1px solid rgba(37,99,235,0.16)",
        boxShadow: "0 18px 44px rgba(15,23,42,0.16)",
        borderRadius: 16,
        padding: "14px 22px",
        fontFamily,
        opacity: Math.min(1, pop * 1.2),
        transform: `translateY(${(1 - pop) * 24 + bob}px) scale(${0.8 + pop * 0.2})`,
      }}
    >
      <span style={{ fontSize: 24 }}>{icon}</span>
      <span style={{ fontSize: 22, fontWeight: 700, color: COLORS.ink, whiteSpace: "nowrap" }}>
        {label}
      </span>
    </div>
  );
};
