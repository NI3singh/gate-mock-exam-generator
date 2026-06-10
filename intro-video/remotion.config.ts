import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// High-quality output: full color range, crisp text.
Config.setChromiumOpenGlRenderer("angle");
