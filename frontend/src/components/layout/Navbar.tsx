import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function Navbar() {
  const { firebaseUser, dbUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const isAuthenticated = Boolean(firebaseUser && dbUser);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const isActive = (path: string) => location.pathname === path;

  const navLinkClass = (path: string) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
      isActive(path)
        ? "bg-blue-50 text-blue-700"
        : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
    }`;

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* ── Logo ── */}
        <Link
          to={isAuthenticated ? "/dashboard" : "/"}
          className="flex items-center gap-2"
        >
          <span className="text-2xl">📝</span>
          <span className="text-xl font-bold text-gray-900">
            GATE&nbsp;<span className="text-blue-600">MockTest</span>
          </span>
        </Link>

        {/* ── Right side ── */}
        {isAuthenticated ? (
          <div className="flex items-center gap-2">
            {/* Nav links — hidden on small screens */}
            <div className="hidden items-center gap-1 sm:flex">
              <Link to="/dashboard" className={navLinkClass("/dashboard")}>
                Dashboard
              </Link>
              <Link
                to="/generate-exam"
                className={navLinkClass("/generate-exam")}
              >
                Generate Exam
              </Link>
              <Link to="/analytics" className={navLinkClass("/analytics")}>
                Analytics
              </Link>
            </div>

            {/* Divider */}
            <div className="mx-2 hidden h-6 w-px bg-gray-200 sm:block" />

            {/* User dropdown */}
            <div className="relative">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                {/* Avatar circle */}
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
                  {(
                    dbUser?.display_name?.[0] ||
                    dbUser?.email?.[0] ||
                    "U"
                  ).toUpperCase()}
                </div>
                <span className="hidden max-w-[120px] truncate sm:inline">
                  {dbUser?.display_name || dbUser?.email?.split("@")[0]}
                </span>
                <svg
                  className={`h-4 w-4 text-gray-400 transition-transform ${
                    menuOpen ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              {/* Dropdown menu */}
              {menuOpen && (
                <>
                  {/* Invisible overlay to close the menu */}
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setMenuOpen(false)}
                  />

                  <div className="absolute right-0 z-50 mt-2 w-56 rounded-xl border border-gray-200 bg-white py-1 shadow-lg">
                    {/* User info */}
                    <div className="border-b border-gray-100 px-4 py-3">
                      <p className="truncate text-sm font-medium text-gray-900">
                        {dbUser?.display_name || "Student"}
                      </p>
                      <p className="truncate text-xs text-gray-500">
                        {dbUser?.email}
                      </p>
                      {dbUser?.preferred_paper && (
                        <span className="mt-1 inline-block rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                          GATE {dbUser.preferred_paper}
                        </span>
                      )}
                    </div>

                    {/* Mobile-only nav links */}
                    <div className="border-b border-gray-100 py-1 sm:hidden">
                      <Link
                        to="/dashboard"
                        onClick={() => setMenuOpen(false)}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Dashboard
                      </Link>
                      <Link
                        to="/generate-exam"
                        onClick={() => setMenuOpen(false)}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Generate Exam
                      </Link>
                      <Link
                        to="/analytics"
                        onClick={() => setMenuOpen(false)}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Analytics
                      </Link>
                    </div>

                    {/* Logout */}
                    <div className="py-1">
                      <button
                        onClick={() => {
                          setMenuOpen(false);
                          handleLogout();
                        }}
                        className="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        <svg
                          className="h-4 w-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                          />
                        </svg>
                        Logout
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              Login
            </Link>
            <Link
              to="/signup"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Sign Up
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
