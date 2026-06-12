/**
 * AmbientBackground
 *
 * A fixed, non-interactive layer that sits behind all page content and renders
 * a few softly drifting, blurred blue blobs over the base canvas tint. Mounted
 * once at the app root; pages whose wrappers are transparent reveal it.
 *
 * Intentionally subtle — low opacity + heavy blur — so it adds life without
 * competing with foreground UI. Honors prefers-reduced-motion via CSS.
 */
export default function AmbientBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      <div className="animate-blob absolute -left-32 -top-32 h-[480px] w-[480px] rounded-full bg-blue-200 opacity-30 blur-3xl" />
      <div className="animate-blob-slow absolute -right-24 top-1/4 h-[420px] w-[420px] rounded-full bg-indigo-200 opacity-25 blur-3xl" />
      <div className="animate-blob absolute bottom-[-10rem] left-1/3 h-[440px] w-[440px] rounded-full bg-sky-200 opacity-25 blur-3xl anim-delay-300" />
    </div>
  );
}
