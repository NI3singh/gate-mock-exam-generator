### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\syllabus.py
*Saved at: 3/20/2026, 3:25:08 PM*

**[REMOVED]**
```
(from line ~1)
from sqlalchemy import Text, func, 

```
**[ADDED]**
```
1     from sqlalchemy import Text, func, String
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\syllabus.py
*Saved at: 3/20/2026, 3:25:06 PM*

**[REMOVED]**
```
(from line ~1)
from sqlalchemy import Text, func

```
**[ADDED]**
```
1     from sqlalchemy import Text, func, 
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\syllabus.py
*Saved at: 3/20/2026, 3:24:58 PM*

**[REMOVED]**
```
(from line ~13)
    section_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subtopic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)

```
**[ADDED]**
```
13        section_name: Mapped[str] = mapped_column(Text(), nullable=False, index=True)
14        topic: Mapped[str] = mapped_column(Text(), nullable=False, index=True)
15        subtopic: Mapped[str | None] = mapped_column(Text(), nullable=True)
16        source_file: Mapped[str | None] = mapped_column(Text(), nullable=True)
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\syllabus.py
*Saved at: 3/20/2026, 3:24:55 PM*

**[REMOVED]**
```
(from line ~13)
    section_name: Mapped[str] = mapped_column(Text(), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(Text(), nullable=False, index=True)
    subtopic: Mapped[str | None] = mapped_column(Text(), nullable=True)
    source_file: Mapped[str | None] = mapped_column(Text(), nullable=True)

```
**[ADDED]**
```
13        section_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
14        topic: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
15        subtopic: Mapped[str | None] = mapped_column(String(255), nullable=True)
16        source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\syllabus.py
*Saved at: 3/20/2026, 3:24:51 PM*

**[REMOVED]**
```
(from line ~1)
from sqlalchemy import String, func

```
**[ADDED]**
```
1     from sqlalchemy import Text, func
```
**[REMOVED]**
```
(from line ~13)
    section_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subtopic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)

```
**[ADDED]**
```
13        section_name: Mapped[str] = mapped_column(Text(), nullable=False, index=True)
14        topic: Mapped[str] = mapped_column(Text(), nullable=False, index=True)
15        subtopic: Mapped[str | None] = mapped_column(Text(), nullable=True)
16        source_file: Mapped[str | None] = mapped_column(Text(), nullable=True)
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\syllabus.py
*Saved at: 3/20/2026, 3:24:47 PM*

**[REMOVED]**
```
(from line ~1)
from sqlalchemy import Text, func

```
**[ADDED]**
```
1     from sqlalchemy import String, func
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\syllabus.py
*Saved at: 3/20/2026, 3:24:44 PM*

**[REMOVED]**
```
(from line ~1)
from sqlalchemy import String, func

```
**[ADDED]**
```
1     from sqlalchemy import Text, func
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\main.py
*Saved at: 3/20/2026, 1:49:18 PM*

**[REMOVED]**
```
(from line ~30)
    # 3. Auto-load syllabus data on startup
    try:
        async with AsyncSessionLocal() as session:
            result = await load_syllabus(session)
            if result.errors:
                print(f"⚠️ Syllabus auto-load completed with errors: {result.errors}")
            else:
                print(
                    f"✅ Syllabus auto-loaded successfully "
                    f"({result.total_rows_inserted} rows, papers: {', '.join(result.papers_loaded)})"
                )
    except Exception as e:
        print(f"❌ Syllabus auto-load failed: {e}")
        raise

```
**[ADDED]**
```
30        
```
**[REMOVED]**
```
(from line ~34)
    yield


```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\main.py
*Saved at: 3/20/2026, 1:48:50 PM*

**[ADDED]**
```
30        # 3. Auto-load syllabus data on startup
31        try:
32            async with AsyncSessionLocal() as session:
33                result = await load_syllabus(session)
34                if result.errors:
35                    print(f"⚠️ Syllabus auto-load completed with errors: {result.errors}")
36                else:
37                    print(
38                        f"✅ Syllabus auto-loaded successfully "
39                        f"({result.total_rows_inserted} rows, papers: {', '.join(result.papers_loaded)})"
40                    )
41        except Exception as e:
42            print(f"❌ Syllabus auto-load failed: {e}")
43            raise
44    
```
**[ADDED]**
```
47        yield
48    
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\main.py
*Saved at: 3/20/2026, 1:48:02 PM*

**[REMOVED]**
```
(from line ~8)
from app.core.database import engine

```
**[ADDED]**
```
8     from app.core.database import engine,  AsyncSessionLocal
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\main.py
*Saved at: 3/20/2026, 1:47:47 PM*

**[ADDED]**
```
11    from app.services.data_loader import load_syllabus
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\pages\ExamProgress.tsx
*Saved at: 3/20/2026, 12:34:15 PM*

**[ADDED]**
```
1     import { useParams, Link } from "react-router-dom";
2     import Navbar from "../components/layout/Navbar";
3     
4     export default function ExamProgress() {
5       const { examId } = useParams<{ examId: string }>();
6     
7       return (
8         <div className="min-h-screen bg-gray-50">
9           <Navbar />
10    
11          <main className="mx-auto max-w-2xl px-4 py-16 text-center sm:px-6 lg:px-8">
12            <div className="rounded-xl border border-gray-200 bg-white p-12 shadow-sm">
13              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-blue-50">
14                <span className="text-3xl">⏳</span>
15              </div>
16    
17              <h1 className="mt-6 text-2xl font-bold text-gray-900">
18                Exam Generation In Progress
19              </h1>
20              <p className="mx-auto mt-3 max-w-md text-gray-500">
21                AI is generating your exam questions. This page will show a live
22                progress bar in the next module.
23              </p>
24    
25              <div className="mt-4 rounded-lg bg-gray-50 p-3">
26                <p className="text-xs text-gray-400">
27                  Exam ID: <code className="text-gray-600">{examId}</code>
28                </p>
29              </div>
30    
31              <div className="mt-8 flex justify-center gap-3">
32                <Link
33                  to="/dashboard"
34                  className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
35                >
36                  ← Back to Dashboard
37                </Link>
38              </div>
39            </div>
40          </main>
41        </div>
42      );
43    }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\App.tsx
*Saved at: 3/20/2026, 12:33:56 PM*

**[REMOVED]**
```
(from line ~1)
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

```
**[ADDED]**
```
1     import { BrowserRouter, Routes, Route } from "react-router-dom";
2     import { Toaster } from "react-hot-toast";
```
**[REMOVED]**
```
(from line ~4)
import { useAuth } from "../hooks/useAuth";
import api from "../services/api";
import type { ExamConfig, ExamGenerateResponse } from "../types";

```
**[ADDED]**
```
4     import { AuthProvider } from "./contexts/AuthContext";
5     import ProtectedRoute from "./components/layout/ProtectedRoute";
```
**[REMOVED]**
```
(from line ~7)
import Navbar from "../components/layout/Navbar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import PaperSelector from "../components/exam/PaperSelector";
import ScopeSelector from "../components/exam/ScopeSelector";
import TopicPicker from "../components/exam/TopicPicker";
import DifficultySelector from "../components/exam/DifficultySelector";
import TypeRatioDisplay from "../components/exam/TypeRatioDisplay";

```
**[ADDED]**
```
7     import Landing from "./pages/Landing";
8     import Login from "./pages/Login";
9     import Signup from "./pages/Signup";
10    import ForgotPassword from "./pages/ForgotPassword";
11    import Dashboard from "./pages/Dashboard";
12    import GenerateExam from "./pages/GenerateExam";
13    import ExamProgress from "./pages/ExamProgress";
14    import Analytics from "./pages/Analytics";
```
**[REMOVED]**
```
(from line ~16)
const DEFAULT_CONFIG: ExamConfig = {
  paper: "CS",
  scope: "full",
  selected_topics: [],
  difficulty: "auto",
  types_ratio: { MCQ: 0.6, MSQ: 0.2, NAT: 0.2 },
};

export default function GenerateExam() {
  const { dbUser } = useAuth();
  const navigate = useNavigate();

  const [config, setConfig] = useState<ExamConfig>(() => ({
    ...DEFAULT_CONFIG,
    paper: dbUser?.preferred_paper || "CS",
  }));
  const [submitting, setSubmitting] = useState(false);

  if (!dbUser) return <LoadingSpinner fullScreen />;

  const updateConfig = <K extends keyof ExamConfig>(
    key: K,
    value: ExamConfig[K]
  ) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const handlePaperChange = (paper: "CS" | "DA") => {
    setConfig((prev) => ({
      ...prev,
      paper,
      selected_topics: [], // Reset topics when paper changes
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // ── Client-side validation ──
    if (config.scope === "topic" && config.selected_topics.length === 0) {
      toast.error("Please select at least one topic.");
      return;
    }

    setSubmitting(true);
    try {
      const { data } = await api.post<ExamGenerateResponse>(
        "/exams/generate",
        {
          paper: config.paper,
          scope: config.scope,
          selected_topics:
            config.scope === "topic" ? config.selected_topics : null,
          difficulty: config.difficulty,
          types_ratio: config.types_ratio,
        }
      );

      toast.success("Exam configuration saved!");

      // Navigate to progress page (Part 7 — placeholder for now)
      navigate(`/exam/${data.exam_id}/progress`);
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail || "Failed to create exam. Please try again.";
      toast.error(detail);
    } finally {
      setSubmitting(false);
    }
  };


```
**[ADDED]**
```
16    function App() {
```
**[REMOVED]**
```
(from line ~18)
    <div className="min-h-screen bg-gray-50">
      <Navbar />

```
**[ADDED]**
```
18        <BrowserRouter>
19          <AuthProvider>
20            <Toaster
21              position="top-right"
22              toastOptions={{
23                duration: 4000,
24                style: { background: "#363636", color: "#fff" },
25              }}
26            />
```
**[REMOVED]**
```
(from line ~28)
      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
            Generate New Mock Test
          </h1>
          <p className="mt-2 text-gray-500">
            Configure your GATE 2026 mock exam. Each test follows the official
            pattern: 65 questions, 100 marks, 3 hours.
          </p>
        </div>

```
**[ADDED]**
```
28            <Routes>
29              {/* Public routes */}
30              <Route path="/" element={<Landing />} />
31              <Route path="/login" element={<Login />} />
32              <Route path="/signup" element={<Signup />} />
33              <Route path="/forgot-password" element={<ForgotPassword />} />
```
**[REMOVED]**
```
(from line ~35)
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* ── Card 1: Paper Selection ── */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <PaperSelector value={config.paper} onChange={handlePaperChange} />
          </div>

          {/* ── Card 2: Scope ── */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <ScopeSelector
              value={config.scope}
              onChange={(scope) => updateConfig("scope", scope)}
            />

            {/* Topic picker — shown only when scope is "topic" */}
            {config.scope === "topic" && (
              <div className="mt-6 border-t border-gray-100 pt-6">
                <TopicPicker
                  paper={config.paper}
                  selected={config.selected_topics}
                  onChange={(topics) =>
                    updateConfig("selected_topics", topics)
                  }
                />
              </div>
            )}
          </div>

          {/* ── Card 3: Difficulty ── */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <DifficultySelector
              value={config.difficulty}
              onChange={(d) => updateConfig("difficulty", d)}
            />
          </div>

          {/* ── Card 4: Question Type Ratio ── */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <TypeRatioDisplay value={config.types_ratio} />
          </div>

          {/* ── Exam Summary ── */}
          <div className="rounded-xl border border-blue-100 bg-blue-50 p-6">
            <h3 className="text-sm font-semibold text-blue-900">
              Exam Summary
            </h3>
            <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
              <div>
                <span className="text-blue-600">Paper:</span>{" "}
                <span className="font-medium text-blue-900">
                  {config.paper}
                </span>
              </div>
              <div>
                <span className="text-blue-600">Questions:</span>{" "}
                <span className="font-medium text-blue-900">65</span>
              </div>
              <div>
                <span className="text-blue-600">Marks:</span>{" "}
                <span className="font-medium text-blue-900">100</span>
              </div>
              <div>
                <span className="text-blue-600">Duration:</span>{" "}
                <span className="font-medium text-blue-900">3 hours</span>
              </div>
              <div>
                <span className="text-blue-600">Scope:</span>{" "}
                <span className="font-medium text-blue-900">
                  {config.scope === "full"
                    ? "Full Syllabus"
                    : `${config.selected_topics.length} topic(s)`}
                </span>
              </div>
              <div>
                <span className="text-blue-600">Difficulty:</span>{" "}
                <span className="font-medium capitalize text-blue-900">
                  {config.difficulty}
                </span>
              </div>
              <div>
                <span className="text-blue-600">GA Section:</span>{" "}
                <span className="font-medium text-blue-900">
                  10 Qs (15 marks)
                </span>
              </div>
              <div>
                <span className="text-blue-600">Subject:</span>{" "}
                <span className="font-medium text-blue-900">
                  55 Qs (85 marks)
                </span>
              </div>
            </div>
          </div>

          {/* ── Submit Button ── */}
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              ← Cancel
            </button>

            <button
              type="submit"
              disabled={
                submitting ||
                (config.scope === "topic" &&
                  config.selected_topics.length === 0)
              }
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-8 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Saving Configuration…
                </>
              ) : (
                <>
                  <svg
                    className="h-5 w-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                  Generate Exam
                </>
              )}
            </button>
          </div>
        </form>
      </main>
    </div>

```
**[ADDED]**
```
35              {/* Protected routes */}
36              <Route
37                path="/dashboard"
38                element={
39                  <ProtectedRoute>
40                    <Dashboard />
41                  </ProtectedRoute>
42                }
43              />
44              <Route
45                path="/generate-exam"
46                element={
47                  <ProtectedRoute>
48                    <GenerateExam />
49                  </ProtectedRoute>
50                }
51              />
52              <Route
53                path="/exam/:examId/progress"
54                element={
55                  <ProtectedRoute>
56                    <ExamProgress />
57                  </ProtectedRoute>
58                }
59              />
60              <Route
61                path="/analytics"
62                element={
63                  <ProtectedRoute>
64                    <Analytics />
65                  </ProtectedRoute>
66                }
67              />
68            </Routes>
69          </AuthProvider>
70        </BrowserRouter>
```
**[REMOVED]**
```
(from line ~72)
}
```
**[ADDED]**
```
72    }
73    
74    export default App;
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\App.tsx
*Saved at: 3/20/2026, 12:33:38 PM*

**[REMOVED]**
```
(from line ~1)
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";

```
**[ADDED]**
```
1     import { useState, type FormEvent } from "react";
2     import { useNavigate } from "react-router-dom";
3     import toast from "react-hot-toast";
```
**[REMOVED]**
```
(from line ~5)
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/layout/ProtectedRoute";

```
**[ADDED]**
```
5     import { useAuth } from "../hooks/useAuth";
6     import api from "../services/api";
7     import type { ExamConfig, ExamGenerateResponse } from "../types";
```
**[REMOVED]**
```
(from line ~9)
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import GenerateExam from "./pages/GenerateExam";
import Analytics from "./pages/Analytics";

```
**[ADDED]**
```
9     import Navbar from "../components/layout/Navbar";
10    import LoadingSpinner from "../components/common/LoadingSpinner";
11    import PaperSelector from "../components/exam/PaperSelector";
12    import ScopeSelector from "../components/exam/ScopeSelector";
13    import TopicPicker from "../components/exam/TopicPicker";
14    import DifficultySelector from "../components/exam/DifficultySelector";
15    import TypeRatioDisplay from "../components/exam/TypeRatioDisplay";
```
**[REMOVED]**
```
(from line ~17)
function App() {

```
**[ADDED]**
```
17    const DEFAULT_CONFIG: ExamConfig = {
18      paper: "CS",
19      scope: "full",
20      selected_topics: [],
21      difficulty: "auto",
22      types_ratio: { MCQ: 0.6, MSQ: 0.2, NAT: 0.2 },
23    };
24    
25    export default function GenerateExam() {
26      const { dbUser } = useAuth();
27      const navigate = useNavigate();
28    
29      const [config, setConfig] = useState<ExamConfig>(() => ({
30        ...DEFAULT_CONFIG,
31        paper: dbUser?.preferred_paper || "CS",
32      }));
33      const [submitting, setSubmitting] = useState(false);
34    
35      if (!dbUser) return <LoadingSpinner fullScreen />;
36    
37      const updateConfig = <K extends keyof ExamConfig>(
38        key: K,
39        value: ExamConfig[K]
40      ) => {
41        setConfig((prev) => ({ ...prev, [key]: value }));
42      };
43    
44      const handlePaperChange = (paper: "CS" | "DA") => {
45        setConfig((prev) => ({
46          ...prev,
47          paper,
48          selected_topics: [], // Reset topics when paper changes
49        }));
50      };
51    
52      const handleSubmit = async (e: FormEvent) => {
53        e.preventDefault();
54    
55        // ── Client-side validation ──
56        if (config.scope === "topic" && config.selected_topics.length === 0) {
57          toast.error("Please select at least one topic.");
58          return;
59        }
60    
61        setSubmitting(true);
62        try {
63          const { data } = await api.post<ExamGenerateResponse>(
64            "/exams/generate",
65            {
66              paper: config.paper,
67              scope: config.scope,
68              selected_topics:
69                config.scope === "topic" ? config.selected_topics : null,
70              difficulty: config.difficulty,
71              types_ratio: config.types_ratio,
72            }
73          );
74    
75          toast.success("Exam configuration saved!");
76    
77          // Navigate to progress page (Part 7 — placeholder for now)
78          navigate(`/exam/${data.exam_id}/progress`);
79        } catch (err: any) {
80          const detail =
81            err?.response?.data?.detail || "Failed to create exam. Please try again.";
82          toast.error(detail);
83        } finally {
84          setSubmitting(false);
85        }
86      };
87    
```
**[REMOVED]**
```
(from line ~89)
    <BrowserRouter>
      <AuthProvider>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: { background: "#363636", color: "#fff" },
          }}
        />

```
**[ADDED]**
```
89        <div className="min-h-screen bg-gray-50">
90          <Navbar />
```
**[REMOVED]**
```
(from line ~92)
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />

```
**[ADDED]**
```
92          <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
93            {/* Header */}
94            <div className="mb-8">
95              <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
96                Generate New Mock Test
97              </h1>
98              <p className="mt-2 text-gray-500">
99                Configure your GATE 2026 mock exam. Each test follows the official
100               pattern: 65 questions, 100 marks, 3 hours.
101             </p>
102           </div>
```
**[REMOVED]**
```
(from line ~104)
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

```
**[ADDED]**
```
104           <form onSubmit={handleSubmit} className="space-y-8">
105             {/* ── Card 1: Paper Selection ── */}
106             <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
107               <PaperSelector value={config.paper} onChange={handlePaperChange} />
108             </div>
```
**[REMOVED]**
```
(from line ~110)
export default App;
```
**[ADDED]**
```
110             {/* ── Card 2: Scope ── */}
111             <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
112               <ScopeSelector
113                 value={config.scope}
114                 onChange={(scope) => updateConfig("scope", scope)}
115               />
116   
117               {/* Topic picker — shown only when scope is "topic" */}
118               {config.scope === "topic" && (
119                 <div className="mt-6 border-t border-gray-100 pt-6">
120                   <TopicPicker
121                     paper={config.paper}
122                     selected={config.selected_topics}
123                     onChange={(topics) =>
124                       updateConfig("selected_topics", topics)
125                     }
126                   />
127                 </div>
128               )}
129             </div>
130   
131             {/* ── Card 3: Difficulty ── */}
132             <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
133               <DifficultySelector
134                 value={config.difficulty}
135                 onChange={(d) => updateConfig("difficulty", d)}
136               />
137             </div>
138   
139             {/* ── Card 4: Question Type Ratio ── */}
140             <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
141               <TypeRatioDisplay value={config.types_ratio} />
142             </div>
143   
144             {/* ── Exam Summary ── */}
145             <div className="rounded-xl border border-blue-100 bg-blue-50 p-6">
146               <h3 className="text-sm font-semibold text-blue-900">
147                 Exam Summary
148               </h3>
149               <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
150                 <div>
151                   <span className="text-blue-600">Paper:</span>{" "}
152                   <span className="font-medium text-blue-900">
153                     {config.paper}
154                   </span>
155                 </div>
156                 <div>
157                   <span className="text-blue-600">Questions:</span>{" "}
158                   <span className="font-medium text-blue-900">65</span>
159                 </div>
160                 <div>
161                   <span className="text-blue-600">Marks:</span>{" "}
162                   <span className="font-medium text-blue-900">100</span>
163                 </div>
164                 <div>
165                   <span className="text-blue-600">Duration:</span>{" "}
166                   <span className="font-medium text-blue-900">3 hours</span>
167                 </div>
168                 <div>
169                   <span className="text-blue-600">Scope:</span>{" "}
170                   <span className="font-medium text-blue-900">
171                     {config.scope === "full"
172                       ? "Full Syllabus"
173                       : `${config.selected_topics.length} topic(s)`}
174                   </span>
175                 </div>
176                 <div>
177                   <span className="text-blue-600">Difficulty:</span>{" "}
178                   <span className="font-medium capitalize text-blue-900">
179                     {config.difficulty}
180                   </span>
181                 </div>
182                 <div>
183                   <span className="text-blue-600">GA Section:</span>{" "}
184                   <span className="font-medium text-blue-900">
185                     10 Qs (15 marks)
186                   </span>
187                 </div>
188                 <div>
189                   <span className="text-blue-600">Subject:</span>{" "}
190                   <span className="font-medium text-blue-900">
191                     55 Qs (85 marks)
192                   </span>
193                 </div>
194               </div>
195             </div>
196   
197             {/* ── Submit Button ── */}
198             <div className="flex items-center justify-between">
199               <button
200                 type="button"
201                 onClick={() => navigate("/dashboard")}
202                 className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
203               >
204                 ← Cancel
205               </button>
206   
207               <button
208                 type="submit"
209                 disabled={
210                   submitting ||
211                   (config.scope === "topic" &&
212                     config.selected_topics.length === 0)
213                 }
214                 className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-8 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
215               >
216                 {submitting ? (
217                   <>
218                     <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
219                     Saving Configuration…
220                   </>
221                 ) : (
222                   <>
223                     <svg
224                       className="h-5 w-5"
225                       fill="none"
226                       stroke="currentColor"
227                       viewBox="0 0 24 24"
228                     >
229                       <path
230                         strokeLinecap="round"
231                         strokeLinejoin="round"
232                         strokeWidth={2}
233                         d="M13 10V3L4 14h7v7l9-11h-7z"
234                       />
235                     </svg>
236                     Generate Exam
237                   </>
238                 )}
239               </button>
240             </div>
241           </form>
242         </main>
243       </div>
244     );
245   }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\pages\GenerateExam.tsx
*Saved at: 3/20/2026, 12:33:13 PM*

**[REMOVED]**
```
(from line ~1)
import { Link } from "react-router-dom";

```
**[ADDED]**
```
1     import { useState, type FormEvent } from "react";
2     import { useNavigate } from "react-router-dom";
3     import toast from "react-hot-toast";
4     
5     import { useAuth } from "../hooks/useAuth";
6     import api from "../services/api";
7     import type { ExamConfig, ExamGenerateResponse } from "../types";
8     
```
**[ADDED]**
```
10    import LoadingSpinner from "../components/common/LoadingSpinner";
11    import PaperSelector from "../components/exam/PaperSelector";
12    import ScopeSelector from "../components/exam/ScopeSelector";
13    import TopicPicker from "../components/exam/TopicPicker";
14    import DifficultySelector from "../components/exam/DifficultySelector";
15    import TypeRatioDisplay from "../components/exam/TypeRatioDisplay";
```
**[ADDED]**
```
17    const DEFAULT_CONFIG: ExamConfig = {
18      paper: "CS",
19      scope: "full",
20      selected_topics: [],
21      difficulty: "auto",
22      types_ratio: { MCQ: 0.6, MSQ: 0.2, NAT: 0.2 },
23    };
24    
```
**[ADDED]**
```
26      const { dbUser } = useAuth();
27      const navigate = useNavigate();
28    
29      const [config, setConfig] = useState<ExamConfig>(() => ({
30        ...DEFAULT_CONFIG,
31        paper: dbUser?.preferred_paper || "CS",
32      }));
33      const [submitting, setSubmitting] = useState(false);
34    
35      if (!dbUser) return <LoadingSpinner fullScreen />;
36    
37      const updateConfig = <K extends keyof ExamConfig>(
38        key: K,
39        value: ExamConfig[K]
40      ) => {
41        setConfig((prev) => ({ ...prev, [key]: value }));
42      };
43    
44      const handlePaperChange = (paper: "CS" | "DA") => {
45        setConfig((prev) => ({
46          ...prev,
47          paper,
48          selected_topics: [], // Reset topics when paper changes
49        }));
50      };
51    
52      const handleSubmit = async (e: FormEvent) => {
53        e.preventDefault();
54    
55        // ── Client-side validation ──
56        if (config.scope === "topic" && config.selected_topics.length === 0) {
57          toast.error("Please select at least one topic.");
58          return;
59        }
60    
61        setSubmitting(true);
62        try {
63          const { data } = await api.post<ExamGenerateResponse>(
64            "/exams/generate",
65            {
66              paper: config.paper,
67              scope: config.scope,
68              selected_topics:
69                config.scope === "topic" ? config.selected_topics : null,
70              difficulty: config.difficulty,
71              types_ratio: config.types_ratio,
72            }
73          );
74    
75          toast.success("Exam configuration saved!");
76    
77          // Navigate to progress page (Part 7 — placeholder for now)
78          navigate(`/exam/${data.exam_id}/progress`);
79        } catch (err: any) {
80          const detail =
81            err?.response?.data?.detail || "Failed to create exam. Please try again.";
82          toast.error(detail);
83        } finally {
84          setSubmitting(false);
85        }
86      };
87    
```
**[REMOVED]**
```
(from line ~92)
      <main className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6 lg:px-8">
        <div className="rounded-xl border border-gray-200 bg-white p-12 shadow-sm">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-blue-50">
            <span className="text-3xl">⚙️</span>
          </div>

          <h1 className="mt-6 text-2xl font-bold text-gray-900">
            Generate New Exam

```
**[ADDED]**
```
92          <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
93            {/* Header */}
94            <div className="mb-8">
95              <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
96                Generate New Mock Test
```
**[REMOVED]**
```
(from line ~98)
          <p className="mx-auto mt-3 max-w-md text-gray-500">
            Exam configuration and AI-powered question generation will be
            available in the next module. Stay tuned!

```
**[ADDED]**
```
98              <p className="mt-2 text-gray-500">
99                Configure your GATE 2026 mock exam. Each test follows the official
100               pattern: 65 questions, 100 marks, 3 hours.
```
**[REMOVED]**
```
(from line ~102)

          <Link
            to="/dashboard"
            className="mt-8 inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            ← Back to Dashboard
          </Link>

```
**[ADDED]**
```
103   
104           <form onSubmit={handleSubmit} className="space-y-8">
105             {/* ── Card 1: Paper Selection ── */}
106             <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
107               <PaperSelector value={config.paper} onChange={handlePaperChange} />
108             </div>
109   
110             {/* ── Card 2: Scope ── */}
111             <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
112               <ScopeSelector
113                 value={config.scope}
114                 onChange={(scope) => updateConfig("scope", scope)}
115               />
116   
117               {/* Topic picker — shown only when scope is "topic" */}
118               {config.scope === "topic" && (
119                 <div className="mt-6 border-t border-gray-100 pt-6">
120                   <TopicPicker
121                     paper={config.paper}
122                     selected={config.selected_topics}
123                     onChange={(topics) =>
124                       updateConfig("selected_topics", topics)
125                     }
126                   />
127                 </div>
128               )}
129             </div>
130   
131             {/* ── Card 3: Difficulty ── */}
132             <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
133               <DifficultySelector
134                 value={config.difficulty}
135                 onChange={(d) => updateConfig("difficulty", d)}
136               />
137             </div>
138   
139             {/* ── Card 4: Question Type Ratio ── */}
140             <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
141               <TypeRatioDisplay value={config.types_ratio} />
142             </div>
143   
144             {/* ── Exam Summary ── */}
145             <div className="rounded-xl border border-blue-100 bg-blue-50 p-6">
146               <h3 className="text-sm font-semibold text-blue-900">
147                 Exam Summary
148               </h3>
149               <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
150                 <div>
151                   <span className="text-blue-600">Paper:</span>{" "}
152                   <span className="font-medium text-blue-900">
153                     {config.paper}
154                   </span>
155                 </div>
156                 <div>
157                   <span className="text-blue-600">Questions:</span>{" "}
158                   <span className="font-medium text-blue-900">65</span>
159                 </div>
160                 <div>
161                   <span className="text-blue-600">Marks:</span>{" "}
162                   <span className="font-medium text-blue-900">100</span>
163                 </div>
164                 <div>
165                   <span className="text-blue-600">Duration:</span>{" "}
166                   <span className="font-medium text-blue-900">3 hours</span>
167                 </div>
168                 <div>
169                   <span className="text-blue-600">Scope:</span>{" "}
170                   <span className="font-medium text-blue-900">
171                     {config.scope === "full"
172                       ? "Full Syllabus"
173                       : `${config.selected_topics.length} topic(s)`}
174                   </span>
175                 </div>
176                 <div>
177                   <span className="text-blue-600">Difficulty:</span>{" "}
178                   <span className="font-medium capitalize text-blue-900">
179                     {config.difficulty}
180                   </span>
181                 </div>
182                 <div>
183                   <span className="text-blue-600">GA Section:</span>{" "}
184                   <span className="font-medium text-blue-900">
185                     10 Qs (15 marks)
186                   </span>
187                 </div>
188                 <div>
189                   <span className="text-blue-600">Subject:</span>{" "}
190                   <span className="font-medium text-blue-900">
191                     55 Qs (85 marks)
192                   </span>
193                 </div>
194               </div>
195             </div>
196   
197             {/* ── Submit Button ── */}
198             <div className="flex items-center justify-between">
199               <button
200                 type="button"
201                 onClick={() => navigate("/dashboard")}
202                 className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
203               >
204                 ← Cancel
205               </button>
206   
207               <button
208                 type="submit"
209                 disabled={
210                   submitting ||
211                   (config.scope === "topic" &&
212                     config.selected_topics.length === 0)
213                 }
214                 className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-8 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
215               >
216                 {submitting ? (
217                   <>
218                     <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
219                     Saving Configuration…
220                   </>
221                 ) : (
222                   <>
223                     <svg
224                       className="h-5 w-5"
225                       fill="none"
226                       stroke="currentColor"
227                       viewBox="0 0 24 24"
228                     >
229                       <path
230                         strokeLinecap="round"
231                         strokeLinejoin="round"
232                         strokeWidth={2}
233                         d="M13 10V3L4 14h7v7l9-11h-7z"
234                       />
235                     </svg>
236                     Generate Exam
237                   </>
238                 )}
239               </button>
240             </div>
241           </form>
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\components\exam\TypeRatioDisplay.tsx
*Saved at: 3/20/2026, 12:32:54 PM*

**[ADDED]**
```
1     import type { TypesRatio } from "../../types";
2     
3     interface Props {
4       value: TypesRatio;
5     }
6     
7     const types = [
8       {
9         key: "MCQ" as const,
10        label: "MCQ",
11        fullName: "Multiple Choice (single correct)",
12        color: "bg-blue-500",
13        lightBg: "bg-blue-50",
14        text: "text-blue-700",
15      },
16      {
17        key: "MSQ" as const,
18        label: "MSQ",
19        fullName: "Multiple Select (one or more correct)",
20        color: "bg-purple-500",
21        lightBg: "bg-purple-50",
22        text: "text-purple-700",
23      },
24      {
25        key: "NAT" as const,
26        label: "NAT",
27        fullName: "Numerical Answer Type",
28        color: "bg-orange-500",
29        lightBg: "bg-orange-50",
30        text: "text-orange-700",
31      },
32    ];
33    
34    export default function TypeRatioDisplay({ value }: Props) {
35      return (
36        <div>
37          <label className="mb-3 block text-sm font-semibold text-gray-700">
38            Question Type Ratio
39          </label>
40    
41          {/* Visual bar */}
42          <div className="mb-4 flex h-4 overflow-hidden rounded-full bg-gray-100">
43            {types.map((t) => (
44              <div
45                key={t.key}
46                className={`${t.color} transition-all`}
47                style={{ width: `${value[t.key] * 100}%` }}
48              />
49            ))}
50          </div>
51    
52          {/* Legend */}
53          <div className="grid gap-3 sm:grid-cols-3">
54            {types.map((t) => {
55              const pct = Math.round(value[t.key] * 100);
56              // Approximate question count out of 55 subject questions
57              const approxCount = Math.round(value[t.key] * 55);
58    
59              return (
60                <div
61                  key={t.key}
62                  className={`rounded-lg ${t.lightBg} p-3`}
63                >
64                  <div className="flex items-center justify-between">
65                    <span className={`text-sm font-semibold ${t.text}`}>
66                      {t.label}
67                    </span>
68                    <span className={`text-lg font-bold ${t.text}`}>{pct}%</span>
69                  </div>
70                  <p className="mt-1 text-xs text-gray-500">{t.fullName}</p>
71                  <p className="mt-0.5 text-xs text-gray-400">
72                    ~{approxCount} questions (subject section)
73                  </p>
74                </div>
75              );
76            })}
77          </div>
78    
79          <p className="mt-3 text-xs text-gray-400">
80            Standard GATE distribution. GA section (10 Qs) is always MCQ. Ratio
81            applies to the 55 subject questions only.
82          </p>
83        </div>
84      );
85    }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\components\exam\DifficultySelector.tsx
*Saved at: 3/20/2026, 12:32:34 PM*

**[ADDED]**
```
1     interface Props {
2       value: "easy" | "medium" | "hard" | "auto";
3       onChange: (difficulty: "easy" | "medium" | "hard" | "auto") => void;
4     }
5     
6     const levels = [
7       {
8         code: "easy" as const,
9         label: "Easy",
10        desc: "Foundational concepts, straightforward problems",
11        color: "green",
12        icon: "🟢",
13      },
14      {
15        code: "medium" as const,
16        label: "Medium",
17        desc: "Standard GATE difficulty, multi-step reasoning",
18        color: "yellow",
19        icon: "🟡",
20      },
21      {
22        code: "hard" as const,
23        label: "Hard",
24        desc: "Challenging problems, deep conceptual understanding",
25        color: "red",
26        icon: "🔴",
27      },
28      {
29        code: "auto" as const,
30        label: "Auto (Mixed)",
31        desc: "AI selects a realistic mix of difficulties",
32        color: "blue",
33        icon: "🔵",
34      },
35    ];
36    
37    const borderMap: Record<string, string> = {
38      green: "border-green-500 bg-green-50 ring-green-200",
39      yellow: "border-yellow-500 bg-yellow-50 ring-yellow-200",
40      red: "border-red-500 bg-red-50 ring-red-200",
41      blue: "border-blue-500 bg-blue-50 ring-blue-200",
42    };
43    
44    const textMap: Record<string, string> = {
45      green: "text-green-700",
46      yellow: "text-yellow-700",
47      red: "text-red-700",
48      blue: "text-blue-700",
49    };
50    
51    export default function DifficultySelector({ value, onChange }: Props) {
52      return (
53        <div>
54          <label className="mb-3 block text-sm font-semibold text-gray-700">
55            Difficulty Level
56          </label>
57          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
58            {levels.map((l) => {
59              const selected = value === l.code;
60              return (
61                <button
62                  key={l.code}
63                  type="button"
64                  onClick={() => onChange(l.code)}
65                  className={`rounded-xl border-2 p-4 text-left transition-all ${
66                    selected
67                      ? `${borderMap[l.color]} ring-1`
68                      : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
69                  }`}
70                >
71                  <div className="flex items-center justify-between">
72                    <span className="text-lg">{l.icon}</span>
73                    <div
74                      className={`flex h-5 w-5 items-center justify-center rounded-full border-2 ${
75                        selected
76                          ? "border-blue-600 bg-blue-600"
77                          : "border-gray-300"
78                      }`}
79                    >
80                      {selected && (
81                        <div className="h-2 w-2 rounded-full bg-white" />
82                      )}
83                    </div>
84                  </div>
85                  <p
86                    className={`mt-2 font-semibold ${
87                      selected ? textMap[l.color] : "text-gray-900"
88                    }`}
89                  >
90                    {l.label}
91                  </p>
92                  <p className="mt-1 text-xs text-gray-500">{l.desc}</p>
93                </button>
94              );
95            })}
96          </div>
97        </div>
98      );
99    }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\components\exam\TopicPicker.tsx
*Saved at: 3/20/2026, 12:32:15 PM*

**[ADDED]**
```
1     import { useEffect, useState } from "react";
2     import toast from "react-hot-toast";
3     import api from "../../services/api";
4     import type { TopicFlat, TopicListResponse } from "../../types";
5     import LoadingSpinner from "../common/LoadingSpinner";
6     
7     interface Props {
8       paper: "CS" | "DA";
9       selected: string[];
10      onChange: (topics: string[]) => void;
11    }
12    
13    export default function TopicPicker({ paper, selected, onChange }: Props) {
14      const [topics, setTopics] = useState<TopicFlat[]>([]);
15      const [loading, setLoading] = useState(false);
16      const [searchQuery, setSearchQuery] = useState("");
17    
18      useEffect(() => {
19        const fetchTopics = async () => {
20          setLoading(true);
21          try {
22            const { data } = await api.get<TopicListResponse>(
23              `/syllabus/${paper}/topics`
24            );
25            setTopics(data.topics);
26          } catch {
27            toast.error(
28              `Failed to load topics for ${paper}. Make sure syllabus data is loaded.`
29            );
30            setTopics([]);
31          } finally {
32            setLoading(false);
33          }
34        };
35        fetchTopics();
36      }, [paper]);
37    
38      // Group topics by section
39      const grouped: Record<string, TopicFlat[]> = {};
40      for (const t of topics) {
41        if (!grouped[t.section_name]) grouped[t.section_name] = [];
42        grouped[t.section_name].push(t);
43      }
44    
45      // Filter by search
46      const filteredGrouped: Record<string, TopicFlat[]> = {};
47      const q = searchQuery.toLowerCase().trim();
48      for (const [section, items] of Object.entries(grouped)) {
49        const filtered = q
50          ? items.filter(
51              (t) =>
52                t.topic.toLowerCase().includes(q) ||
53                section.toLowerCase().includes(q)
54            )
55          : items;
56        if (filtered.length > 0) filteredGrouped[section] = filtered;
57      }
58    
59      const toggle = (topic: string) => {
60        if (selected.includes(topic)) {
61          onChange(selected.filter((t) => t !== topic));
62        } else {
63          onChange([...selected, topic]);
64        }
65      };
66    
67      const toggleSection = (sectionTopics: TopicFlat[]) => {
68        const sectionNames = sectionTopics.map((t) => t.topic);
69        const allSelected = sectionNames.every((t) => selected.includes(t));
70    
71        if (allSelected) {
72          onChange(selected.filter((t) => !sectionNames.includes(t)));
73        } else {
74          const merged = new Set([...selected, ...sectionNames]);
75          onChange(Array.from(merged));
76        }
77      };
78    
79      const selectAll = () => {
80        onChange(topics.map((t) => t.topic));
81      };
82    
83      const clearAll = () => {
84        onChange([]);
85      };
86    
87      if (loading) return <LoadingSpinner size="sm" />;
88    
89      if (topics.length === 0) {
90        return (
91          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-700">
92            No topics found for {paper}. Please load syllabus data first via{" "}
93            <code className="rounded bg-yellow-100 px-1">POST /api/v1/admin/load-data</code>
94          </div>
95        );
96      }
97    
98      return (
99        <div>
100         <label className="mb-3 block text-sm font-semibold text-gray-700">
101           Select Topics ({selected.length} of {topics.length} selected)
102         </label>
103   
104         {/* Search + bulk actions */}
105         <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
106           <input
107             type="text"
108             placeholder="Search topics..."
109             value={searchQuery}
110             onChange={(e) => setSearchQuery(e.target.value)}
111             className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:max-w-xs"
112           />
113           <div className="flex gap-2">
114             <button
115               type="button"
116               onClick={selectAll}
117               className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
118             >
119               Select All
120             </button>
121             <button
122               type="button"
123               onClick={clearAll}
124               className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
125             >
126               Clear All
127             </button>
128           </div>
129         </div>
130   
131         {/* Sections and topics */}
132         <div className="max-h-[400px] space-y-4 overflow-y-auto rounded-lg border border-gray-200 bg-white p-4">
133           {Object.entries(filteredGrouped).map(([section, items]) => {
134             const sectionNames = items.map((t) => t.topic);
135             const allSelected = sectionNames.every((t) => selected.includes(t));
136             const someSelected =
137               !allSelected && sectionNames.some((t) => selected.includes(t));
138   
139             return (
140               <div key={section}>
141                 {/* Section header */}
142                 <div className="mb-2 flex items-center gap-2">
143                   <input
144                     type="checkbox"
145                     checked={allSelected}
146                     ref={(el) => {
147                       if (el) el.indeterminate = someSelected;
148                     }}
149                     onChange={() => toggleSection(items)}
150                     className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
151                   />
152                   <span className="text-sm font-semibold text-gray-800">
153                     {section}
154                   </span>
155                   <span className="text-xs text-gray-400">
156                     ({items.length} topics)
157                   </span>
158                 </div>
159   
160                 {/* Topics grid */}
161                 <div className="ml-6 grid gap-1.5 sm:grid-cols-2">
162                   {items.map((t) => (
163                     <label
164                       key={t.id}
165                       className={`flex cursor-pointer items-center gap-2 rounded-lg px-3 py-1.5 text-sm transition-colors ${
166                         selected.includes(t.topic)
167                           ? "bg-blue-50 text-blue-700"
168                           : "text-gray-600 hover:bg-gray-50"
169                       }`}
170                     >
171                       <input
172                         type="checkbox"
173                         checked={selected.includes(t.topic)}
174                         onChange={() => toggle(t.topic)}
175                         className="h-3.5 w-3.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
176                       />
177                       <span className="truncate">{t.topic}</span>
178                     </label>
179                   ))}
180                 </div>
181               </div>
182             );
183           })}
184   
185           {Object.keys(filteredGrouped).length === 0 && (
186             <p className="py-4 text-center text-sm text-gray-400">
187               No topics match "{searchQuery}"
188             </p>
189           )}
190         </div>
191       </div>
192     );
193   }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\components\exam\ScopeSelector.tsx
*Saved at: 3/20/2026, 12:32:02 PM*

**[ADDED]**
```
1     interface Props {
2       value: "full" | "topic";
3       onChange: (scope: "full" | "topic") => void;
4     }
5     
6     const scopes = [
7       {
8         code: "full" as const,
9         name: "Full Syllabus",
10        desc: "Questions from all sections — mimics the real GATE exam.",
11        icon: "📚",
12      },
13      {
14        code: "topic" as const,
15        name: "Select Topics",
16        desc: "Choose specific topics to focus your practice session.",
17        icon: "🎯",
18      },
19    ];
20    
21    export default function ScopeSelector({ value, onChange }: Props) {
22      return (
23        <div>
24          <label className="mb-3 block text-sm font-semibold text-gray-700">
25            Exam Scope
26          </label>
27          <div className="grid gap-4 sm:grid-cols-2">
28            {scopes.map((s) => {
29              const selected = value === s.code;
30              return (
31                <button
32                  key={s.code}
33                  type="button"
34                  onClick={() => onChange(s.code)}
35                  className={`flex items-start gap-3 rounded-xl border-2 p-4 text-left transition-all ${
36                    selected
37                      ? "border-blue-600 bg-blue-50 ring-1 ring-blue-200"
38                      : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
39                  }`}
40                >
41                  <span className="text-2xl">{s.icon}</span>
42                  <div className="flex-1">
43                    <p
44                      className={`font-semibold ${
45                        selected ? "text-blue-700" : "text-gray-900"
46                      }`}
47                    >
48                      {s.name}
49                    </p>
50                    <p className="mt-0.5 text-xs text-gray-500">{s.desc}</p>
51                  </div>
52                  <div className="mt-0.5">
53                    <div
54                      className={`flex h-5 w-5 items-center justify-center rounded-full border-2 ${
55                        selected
56                          ? "border-blue-600 bg-blue-600"
57                          : "border-gray-300"
58                      }`}
59                    >
60                      {selected && (
61                        <div className="h-2 w-2 rounded-full bg-white" />
62                      )}
63                    </div>
64                  </div>
65                </button>
66              );
67            })}
68          </div>
69        </div>
70      );
71    }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\components\exam\PaperSelector.tsx
*Saved at: 3/20/2026, 12:31:45 PM*

**[REMOVED]**
```
(from line ~74)
} 
```
**[ADDED]**
```
74    }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\components\exam\PaperSelector.tsx
*Saved at: 3/20/2026, 12:31:43 PM*

**[REMOVED]**
```
(from line ~74)
}  
```
**[ADDED]**
```
74    } 
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\components\exam\PaperSelector.tsx
*Saved at: 3/20/2026, 12:31:42 PM*

**[REMOVED]**
```
(from line ~74)
}   
```
**[ADDED]**
```
74    }  
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\components\exam\PaperSelector.tsx
*Saved at: 3/20/2026, 12:31:41 PM*

**[ADDED]**
```
1     interface Props {
2       value: "CS" | "DA";
3       onChange: (paper: "CS" | "DA") => void;
4     }
5     
6     const papers = [
7       {
8         code: "CS" as const,
9         name: "Computer Science & IT",
10        sections: "13 sections · ~140 topics",
11        icon: "💻",
12      },
13      {
14        code: "DA" as const,
15        name: "Data Science & AI",
16        sections: "7 sections · ~110 topics",
17        icon: "🤖",
18      },
19    ];
20    
21    export default function PaperSelector({ value, onChange }: Props) {
22      return (
23        <div>
24          <label className="mb-3 block text-sm font-semibold text-gray-700">
25            Select Paper
26          </label>
27          <div className="grid gap-4 sm:grid-cols-2">
28            {papers.map((p) => {
29              const selected = value === p.code;
30              return (
31                <button
32                  key={p.code}
33                  type="button"
34                  onClick={() => onChange(p.code)}
35                  className={`flex items-start gap-4 rounded-xl border-2 p-5 text-left transition-all ${
36                    selected
37                      ? "border-blue-600 bg-blue-50 ring-1 ring-blue-200"
38                      : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
39                  }`}
40                >
41                  <span className="text-3xl">{p.icon}</span>
42                  <div>
43                    <p
44                      className={`text-base font-semibold ${
45                        selected ? "text-blue-700" : "text-gray-900"
46                      }`}
47                    >
48                      GATE {p.code}
49                    </p>
50                    <p className="mt-0.5 text-sm text-gray-500">{p.name}</p>
51                    <p className="mt-1 text-xs text-gray-400">{p.sections}</p>
52                  </div>
53    
54                  {/* Radio indicator */}
55                  <div className="ml-auto mt-1">
56                    <div
57                      className={`flex h-5 w-5 items-center justify-center rounded-full border-2 ${
58                        selected
59                          ? "border-blue-600 bg-blue-600"
60                          : "border-gray-300"
61                      }`}
62                    >
63                      {selected && (
64                        <div className="h-2 w-2 rounded-full bg-white" />
65                      )}
66                    </div>
67                  </div>
68                </button>
69              );
70            })}
71          </div>
72        </div>
73      );
74    }   
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\types\index.ts
*Saved at: 3/20/2026, 12:31:14 PM*

**[ADDED]**
```
35    /* ── Syllabus ── */
36    export interface TopicFlat {
37      id: number;
38      section_name: string;
39      topic: string;
40    }
41    
42    export interface TopicListResponse {
43      paper: string;
44      total_topics: number;
45      topics: TopicFlat[];
46    }
47    
48    /* ── Exam Config ── */
49    export interface TypesRatio {
50      MCQ: number;
51      MSQ: number;
52      NAT: number;
53    }
54    
55    export interface ExamConfig {
56      paper: "CS" | "DA";
57      scope: "full" | "topic";
58      selected_topics: string[];
59      difficulty: "easy" | "medium" | "hard" | "auto";
60      types_ratio: TypesRatio;
61    }
62    
63    export interface ExamGenerateResponse {
64      exam_id: string;
65      status: string;
66      message: string;
67    }
68    
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\api\router.py
*Saved at: 3/20/2026, 12:30:40 PM*

**[REMOVED]**
```
(from line ~14)
api_router.include_router(syllabus_router, prefix="/syllabus", tags=["syllabus"])api_router.include_router(exams_router, prefix="/exams", tags=["exams"])

```
**[ADDED]**
```
14    api_router.include_router(syllabus_router, prefix="/syllabus", tags=["syllabus"])
15    api_router.include_router(exams_router, prefix="/exams", tags=["exams"])
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\api\router.py
*Saved at: 3/20/2026, 12:30:37 PM*

**[REMOVED]**
```
(from line ~14)
api_router.include_router(syllabus_router, prefix="/syllabus", tags=["syllabus"])
```
**[ADDED]**
```
14    api_router.include_router(syllabus_router, prefix="/syllabus", tags=["syllabus"])api_router.include_router(exams_router, prefix="/exams", tags=["exams"])
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\api\router.py
*Saved at: 3/20/2026, 12:30:33 PM*

**[ADDED]**
```
7     from app.api.exams import router as exams_router
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\api\exams.py
*Saved at: 3/20/2026, 12:15:29 PM*

**[ADDED]**
```
1     import uuid
2     
3     from fastapi import APIRouter, Depends, HTTPException, status
4     from sqlalchemy import select
5     from sqlalchemy.ext.asyncio import AsyncSession
6     
7     from app.core.database import get_db
8     from app.core.security import get_current_user
9     from app.models.user import User
10    from app.models.exam import Exam
11    from app.models.syllabus import Syllabus
12    from app.schemas.exam import ExamGenerateRequest, ExamGenerateResponse, ExamSummary
13    
14    router = APIRouter()
15    
16    
17    @router.post(
18        "/generate",
19        response_model=ExamGenerateResponse,
20        status_code=status.HTTP_201_CREATED,
21        summary="Create exam configuration and start generation",
22    )
23    async def generate_exam(
24        body: ExamGenerateRequest,
25        user: User = Depends(get_current_user),
26        db: AsyncSession = Depends(get_db),
27    ):
28        """
29        Validates the exam configuration, creates an exam row with
30        status 'generating', and returns the exam_id.
31    
32        Does NOT call the LLM or generate questions yet — that happens
33        in a later part when the generation worker is built.
34        """
35    
36        # ── 1. Validate paper has syllabus data loaded ──
37        paper_count_result = await db.execute(
38            select(Syllabus.id).where(Syllabus.paper == body.paper).limit(1)
39        )
40        if paper_count_result.scalar_one_or_none() is None:
41            raise HTTPException(
42                status_code=status.HTTP_400_BAD_REQUEST,
43                detail=f"No syllabus data found for paper '{body.paper}'. "
44                "Please call POST /api/v1/admin/load-data first.",
45            )
46    
47        # ── 2. Validate GA syllabus exists (needed for every exam) ──
48        ga_count_result = await db.execute(
49            select(Syllabus.id).where(Syllabus.paper == "GA").limit(1)
50        )
51        if ga_count_result.scalar_one_or_none() is None:
52            raise HTTPException(
53                status_code=status.HTTP_400_BAD_REQUEST,
54                detail="No syllabus data found for General Aptitude (GA). "
55                "Please call POST /api/v1/admin/load-data first.",
56            )
57    
58        # ── 3. If scope is 'topic', validate selected_topics ──
59        if body.scope == "topic":
60            if not body.selected_topics or len(body.selected_topics) == 0:
61                raise HTTPException(
62                    status_code=status.HTTP_400_BAD_REQUEST,
63                    detail="When scope is 'topic', you must select at least one topic.",
64                )
65    
66            # Fetch all valid topics for this paper from the database
67            valid_topics_result = await db.execute(
68                select(Syllabus.topic).where(Syllabus.paper == body.paper)
69            )
70            valid_topics = {row[0] for row in valid_topics_result.fetchall()}
71    
72            invalid = [t for t in body.selected_topics if t not in valid_topics]
73            if invalid:
74                raise HTTPException(
75                    status_code=status.HTTP_400_BAD_REQUEST,
76                    detail=f"Invalid topics for paper {body.paper}: {invalid}",
77                )
78    
79        # ── 4. Validate types_ratio sums to ~1.0 ──
80        ratio_sum = body.types_ratio.MCQ + body.types_ratio.MSQ + body.types_ratio.NAT
81        if abs(ratio_sum - 1.0) > 0.05:
82            raise HTTPException(
83                status_code=status.HTTP_400_BAD_REQUEST,
84                detail=f"types_ratio must sum to 1.0 (got {ratio_sum:.2f})",
85            )
86    
87        # ── 5. Create exam row ──
88        exam_id = uuid.uuid4()
89    
90        exam = Exam(
91            id=exam_id,
92            user_id=user.id,
93            paper=body.paper,
94            scope=body.scope,
95            selected_topics=body.selected_topics if body.scope == "topic" else None,
96            difficulty=body.difficulty,
97            use_pyq_reference=False,  # Disabled — no RAG in v1
98            types_ratio={
99                "MCQ": body.types_ratio.MCQ,
100               "MSQ": body.types_ratio.MSQ,
101               "NAT": body.types_ratio.NAT,
102           },
103           total_questions=65,
104           total_marks=100,
105           duration_minutes=180,
106           question_ids=[],       # Will be populated by generation worker
107           question_order=[],     # Will be populated by generation worker
108           status="generating",
109           generation_progress={"total": 65, "completed": 0, "failed": 0},
110       )
111   
112       db.add(exam)
113       await db.commit()
114       await db.refresh(exam)
115   
116       return ExamGenerateResponse(
117           exam_id=exam.id,
118           status=exam.status,
119           message="Exam configuration saved. Generation will begin shortly.",
120       )
121   
122   
123   @router.get(
124       "",
125       response_model=list[ExamSummary],
126       summary="List all exams for the current user",
127   )
128   async def list_exams(
129       user: User = Depends(get_current_user),
130       db: AsyncSession = Depends(get_db),
131   ):
132       """Returns all exams created by the current user, newest first."""
133       result = await db.execute(
134           select(Exam)
135           .where(Exam.user_id == user.id)
136           .order_by(Exam.created_at.desc())
137       )
138       exams = result.scalars().all()
139   
140       return [
141           ExamSummary(
142               id=e.id,
143               paper=e.paper,
144               scope=e.scope,
145               selected_topics=e.selected_topics,
146               difficulty=e.difficulty,
147               total_questions=e.total_questions,
148               total_marks=e.total_marks,
149               duration_minutes=e.duration_minutes,
150               status=e.status,
151               created_at=e.created_at,
152           )
153           for e in exams
154       ]
155   
156   
157   @router.get(
158       "/{exam_id}/status",
159       summary="Get exam generation status",
160   )
161   async def get_exam_status(
162       exam_id: uuid.UUID,
163       user: User = Depends(get_current_user),
164       db: AsyncSession = Depends(get_db),
165   ):
166       """Poll this endpoint to check generation progress."""
167       result = await db.execute(
168           select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
169       )
170       exam = result.scalar_one_or_none()
171   
172       if exam is None:
173           raise HTTPException(
174               status_code=status.HTTP_404_NOT_FOUND,
175               detail="Exam not found.",
176           )
177   
178       return {
179           "exam_id": exam.id,
180           "status": exam.status,
181           "progress": exam.generation_progress,
182       }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\schemas\exam.py
*Saved at: 3/20/2026, 12:14:52 PM*

**[ADDED]**
```
1     from datetime import datetime
2     from typing import Optional
3     from uuid import UUID
4     
5     from pydantic import BaseModel, field_validator
6     
7     
8     class TypesRatio(BaseModel):
9         MCQ: float = 0.6
10        MSQ: float = 0.2
11        NAT: float = 0.2
12    
13        @field_validator("MCQ", "MSQ", "NAT")
14        @classmethod
15        def validate_ratio(cls, v: float) -> float:
16            if v < 0 or v > 1:
17                raise ValueError("Ratio values must be between 0 and 1")
18            return v
19    
20    
21    class ExamGenerateRequest(BaseModel):
22        paper: str
23        scope: str  # 'full' or 'topic'
24        selected_topics: Optional[list[str]] = None
25        difficulty: str  # 'easy', 'medium', 'hard', 'auto'
26        types_ratio: TypesRatio = TypesRatio()
27    
28        @field_validator("paper")
29        @classmethod
30        def validate_paper(cls, v: str) -> str:
31            v = v.upper()
32            if v not in ("CS", "DA"):
33                raise ValueError("paper must be 'CS' or 'DA'")
34            return v
35    
36        @field_validator("scope")
37        @classmethod
38        def validate_scope(cls, v: str) -> str:
39            v = v.lower()
40            if v not in ("full", "topic"):
41                raise ValueError("scope must be 'full' or 'topic'")
42            return v
43    
44        @field_validator("difficulty")
45        @classmethod
46        def validate_difficulty(cls, v: str) -> str:
47            v = v.lower()
48            if v not in ("easy", "medium", "hard", "auto"):
49                raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
50            return v
51    
52        @field_validator("selected_topics")
53        @classmethod
54        def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
55            # Will be validated against DB in the endpoint
56            return v
57    
58    
59    class ExamGenerateResponse(BaseModel):
60        exam_id: UUID
61        status: str
62        message: str
63    
64    
65    class ExamSummary(BaseModel):
66        id: UUID
67        paper: str
68        scope: str
69        selected_topics: Optional[list[str]] = None
70        difficulty: str
71        total_questions: int
72        total_marks: int
73        duration_minutes: int
74        status: str
75        created_at: datetime
76    
77        class Config:
78            from_attributes = True
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\.env
*Saved at: 3/20/2026, 10:56:43 AM*

**[REMOVED]**
```
(from line ~1)
VITE_API_BASE_URL=http://localhost:8000/api/v1

```
**[ADDED]**
```
1     VITE_API_BASE_URL=http://localhost:8001/api/v1
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\api\router.py
*Saved at: 3/20/2026, 10:23:00 AM*

**[ADDED]**
```
5     from app.api.admin import router as admin_router
6     from app.api.syllabus import router as syllabus_router
```
**[REMOVED]**
```
(from line ~11)
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
```
**[ADDED]**
```
11    api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
12    api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
13    api_router.include_router(syllabus_router, prefix="/syllabus", tags=["syllabus"])
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\api\syllabus.py
*Saved at: 3/20/2026, 10:22:40 AM*

**[ADDED]**
```
1     from fastapi import APIRouter, Depends, HTTPException, status
2     from sqlalchemy import select
3     from sqlalchemy.ext.asyncio import AsyncSession
4     
5     from app.core.database import get_db
6     from app.core.security import get_current_user
7     from app.models.user import User
8     from app.models.syllabus import Syllabus
9     from app.schemas.syllabus import (
10        SyllabusResponse,
11        SyllabusSection,
12        TopicItem,
13        TopicListResponse,
14        TopicFlat,
15    )
16    
17    router = APIRouter()
18    
19    VALID_PAPERS = {"CS", "DA", "GA"}
20    
21    
22    def _validate_paper(paper: str) -> str:
23        """Normalise to uppercase and validate."""
24        paper = paper.upper()
25        if paper not in VALID_PAPERS:
26            raise HTTPException(
27                status_code=status.HTTP_400_BAD_REQUEST,
28                detail=f"Invalid paper '{paper}'. Must be one of: {', '.join(sorted(VALID_PAPERS))}",
29            )
30        return paper
31    
32    
33    @router.get(
34        "/{paper}",
35        response_model=SyllabusResponse,
36        summary="Get syllabus for a paper, grouped by sections",
37    )
38    async def get_syllabus(
39        paper: str,
40        user: User = Depends(get_current_user),
41        db: AsyncSession = Depends(get_db),
42    ):
43        """
44        Returns the full syllabus taxonomy for CS, DA, or GA,
45        organised as sections → topics.
46        """
47        paper = _validate_paper(paper)
48    
49        result = await db.execute(
50            select(Syllabus)
51            .where(Syllabus.paper == paper)
52            .order_by(Syllabus.section_name, Syllabus.id)
53        )
54        rows = result.scalars().all()
55    
56        if not rows:
57            raise HTTPException(
58                status_code=status.HTTP_404_NOT_FOUND,
59                detail=f"No syllabus data found for paper '{paper}'. "
60                "Have you called POST /api/v1/admin/load-data ?",
61            )
62    
63        # Group by section_name preserving insertion order
64        sections_map: dict[str, list[TopicItem]] = {}
65        for row in rows:
66            if row.section_name not in sections_map:
67                sections_map[row.section_name] = []
68            sections_map[row.section_name].append(
69                TopicItem(id=row.id, topic=row.topic, subtopic=row.subtopic)
70            )
71    
72        sections = [
73            SyllabusSection(section_name=name, topics=topics)
74            for name, topics in sections_map.items()
75        ]
76    
77        return SyllabusResponse(
78            paper=paper,
79            total_topics=len(rows),
80            sections=sections,
81        )
82    
83    
84    @router.get(
85        "/{paper}/topics",
86        response_model=TopicListResponse,
87        summary="Get flat list of topics for a paper",
88    )
89    async def get_topics(
90        paper: str,
91        user: User = Depends(get_current_user),
92        db: AsyncSession = Depends(get_db),
93    ):
94        """
95        Returns a flat list of all topics for a paper.
96        Used by the frontend exam-configuration page
97        to render topic-selection checkboxes.
98        """
99        paper = _validate_paper(paper)
100   
101       result = await db.execute(
102           select(Syllabus)
103           .where(Syllabus.paper == paper)
104           .order_by(Syllabus.section_name, Syllabus.id)
105       )
106       rows = result.scalars().all()
107   
108       if not rows:
109           raise HTTPException(
110               status_code=status.HTTP_404_NOT_FOUND,
111               detail=f"No syllabus data found for paper '{paper}'. "
112               "Have you called POST /api/v1/admin/load-data ?",
113           )
114   
115       topics = [
116           TopicFlat(id=row.id, section_name=row.section_name, topic=row.topic)
117           for row in rows
118       ]
119   
120       return TopicListResponse(
121           paper=paper,
122           total_topics=len(topics),
123           topics=topics,
124       )
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\api\admin.py
*Saved at: 3/20/2026, 10:22:22 AM*

**[ADDED]**
```
1     from fastapi import APIRouter, Depends
2     from sqlalchemy.ext.asyncio import AsyncSession
3     
4     from app.core.database import get_db
5     from app.core.security import get_current_user
6     from app.models.user import User
7     from app.schemas.syllabus import DataLoadResponse, SyllabusStatsResponse
8     from app.services.data_loader import load_syllabus, get_syllabus_stats
9     
10    router = APIRouter()
11    
12    
13    @router.post(
14        "/load-data",
15        response_model=DataLoadResponse,
16        summary="Load syllabus JSON files into the database",
17    )
18    async def load_data(
19        user: User = Depends(get_current_user),
20        db: AsyncSession = Depends(get_db),
21    ):
22        """
23        Reads syllabus JSONs from backend/data/syllabus/ and inserts into
24        the `syllabus` table.  Idempotent — safe to call multiple times.
25    
26        Requires authentication (any logged-in user can trigger this for now).
27        """
28        result = await load_syllabus(db)
29    
30        if result.errors and not result.papers_loaded:
31            message = "Data loading failed — see errors"
32        elif result.errors:
33            message = "Data partially loaded — some files had errors"
34        else:
35            message = "All syllabus data loaded successfully"
36    
37        return DataLoadResponse(
38            message=message,
39            papers_loaded=result.papers_loaded,
40            total_rows_inserted=result.total_rows_inserted,
41            details=result.details,
42            errors=result.errors,
43        )
44    
45    
46    @router.get(
47        "/data-stats",
48        response_model=SyllabusStatsResponse,
49        summary="Get current data loading status",
50    )
51    async def data_stats(
52        user: User = Depends(get_current_user),
53        db: AsyncSession = Depends(get_db),
54    ):
55        """Returns counts of topics per paper currently in the database."""
56        stats = await get_syllabus_stats(db)
57        return SyllabusStatsResponse(stats=stats)
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\schemas\syllabus.py
*Saved at: 3/20/2026, 10:22:05 AM*

**[ADDED]**
```
1     from pydantic import BaseModel
2     
3     
4     class TopicItem(BaseModel):
5         """Single topic row from the syllabus table."""
6         id: int
7         topic: str
8         subtopic: str | None = None
9     
10    
11    class SyllabusSection(BaseModel):
12        """A section containing a list of topics."""
13        section_name: str
14        topics: list[TopicItem]
15    
16    
17    class SyllabusResponse(BaseModel):
18        """Full syllabus for a paper, grouped by sections."""
19        paper: str
20        total_topics: int
21        sections: list[SyllabusSection]
22    
23    
24    class TopicFlat(BaseModel):
25        """Flat topic item for checkbox lists."""
26        id: int
27        section_name: str
28        topic: str
29    
30    
31    class TopicListResponse(BaseModel):
32        """Flat list of all topics for a paper."""
33        paper: str
34        total_topics: int
35        topics: list[TopicFlat]
36    
37    
38    class DataLoadResponse(BaseModel):
39        """Response from the data loading endpoint."""
40        message: str
41        papers_loaded: list[str]
42        total_rows_inserted: int
43        details: dict
44        errors: list[str]
45    
46    
47    class SyllabusStatsResponse(BaseModel):
48        """Quick overview of what's loaded."""
49        stats: dict
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\data_loader.py
*Saved at: 3/20/2026, 10:19:21 AM*

**[ADDED]**
```
1     """
2     Service to load syllabus JSON files into the PostgreSQL syllabus table.
3     
4     • Reads from  backend/data/syllabus/
5     • Idempotent — deletes existing rows for the paper before inserting
6     • No PYQ loading, no embeddings (deferred to v2)
7     """
8     
9     import json
10    from pathlib import Path
11    
12    from sqlalchemy import delete, select, func
13    from sqlalchemy.ext.asyncio import AsyncSession
14    
15    from app.models.syllabus import Syllabus
16    
17    # Resolve the data directory relative to this file
18    # services/data_loader.py  →  app/services/  →  app/  →  backend/
19    DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
20    SYLLABUS_DIR = DATA_DIR / "syllabus"
21    
22    EXPECTED_FILES = {
23        "DA": "DA_syllabus.json",
24        "CS": "CS_syllabus.json",
25        "GA": "GA_syllabus.json",
26    }
27    
28    
29    class DataLoadResult:
30        """Simple container for load results."""
31    
32        def __init__(self) -> None:
33            self.papers_loaded: list[str] = []
34            self.total_rows_inserted: int = 0
35            self.details: dict[str, dict] = {}
36            self.errors: list[str] = []
37    
38        def to_dict(self) -> dict:
39            return {
40                "papers_loaded": self.papers_loaded,
41                "total_rows_inserted": self.total_rows_inserted,
42                "details": self.details,
43                "errors": self.errors,
44            }
45    
46    
47    def _read_syllabus_json(filepath: Path) -> dict:
48        """Read and parse a single syllabus JSON file."""
49        with open(filepath, "r", encoding="utf-8") as f:
50            data = json.load(f)
51    
52        # Basic validation
53        if "paper" not in data:
54            raise ValueError(f"Missing 'paper' key in {filepath.name}")
55        if "sections" not in data or not isinstance(data["sections"], list):
56            raise ValueError(f"Missing or invalid 'sections' in {filepath.name}")
57    
58        return data
59    
60    
61    async def load_syllabus(db: AsyncSession) -> DataLoadResult:
62        """
63        Load ALL syllabus JSON files into the database.
64    
65        Steps per file:
66          1. Parse JSON
67          2. DELETE existing rows for that paper (idempotent)
68          3. INSERT one row per topic
69        """
70        result = DataLoadResult()
71    
72        if not SYLLABUS_DIR.exists():
73            result.errors.append(
74                f"Syllabus directory not found: {SYLLABUS_DIR}. "
75                "Create it and place DA_syllabus.json, CS_syllabus.json, GA_syllabus.json inside."
76            )
77            return result
78    
79        for paper_code, filename in EXPECTED_FILES.items():
80            filepath = SYLLABUS_DIR / filename
81    
82            if not filepath.exists():
83                result.errors.append(f"File not found: {filepath}")
84                continue
85    
86            try:
87                data = _read_syllabus_json(filepath)
88            except (json.JSONDecodeError, ValueError) as exc:
89                result.errors.append(f"Failed to parse {filename}: {exc}")
90                continue
91    
92            paper = data["paper"]
93            sections = data["sections"]
94    
95            # ── Step 1: Delete existing rows for this paper ──
96            await db.execute(delete(Syllabus).where(Syllabus.paper == paper))
97    
98            # ── Step 2: Insert new rows ──
99            rows_inserted = 0
100           sections_count = 0
101   
102           for section in sections:
103               section_name = section.get("section_name", "Unknown")
104               topics = section.get("topics", [])
105               sections_count += 1
106   
107               for topic in topics:
108                   row = Syllabus(
109                       paper=paper,
110                       section_name=section_name,
111                       topic=topic,
112                       subtopic=None,
113                       source_file=filename,
114                   )
115                   db.add(row)
116                   rows_inserted += 1
117   
118           await db.flush()  # Flush so IDs are generated (but don't commit yet)
119   
120           result.papers_loaded.append(paper)
121           result.total_rows_inserted += rows_inserted
122           result.details[paper] = {
123               "filename": filename,
124               "sections": sections_count,
125               "topics_inserted": rows_inserted,
126           }
127   
128       # ── Commit all at once ──
129       await db.commit()
130       return result
131   
132   
133   async def get_syllabus_stats(db: AsyncSession) -> dict:
134       """Quick stats about what's currently loaded in the syllabus table."""
135       stats: dict[str, dict] = {}
136   
137       for paper_code in ["CS", "DA", "GA"]:
138           count_result = await db.execute(
139               select(func.count(Syllabus.id)).where(Syllabus.paper == paper_code)
140           )
141           count = count_result.scalar() or 0
142   
143           section_result = await db.execute(
144               select(Syllabus.section_name)
145               .where(Syllabus.paper == paper_code)
146               .distinct()
147           )
148           sections = [row[0] for row in section_result.fetchall()]
149   
150           stats[paper_code] = {
151               "total_topics": count,
152               "sections": sections,
153               "section_count": len(sections),
154           }
155   
156       return stats
```

---

