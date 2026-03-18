import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import LoadingSpinner from "../common/LoadingSpinner";

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
  const { firebaseUser, loading } = useAuth();

  if (loading) return <LoadingSpinner fullScreen />;
  if (!firebaseUser) return <Navigate to="/login" replace />;

  return <>{children}</>;
}