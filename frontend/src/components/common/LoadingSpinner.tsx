interface Props {
  fullScreen?: boolean;
  size?: "sm" | "md" | "lg";
}

export default function LoadingSpinner({
  fullScreen = false,
  size = "md",
}: Props) {
  const dims = { sm: "h-6 w-6", md: "h-10 w-10", lg: "h-16 w-16" }[size];

  const spinner = (
    <div
      className={`${dims} animate-spin rounded-full border-4 border-gray-300 border-t-blue-600`}
    />
  );

  if (fullScreen) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-50">
        {spinner}
      </div>
    );
  }

  return <div className="flex items-center justify-center py-12">{spinner}</div>;
}