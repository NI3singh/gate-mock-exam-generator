import { Composition } from "remotion";
import { Intro } from "./Intro";
import { FPS, TOTAL } from "./theme";
import { WebsiteTour } from "./tour/WebsiteTour";
import { TOUR_TOTAL } from "./tour/config";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Intro"
        component={Intro}
        durationInFrames={TOTAL}
        fps={FPS}
        width={1920}
        height={1080}
      />
      <Composition
        id="WebsiteTour"
        component={WebsiteTour}
        durationInFrames={TOUR_TOTAL}
        fps={FPS}
        width={1920}
        height={1080}
      />
    </>
  );
};
