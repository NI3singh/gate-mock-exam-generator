# GATE Mock-Exam AI — Intro Video (Remotion)

A ~24-second branded intro/promo for the GATE Mock-Exam AI web portal, built with
[Remotion](https://www.remotion.dev). It reuses the product's identity: the M✓ logo
mark, Plus Jakarta Sans, the blue/indigo/sky palette, and the ambient drifting blobs.

## Scenes

1. **Logo reveal** — the M✓ mark draws itself in, wordmark settles.
2. **Headline** — “Master GATE 2027” with an animated gradient underline.
3. **Feature pillars** — Full-Length Mocks · AI-Generated · Authentic UI · Deep Analytics.
4. **Stats** — counting up 65 / 100 / 180 / ∞.
5. **Papers** — CS and DA cards slide in with topic tags.
6. **Call to action** — “Start practicing today.”

## Commands

```bash
npm install          # first time only
npm run dev          # open Remotion Studio to preview/scrub
npm run render       # render to out/intro.mp4 (1920×1080, 30fps)
npm run render:still # export a poster frame to out/poster.png
```

## Customizing

- Colors, fonts and scene lengths live in `src/theme.ts`.
- Each scene is an isolated component under `src/scenes/`.
- Background motion is in `src/components/Background.tsx`.

All motion is driven by `useCurrentFrame()` (no CSS animations), per Remotion best practice.
