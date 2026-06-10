import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../theme";

type Feature = { icon: string; title: string; desc: string };

const FEATURES: Feature[] = [
  { icon: "📄", title: "Full-Length Mocks", desc: "65 questions · 100 marks · 180 minutes — the exact GATE pattern." },
  { icon: "🤖", title: "AI-Generated", desc: "Fresh, original, syllabus-aware questions every single time." },
  { icon: "🖥️", title: "Authentic UI", desc: "Palette, section tabs, mark-for-review and a real countdown timer." },
  { icon: "📊", title: "Deep Analytics", desc: "Topic-wise accuracy, score trends and weak-area insights." },
];

const Card: React.FC<{ feature: Feature; index: number }> = ({ feature, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - 16 - index * 7,
    fps,
    config: { damping: 16, stiffness: 130 },
  });
  const y = interpolate(s, [0, 1], [60, 0]);

  return (
    <div
      style={{
        width: 360,
        opacity: s,
        transform: `translateY(${y}px)`,
        background: COLORS.white,
        border: `1px solid ${COLORS.line}`,
        borderRadius: 26,
        padding: 32,
        boxShadow: "0 24px 50px -28px rgba(37,99,235,0.35)",
      }}
    >
      <div
        style={{
          width: 72,
          height: 72,
          borderRadius: 18,
          background: "#eff5ff",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 36,
        }}
      >
        {feature.icon}
      </div>
      <div style={{ marginTop: 22, fontSize: 26, fontWeight: 700, color: COLORS.ink }}>
        {feature.title}
      </div>
      <div style={{ marginTop: 12, fontSize: 17, lineHeight: 1.55, color: COLORS.slate }}>
        {feature.desc}
      </div>
    </div>
  );
};

export const FeaturesScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleIn = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 26 });

  return (
    <AbsoluteFill
      style={{ alignItems: "center", justifyContent: "center", flexDirection: "column" }}
    >
      <div
        style={{
          opacity: titleIn,
          transform: `translateY(${interpolate(titleIn, [0, 1], [-18, 0])}px)`,
          fontSize: 46,
          fontWeight: 800,
          color: COLORS.ink,
          letterSpacing: "-0.02em",
          marginBottom: 48,
        }}
      >
        Everything you need to <span style={{ color: COLORS.blue }}>ace GATE</span>
      </div>

      <div style={{ display: "flex", gap: 28, justifyContent: "center" }}>
        {FEATURES.map((f, i) => (
          <Card key={f.title} feature={f} index={i} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
