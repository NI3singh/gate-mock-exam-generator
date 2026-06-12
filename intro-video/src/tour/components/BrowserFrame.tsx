import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, fontFamily } from "../../theme";

const HEADER_H = 56;

/**
 * A clean macOS-style browser window. Children render inside the viewport
 * area (width × height-56), clipped by the rounded corners. The whole window
 * rises in with a soft spring.
 */
export const BrowserFrame: React.FC<{
  width: number;
  height: number;
  urlPath?: string;
  riseDelay?: number;
  children: React.ReactNode;
}> = ({ width, height, urlPath = "", riseDelay = 0, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const rise = spring({
    frame: frame - riseDelay,
    fps,
    config: { damping: 200 },
    durationInFrames: 34,
  });

  return (
    <div
      style={{
        width,
        height,
        borderRadius: 18,
        background: COLORS.white,
        boxShadow:
          "0 40px 90px rgba(15,23,42,0.18), 0 12px 30px rgba(37,99,235,0.10)",
        border: "1px solid rgba(15,23,42,0.08)",
        overflow: "hidden",
        opacity: rise,
        transform: `translateY(${(1 - rise) * 90}px)`,
      }}
    >
      {/* Title bar */}
      <div
        style={{
          height: HEADER_H,
          display: "flex",
          alignItems: "center",
          padding: "0 22px",
          gap: 9,
          background: "linear-gradient(180deg, #fbfcff, #f3f6fd)",
          borderBottom: "1px solid rgba(15,23,42,0.07)",
        }}
      >
        <div style={{ width: 13, height: 13, borderRadius: "50%", background: "#ff5f57" }} />
        <div style={{ width: 13, height: 13, borderRadius: "50%", background: "#febc2e" }} />
        <div style={{ width: 13, height: 13, borderRadius: "50%", background: "#28c840" }} />
        {/* Address pill */}
        <div
          style={{
            margin: "0 auto",
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: COLORS.white,
            border: "1px solid rgba(15,23,42,0.09)",
            borderRadius: 999,
            padding: "7px 18px",
            minWidth: 380,
            justifyContent: "center",
          }}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
            <rect x="4" y="10" width="16" height="11" rx="2.5" fill={COLORS.slate} opacity={0.55} />
            <path
              d="M8 10V7a4 4 0 0 1 8 0v3"
              stroke={COLORS.slate}
              strokeWidth="2.4"
              opacity={0.55}
            />
          </svg>
          <span
            style={{
              fontFamily,
              fontSize: 16,
              fontWeight: 500,
              color: COLORS.slate,
              letterSpacing: 0.2,
            }}
          >
            mockexam.ai
            <span style={{ color: COLORS.muted }}>{urlPath}</span>
          </span>
        </div>
        {/* spacer to balance the traffic lights */}
        <div style={{ width: 57 }} />
      </div>
      {/* Viewport */}
      <div style={{ width, height: height - HEADER_H, overflow: "hidden", position: "relative" }}>
        {children}
      </div>
    </div>
  );
};

export const FRAME_HEADER_H = HEADER_H;
