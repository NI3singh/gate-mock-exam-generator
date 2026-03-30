import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import LoadingSpinner from "../common/LoadingSpinner";

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
  const { firebaseUser, dbUser, loading } = useAuth();

  if (loading) return <LoadingSpinner fullScreen />;
  if (!firebaseUser || !dbUser) return <Navigate to="/login" replace />;

  return <>{children}</>;
}
