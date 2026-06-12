import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { SHOTS, TOUR_SCENE, TOUR_TRANS } from "./config";
import { TourIntro } from "./scenes/TourIntro";
import { HeroScene } from "./scenes/HeroScene";
import { LandingScroll } from "./scenes/LandingScroll";
import { AppScene } from "./scenes/AppScene";
import { TourOutro } from "./scenes/TourOutro";

const timing = linearTiming({ durationInFrames: TOUR_TRANS });

/**
 * WebsiteTour — a professional walkthrough of the live product, built from
 * real screenshots of localhost:5173 (see capture/capture.mjs).
 */
export const WebsiteTour: React.FC = () => {
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={TOUR_SCENE.intro}>
        <TourIntro />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition presentation={fade()} timing={timing} />

      <TransitionSeries.Sequence durationInFrames={TOUR_SCENE.hero}>
        <HeroScene />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition presentation={fade()} timing={timing} />

      <TransitionSeries.Sequence durationInFrames={TOUR_SCENE.scroll}>
        <LandingScroll />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />

      <TransitionSeries.Sequence durationInFrames={TOUR_SCENE.dashboard}>
        <AppScene
          shot={SHOTS.dashboard.file}
          imgW={SHOTS.dashboard.w}
          imgH={SHOTS.dashboard.h}
          urlPath="/dashboard"
          kicker="DASHBOARD"
          title="Every attempt,"
          highlight="tracked."
          bullets={[
            "Resume in-progress exams exactly where you left off",
            "Scores, history and bests — at a glance",
          ]}
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />

      <TransitionSeries.Sequence durationInFrames={TOUR_SCENE.generate}>
        <AppScene
          shot={SHOTS.generate.file}
          imgW={SHOTS.generate.w}
          imgH={SHOTS.generate.h}
          urlPath="/generate-exam"
          kicker="EXAM GENERATOR"
          title="Your paper,"
          highlight="your rules."
          bullets={[
            "GATE CS or DA — full syllabus or hand-picked topics",
            "AI assembles a real 65-question, 100-mark paper",
          ]}
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />

      <TransitionSeries.Sequence durationInFrames={TOUR_SCENE.qbank}>
        <AppScene
          shot={SHOTS.qbank.file}
          imgW={SHOTS.qbank.w}
          imgH={SHOTS.qbank.h}
          urlPath="/question-bank"
          kicker="QUESTION BANK"
          title="Hundreds of questions,"
          highlight="with solutions."
          bullets={[
            "Filter by paper, topic, difficulty and type",
            "Step-by-step solutions for every question",
          ]}
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />

      <TransitionSeries.Sequence durationInFrames={TOUR_SCENE.analytics}>
        <AppScene
          shot={SHOTS.analyticsTop.file}
          imgW={SHOTS.analyticsTop.w}
          imgH={SHOTS.analyticsTop.h}
          urlPath="/analytics"
          kicker="ANALYTICS"
          title="Know your weak topics"
          highlight="before the exam does."
          bullets={[
            "Score trend across every attempt",
            "Topic-wise accuracy, strongest to weakest",
          ]}
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition presentation={fade()} timing={timing} />

      <TransitionSeries.Sequence durationInFrames={TOUR_SCENE.outro}>
        <TourOutro />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
