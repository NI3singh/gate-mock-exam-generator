import { AbsoluteFill } from "remotion";
import {
  TransitionSeries,
  linearTiming,
  springTiming,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";

import { COLORS, SCENE, TRANS, fontFamily } from "./theme";
import { Background } from "./components/Background";
import { LogoScene } from "./scenes/LogoScene";
import { HeadlineScene } from "./scenes/HeadlineScene";
import { FeaturesScene } from "./scenes/FeaturesScene";
import { StatsScene } from "./scenes/StatsScene";
import { PapersScene } from "./scenes/PapersScene";
import { CtaScene } from "./scenes/CtaScene";

export const Intro: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        fontFamily,
        background: `linear-gradient(180deg, ${COLORS.bgTop} 0%, ${COLORS.bgBottom} 100%)`,
      }}
    >
      {/* Persistent ambient layer — drifts continuously beneath every scene,
          echoing the AmbientBackground used across the live site. */}
      <Background />

      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={SCENE.logo}>
          <LogoScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={springTiming({ config: { damping: 200 }, durationInFrames: TRANS })}
        />

        <TransitionSeries.Sequence durationInFrames={SCENE.headline}>
          <HeadlineScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANS })}
        />

        <TransitionSeries.Sequence durationInFrames={SCENE.features}>
          <FeaturesScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANS })}
        />

        <TransitionSeries.Sequence durationInFrames={SCENE.stats}>
          <StatsScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANS })}
        />

        <TransitionSeries.Sequence durationInFrames={SCENE.papers}>
          <PapersScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={springTiming({ config: { damping: 200 }, durationInFrames: TRANS })}
        />

        <TransitionSeries.Sequence durationInFrames={SCENE.cta}>
          <CtaScene />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
