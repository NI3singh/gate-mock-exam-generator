import { loadFont } from "@remotion/google-fonts/PlusJakartaSans";
import type React from "react";

// Same typeface as the website (Plus Jakarta Sans). Blocks render until ready.
export const { fontFamily } = loadFont("normal", {
  weights: ["400", "500", "600", "700", "800"],
  subsets: ["latin"],
});

// Palette lifted from the app's Tailwind config / Landing page.
export const COLORS = {
  blue: "#2563eb", // blue-600 (brand)
  blueLight: "#3b82f6", // blue-500
  blueDark: "#1d4ed8", // blue-700
  blueDarker: "#1e40af", // blue-800 (logo mark)
  indigo: "#6366f1",
  sky: "#0ea5e9",
  ink: "#0f172a", // slate-900
  slate: "#475569", // slate-600
  muted: "#94a3b8", // slate-400
  line: "#e7eeff",
  bgTop: "#ffffff",
  bgBottom: "#eef3ff",
  white: "#ffffff",
};

export const FPS = 30;

// Scene lengths (frames @ 30fps) and the cross-fade length between them.
export const SCENE = {
  logo: 110,
  headline: 115,
  features: 175,
  stats: 135,
  papers: 115,
  cta: 150,
} as const;

export const TRANS = 16;

// 5 transitions overlap adjacent scenes, so subtract them from the sum.
export const TOTAL =
  SCENE.logo +
  SCENE.headline +
  SCENE.features +
  SCENE.stats +
  SCENE.papers +
  SCENE.cta -
  5 * TRANS;

// Reusable gradient-text style (blue-600 → blue-500), Chromium-safe.
export const gradientText: React.CSSProperties = {
  backgroundImage: `linear-gradient(90deg, ${COLORS.blue}, ${COLORS.blueLight})`,
  WebkitBackgroundClip: "text",
  backgroundClip: "text",
  WebkitTextFillColor: "transparent",
  color: "transparent",
};
