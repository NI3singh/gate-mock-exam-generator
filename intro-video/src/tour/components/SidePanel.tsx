import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, fontFamily, gradientText } from "../../theme";

const Reveal: React.FC<{ delay: number; children: React.ReactNode }> = ({ delay, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 30 });
  return (
    <div style={{ opacity: p, transform: `translateY(${(1 - p) * 26}px)` }}>{children}</div>
  );
};

/** Left-hand text column used by every app scene: kicker chip, headline,
 * check-marked bullets — all spring-staggered. */
export const SidePanel: React.FC<{
  kicker: string;
  title: string;
  highlight?: string;
  bullets: string[];
}> = ({ kicker, title, highlight, bullets }) => {
  const frame = useCurrentFrame();
  const lineGrow = interpolate(frame, [8, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        width: 560,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "0 30px 0 96px",
        fontFamily,
      }}
    >
      <Reveal delay={4}>
        <div
          style={{
            display: "inline-flex",
            alignSelf: "flex-start",
            alignItems: "center",
            gap: 10,
            background: "rgba(37,99,235,0.08)",
            border: "1px solid rgba(37,99,235,0.18)",
            borderRadius: 999,
            padding: "8px 18px",
          }}
        >
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: COLORS.blue }} />
          <span
            style={{
              fontSize: 17,
              fontWeight: 700,
              letterSpacing: "0.16em",
              color: COLORS.blueDark,
            }}
          >
            {kicker}
          </span>
        </div>
      </Reveal>

      <Reveal delay={10}>
        <h2
          style={{
            margin: "26px 0 0",
            fontSize: 58,
            lineHeight: 1.08,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            color: COLORS.ink,
          }}
        >
          {title}
          {highlight ? (
            <>
              {" "}
              <span style={gradientText}>{highlight}</span>
            </>
          ) : null}
        </h2>
      </Reveal>

      <div
        style={{
          height: 4,
          width: 96 * lineGrow,
          borderRadius: 2,
          margin: "26px 0 8px",
          background: `linear-gradient(90deg, ${COLORS.blue}, ${COLORS.sky})`,
        }}
      />

      <div style={{ marginTop: 18, display: "flex", flexDirection: "column", gap: 18 }}>
        {bullets.map((b, i) => (
          <Reveal key={b} delay={26 + i * 9}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
              <svg width="26" height="26" viewBox="0 0 24 24" style={{ flexShrink: 0, marginTop: 2 }}>
                <circle cx="12" cy="12" r="11" fill="rgba(37,99,235,0.10)" />
                <path
                  d="M7 12.5l3.2 3.2L17 9"
                  stroke={COLORS.blue}
                  strokeWidth="2.6"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
              </svg>
              <span style={{ fontSize: 24, lineHeight: 1.45, color: COLORS.slate, fontWeight: 500 }}>
                {b}
              </span>
            </div>
          </Reveal>
        ))}
      </div>
    </div>
  );
};
