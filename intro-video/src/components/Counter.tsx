import { Easing, interpolate, useCurrentFrame } from "remotion";

/** Counts up from 0 to `to` over `duration` frames, eased out. */
export const Counter: React.FC<{
  to: number;
  duration: number;
  delay?: number;
  suffix?: string;
}> = ({ to, duration, delay = 0, suffix = "" }) => {
  const frame = useCurrentFrame();
  const value = interpolate(frame - delay, [0, duration], [0, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <>
      {Math.round(value)}
      {suffix}
    </>
  );
};
