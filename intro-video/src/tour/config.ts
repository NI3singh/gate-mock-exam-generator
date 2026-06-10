// Scene lengths (frames @ 30fps) for the WebsiteTour composition and the
// cross-transition length between scenes.
export const TOUR_SCENE = {
  intro: 95,
  hero: 185,
  scroll: 200,
  dashboard: 185,
  generate: 185,
  qbank: 165,
  analytics: 170,
  outro: 150,
} as const;

export const TOUR_TRANS = 16;

// 7 transitions overlap adjacent scenes, so subtract them from the sum.
export const TOUR_TOTAL =
  TOUR_SCENE.intro +
  TOUR_SCENE.hero +
  TOUR_SCENE.scroll +
  TOUR_SCENE.dashboard +
  TOUR_SCENE.generate +
  TOUR_SCENE.qbank +
  TOUR_SCENE.analytics +
  TOUR_SCENE.outro -
  7 * TOUR_TRANS;

// Real pixel dimensions of the captured screenshots (2x DPR), used to compute
// exact scroll distances inside the browser frame.
export const SHOTS = {
  landingTop: { file: "shots/landing-top.png", w: 3200, h: 2000 },
  landingFull: { file: "shots/landing.png", w: 3200, h: 5324 },
  dashboard: { file: "shots/dashboard.png", w: 3200, h: 3090 },
  generate: { file: "shots/generate-exam.png", w: 3200, h: 2716 },
  qbank: { file: "shots/question-bank.png", w: 3200, h: 6164 },
  analyticsTop: { file: "shots/analytics-top.png", w: 3200, h: 2000 },
} as const;
