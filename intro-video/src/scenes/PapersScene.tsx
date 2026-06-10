import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../theme";

type Paper = { code: string; title: string; tags: string[]; fromX: number; delay: number };

const PAPERS: Paper[] = [
  {
    code: "CS",
    title: "Computer Science & IT",
    tags: ["DSA", "OS", "DBMS", "CN", "TOC", "COA"],
    fromX: -90,
    delay: 6,
  },
  {
    code: "DA",
    title: "Data Science & AI",
    tags: ["ML", "AI", "Probability", "Python", "DBMS", "LA"],
    fromX: 90,
    delay: 12,
  },
];

const PaperCard: React.FC<{ paper: Paper }> = ({ paper }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - paper.delay, fps, config: { damping: 18, stiffness: 110 } });
  const x = interpolate(s, [0, 1], [paper.fromX, 0]);

  return (
    <div
      style={{
        width: 520,
        opacity: s,
        transform: `translateX(${x}px)`,
        background: `linear-gradient(160deg, ${COLORS.white} 0%, #f4f7ff 100%)`,
        border: `1px solid ${COLORS.line}`,
        borderRadius: 30,
        padding: 44,
        boxShadow: "0 30px 60px -34px rgba(37,99,235,0.4)",
      }}
    >
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          width: 88,
          height: 88,
          borderRadius: 22,
          background: COLORS.blue,
          color: COLORS.white,
          fontSize: 40,
          fontWeight: 800,
          letterSpacing: "0.04em",
          boxShadow: "0 14px 30px -12px rgba(37,99,235,0.7)",
        }}
      >
        {paper.code}
      </div>
      <div style={{ marginTop: 28, fontSize: 36, fontWeight: 800, color: COLORS.ink }}>
        {paper.title}
      </div>
      <div style={{ marginTop: 22, display: "flex", flexWrap: "wrap", gap: 12 }}>
        {paper.tags.map((tag) => (
          <span
            key={tag}
            style={{
              padding: "8px 18px",
              borderRadius: 999,
              background: "#eef3ff",
              color: COLORS.blueDark,
              fontSize: 19,
              fontWeight: 600,
            }}
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
};

export const PapersScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleIn = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 24 });

  return (
    <AbsoluteFill
      style={{ alignItems: "center", justifyContent: "center", flexDirection: "column" }}
    >
      <div
        style={{
          opacity: titleIn,
          transform: `translateY(${interpolate(titleIn, [0, 1], [-16, 0])}px)`,
          fontSize: 46,
          fontWeight: 800,
          color: COLORS.ink,
          letterSpacing: "-0.02em",
          marginBottom: 50,
        }}
      >
        Two papers. <span style={{ color: COLORS.blue }}>Full syllabus.</span>
      </div>
      <div style={{ display: "flex", gap: 40 }}>
        {PAPERS.map((p) => (
          <PaperCard key={p.code} paper={p} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
