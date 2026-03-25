import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/layout/ProtectedRoute";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import GenerateExam from "./pages/GenerateExam";
import ExamProgress from "./pages/ExamProgress";
import ExamScreen from "./pages/ExamScreen";
import ResultScreen from "./pages/ResultScreen";
import Analytics from "./pages/Analytics";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: { background: "#363636", color: "#fff" },
          }}
        />

        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/generate-exam"
            element={
              <ProtectedRoute>
                <GenerateExam />
              </ProtectedRoute>
            }
          />
          <Route
            path="/exam/:examId/progress"
            element={
              <ProtectedRoute>
                <ExamProgress />
              </ProtectedRoute>
            }
          />
          {/* Part 8: Exam Screen */}
          <Route
            path="/exam/:examId"
            element={
              <ProtectedRoute>
                <ExamScreen />
              </ProtectedRoute>
            }
          />
          {/* Part 10: Result Screen */}
          <Route
            path="/result/:attemptId"
            element={
              <ProtectedRoute>
                <ResultScreen />
              </ProtectedRoute>
            }
          />
          {/* Part 11: Solutions (same screen, modal via ?solutions param) */}
          <Route
            path="/result/:attemptId/solutions"
            element={
              <ProtectedRoute>
                <ResultScreen />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;