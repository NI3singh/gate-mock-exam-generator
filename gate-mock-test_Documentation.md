### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\styles\index.css
*Saved at: 3/24/2026, 2:45:35 PM*

**[REMOVED]**
```
(from line ~1)
@import 'katex/dist/katex.min.css'; 

```
**[ADDED]**
```
1     @import 'katex/dist/katex.min.css';
2     
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\styles\index.css
*Saved at: 3/24/2026, 2:45:33 PM*

**[REMOVED]**
```
(from line ~1)
@import 'katex/dist/katex.min.css';

```
**[ADDED]**
```
1     @import 'katex/dist/katex.min.css'; 
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\styles\index.css
*Saved at: 3/24/2026, 2:45:32 PM*

**[ADDED]**
```
1     @import 'katex/dist/katex.min.css';
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\styles\index.css
*Saved at: 3/24/2026, 2:45:29 PM*

**[REMOVED]**
```
(from line ~4)
@import 'katex/dist/katex.min.css';

```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\styles\index.css
*Saved at: 3/24/2026, 1:59:55 PM*

**[ADDED]**
```
4     @import 'katex/dist/katex.min.css';
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\schemas\exam.py
*Saved at: 3/24/2026, 10:03:19 AM*

**[ADDED]**
```
8     # ── Existing schemas (unchanged) ──────────────────────────────────────────────
9     
```
**[REMOVED]**
```
(from line ~57)
        # Will be validated against DB in the endpoint

```
**[REMOVED]**
```
(from line ~79)
        from_attributes = True
```
**[ADDED]**
```
79            from_attributes = True
80    
81    
82    # ── Part 8: Exam screen schemas ───────────────────────────────────────────────
83    
84    class QuestionItem(BaseModel):
85        """
86        Single question for the exam screen.
87        CRITICAL: Does NOT contain the answer field.
88        """
89        id: str
90        qno: int
91        question_type: str          # 'MCQ', 'MSQ', 'NAT'
92        marks: int                  # 1 or 2
93        section: str                # 'GA' or 'Subject'
94        section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
95        topic: str
96        stem_tex: str               # Question text with LaTeX math
97        code_snippet: Optional[str] = None
98        code_language: Optional[str] = None
99        choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
100       estimated_time_seconds: Optional[int] = None
101   
102   
103   class ExamScreenResponse(BaseModel):
104       """Full exam data returned for the exam screen."""
105       exam_id: str
106       paper: str
107       difficulty: str
108       total_questions: int
109       total_marks: int
110       duration_minutes: int
111       questions: list[QuestionItem]   # Ordered by qno, NO answers
112   
113   
114   class AttemptStartResponse(BaseModel):
115       """
116       Response from POST /exams/{id}/start.
117       Returns attempt ID, server start time, and any saved responses for resume.
118       """
119       attempt_id: str
120       exam_id: str
121       start_time: str         # ISO 8601 datetime string
122       remaining_seconds: int  # Seconds left in the exam
123       responses: dict         # Previously saved responses (for resume)
124       question_statuses: dict # Previously saved statuses (for resume)
125       submitted: bool         # True if already submitted (should not reach exam screen)
126       is_resume: bool = False # True if resuming an existing attempt
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\__init__.py
*Saved at: 3/24/2026, 10:02:59 AM*

**[REMOVED]**
```
(from line ~6)
from app.models.exam import exam

```
**[ADDED]**
```
6     from app.models.exam import Exam
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\exam.py
*Saved at: 3/24/2026, 10:02:49 AM*

**[REMOVED]**
```
(from line ~1)
from datetime import datetime
from typing import Optional
from uuid import UUID

```
**[ADDED]**
```
1     import uuid
```
**[REMOVED]**
```
(from line ~3)
from pydantic import BaseModel, field_validator

```
**[ADDED]**
```
3     from sqlalchemy import String, Integer, JSON, Boolean, ForeignKey
4     from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
5     from sqlalchemy.orm import Mapped, mapped_column
6     from sqlalchemy import func
```
**[ADDED]**
```
8     from app.core.database import Base
```
**[REMOVED]**
```
(from line ~10)
# ── Existing schemas (unchanged) ──────────────────────────────────────────────

```
**[REMOVED]**
```
(from line ~11)
class TypesRatio(BaseModel):
    MCQ: float = 0.6
    MSQ: float = 0.2
    NAT: float = 0.2

```
**[ADDED]**
```
11    class Exam(Base):
12        __tablename__ = "exams"
```
**[REMOVED]**
```
(from line ~14)
    @field_validator("MCQ", "MSQ", "NAT")
    @classmethod
    def validate_ratio(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("Ratio values must be between 0 and 1")
        return v


class ExamGenerateRequest(BaseModel):
    paper: str
    scope: str  # 'full' or 'topic'
    selected_topics: Optional[list[str]] = None
    difficulty: str  # 'easy', 'medium', 'hard', 'auto'
    types_ratio: TypesRatio = TypesRatio()

    @field_validator("paper")
    @classmethod
    def validate_paper(cls, v: str) -> str:
        v = v.upper()
        if v not in ("CS", "DA"):
            raise ValueError("paper must be 'CS' or 'DA'")
        return v

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        v = v.lower()
        if v not in ("full", "topic"):
            raise ValueError("scope must be 'full' or 'topic'")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        v = v.lower()
        if v not in ("easy", "medium", "hard", "auto"):
            raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
        return v

    @field_validator("selected_topics")
    @classmethod
    def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
        return v


class ExamGenerateResponse(BaseModel):
    exam_id: UUID
    status: str
    message: str


class ExamSummary(BaseModel):
    id: UUID
    paper: str
    scope: str
    selected_topics: Optional[list[str]] = None
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Part 8: Exam screen schemas ───────────────────────────────────────────────

class QuestionItem(BaseModel):
    """
    Single question for the exam screen.
    CRITICAL: Does NOT contain the answer field.
    """
    id: str
    qno: int
    question_type: str          # 'MCQ', 'MSQ', 'NAT'
    marks: int                  # 1 or 2
    section: str                # 'GA' or 'Subject'
    section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
    topic: str
    stem_tex: str               # Question text with LaTeX math
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None
    choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
    estimated_time_seconds: Optional[int] = None


class ExamScreenResponse(BaseModel):
    """Full exam data returned for the exam screen."""
    exam_id: str
    paper: str
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    questions: list[QuestionItem]   # Ordered by qno, NO answers


class AttemptStartResponse(BaseModel):
    """
    Response from POST /exams/{id}/start.
    Returns attempt ID, server start time, and any saved responses for resume.
    """
    attempt_id: str
    exam_id: str
    start_time: str         # ISO 8601 datetime string
    remaining_seconds: int  # Seconds left in the exam
    responses: dict         # Previously saved responses (for resume)
    question_statuses: dict # Previously saved statuses (for resume)
    submitted: bool         # True if already submitted (should not reach exam screen)
    is_resume: bool = False # True if resuming an existing attempt
```
**[ADDED]**
```
14        id: Mapped[uuid.UUID] = mapped_column(
15            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
16        )
17        user_id: Mapped[uuid.UUID] = mapped_column(
18            PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
19        )
20        paper: Mapped[str] = mapped_column(String(10), nullable=False)
21        scope: Mapped[str] = mapped_column(String(20), nullable=False)
22        selected_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)
23        difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
24        use_pyq_reference: Mapped[bool] = mapped_column(Boolean, default=True)
25        types_ratio: Mapped[dict] = mapped_column(
26            JSON, default={"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
27        )
28        total_questions: Mapped[int] = mapped_column(Integer, default=65)
29        total_marks: Mapped[int] = mapped_column(Integer, default=100)
30        duration_minutes: Mapped[int] = mapped_column(Integer, default=180)
31        question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
32        question_order: Mapped[list] = mapped_column(JSON, nullable=False)
33        status: Mapped[str] = mapped_column(String(20), default="generated")
34        generation_progress: Mapped[dict | None] = mapped_column(JSON, nullable=True)
35        created_at: Mapped[str] = mapped_column(
36            TIMESTAMP(timezone=True), server_default=func.now()
37        )
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\exam.py
*Saved at: 3/24/2026, 10:00:02 AM*

**[ADDED]**
```
1     from datetime import datetime
2     from typing import Optional
3     from uuid import UUID
4     
5     from pydantic import BaseModel, field_validator
6     
7     
8     # ── Existing schemas (unchanged) ──────────────────────────────────────────────
9     
10    class TypesRatio(BaseModel):
11        MCQ: float = 0.6
12        MSQ: float = 0.2
13        NAT: float = 0.2
14    
15        @field_validator("MCQ", "MSQ", "NAT")
16        @classmethod
17        def validate_ratio(cls, v: float) -> float:
18            if v < 0 or v > 1:
19                raise ValueError("Ratio values must be between 0 and 1")
20            return v
21    
22    
23    class ExamGenerateRequest(BaseModel):
24        paper: str
25        scope: str  # 'full' or 'topic'
26        selected_topics: Optional[list[str]] = None
27        difficulty: str  # 'easy', 'medium', 'hard', 'auto'
28        types_ratio: TypesRatio = TypesRatio()
29    
30        @field_validator("paper")
31        @classmethod
32        def validate_paper(cls, v: str) -> str:
33            v = v.upper()
34            if v not in ("CS", "DA"):
35                raise ValueError("paper must be 'CS' or 'DA'")
36            return v
37    
38        @field_validator("scope")
39        @classmethod
40        def validate_scope(cls, v: str) -> str:
41            v = v.lower()
42            if v not in ("full", "topic"):
43                raise ValueError("scope must be 'full' or 'topic'")
44            return v
45    
46        @field_validator("difficulty")
47        @classmethod
48        def validate_difficulty(cls, v: str) -> str:
49            v = v.lower()
50            if v not in ("easy", "medium", "hard", "auto"):
51                raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
52            return v
53    
54        @field_validator("selected_topics")
55        @classmethod
56        def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
57            return v
58    
59    
60    class ExamGenerateResponse(BaseModel):
61        exam_id: UUID
62        status: str
63        message: str
64    
65    
66    class ExamSummary(BaseModel):
67        id: UUID
68        paper: str
69        scope: str
70        selected_topics: Optional[list[str]] = None
71        difficulty: str
72        total_questions: int
73        total_marks: int
74        duration_minutes: int
75        status: str
76        created_at: datetime
77    
78        class Config:
79            from_attributes = True
80    
81    
82    # ── Part 8: Exam screen schemas ───────────────────────────────────────────────
83    
84    class QuestionItem(BaseModel):
85        """
86        Single question for the exam screen.
87        CRITICAL: Does NOT contain the answer field.
88        """
89        id: str
90        qno: int
91        question_type: str          # 'MCQ', 'MSQ', 'NAT'
92        marks: int                  # 1 or 2
93        section: str                # 'GA' or 'Subject'
94        section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
95        topic: str
96        stem_tex: str               # Question text with LaTeX math
97        code_snippet: Optional[str] = None
98        code_language: Optional[str] = None
99        choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
100       estimated_time_seconds: Optional[int] = None
101   
102   
103   class ExamScreenResponse(BaseModel):
104       """Full exam data returned for the exam screen."""
105       exam_id: str
106       paper: str
107       difficulty: str
108       total_questions: int
109       total_marks: int
110       duration_minutes: int
111       questions: list[QuestionItem]   # Ordered by qno, NO answers
112   
113   
114   class AttemptStartResponse(BaseModel):
115       """
116       Response from POST /exams/{id}/start.
117       Returns attempt ID, server start time, and any saved responses for resume.
118       """
119       attempt_id: str
120       exam_id: str
121       start_time: str         # ISO 8601 datetime string
122       remaining_seconds: int  # Seconds left in the exam
123       responses: dict         # Previously saved responses (for resume)
124       question_statuses: dict # Previously saved statuses (for resume)
125       submitted: bool         # True if already submitted (should not reach exam screen)
126       is_resume: bool = False # True if resuming an existing attempt
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\exam.py
*Saved at: 3/24/2026, 10:00:01 AM*

**[REMOVED]**
```
(from line ~1)
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


# ── Existing schemas (unchanged) ──────────────────────────────────────────────

class TypesRatio(BaseModel):
    MCQ: float = 0.6
    MSQ: float = 0.2
    NAT: float = 0.2

    @field_validator("MCQ", "MSQ", "NAT")
    @classmethod
    def validate_ratio(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("Ratio values must be between 0 and 1")
        return v


class ExamGenerateRequest(BaseModel):
    paper: str
    scope: str  # 'full' or 'topic'
    selected_topics: Optional[list[str]] = None
    difficulty: str  # 'easy', 'medium', 'hard', 'auto'
    types_ratio: TypesRatio = TypesRatio()

    @field_validator("paper")
    @classmethod
    def validate_paper(cls, v: str) -> str:
        v = v.upper()
        if v not in ("CS", "DA"):
            raise ValueError("paper must be 'CS' or 'DA'")
        return v

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        v = v.lower()
        if v not in ("full", "topic"):
            raise ValueError("scope must be 'full' or 'topic'")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        v = v.lower()
        if v not in ("easy", "medium", "hard", "auto"):
            raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
        return v

    @field_validator("selected_topics")
    @classmethod
    def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
        return v


class ExamGenerateResponse(BaseModel):
    exam_id: UUID
    status: str
    message: str


class ExamSummary(BaseModel):
    id: UUID
    paper: str
    scope: str
    selected_topics: Optional[list[str]] = None
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Part 8: Exam screen schemas ───────────────────────────────────────────────

class QuestionItem(BaseModel):
    """
    Single question for the exam screen.
    CRITICAL: Does NOT contain the answer field.
    """
    id: str
    qno: int
    question_type: str          # 'MCQ', 'MSQ', 'NAT'
    marks: int                  # 1 or 2
    section: str                # 'GA' or 'Subject'
    section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
    topic: str
    stem_tex: str               # Question text with LaTeX math
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None
    choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
    estimated_time_seconds: Optional[int] = None


class ExamScreenResponse(BaseModel):
    """Full exam data returned for the exam screen."""
    exam_id: str
    paper: str
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    questions: list[QuestionItem]   # Ordered by qno, NO answers


class AttemptStartResponse(BaseModel):
    """
    Response from POST /exams/{id}/start.
    Returns attempt ID, server start time, and any saved responses for resume.
    """
    attempt_id: str
    exam_id: str
    start_time: str         # ISO 8601 datetime string
    remaining_seconds: int  # Seconds left in the exam
    responses: dict         # Previously saved responses (for resume)
    question_statuses: dict # Previously saved statuses (for resume)
    submitted: bool         # True if already submitted (should not reach exam screen)
    is_resume: bool = False # True if resuming an existing attempt
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\exam.py
*Saved at: 3/24/2026, 9:59:46 AM*

**[REMOVED]**
```
(from line ~1)
import uuid

```
**[ADDED]**
```
1     from datetime import datetime
2     from typing import Optional
3     from uuid import UUID
```
**[REMOVED]**
```
(from line ~5)
from sqlalchemy import String, Integer, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

```
**[ADDED]**
```
5     from pydantic import BaseModel, field_validator
```
**[REMOVED]**
```
(from line ~7)
from app.core.database import Base

```
**[ADDED]**
```
8     # ── Existing schemas (unchanged) ──────────────────────────────────────────────
```
**[REMOVED]**
```
(from line ~10)
class Exam(Base):
    __tablename__ = "exams"

```
**[ADDED]**
```
10    class TypesRatio(BaseModel):
11        MCQ: float = 0.6
12        MSQ: float = 0.2
13        NAT: float = 0.2
```
**[REMOVED]**
```
(from line ~15)
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    paper: Mapped[str] = mapped_column(String(10), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    selected_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    use_pyq_reference: Mapped[bool] = mapped_column(Boolean, default=True)
    types_ratio: Mapped[dict] = mapped_column(
        JSON, default={"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
    )
    total_questions: Mapped[int] = mapped_column(Integer, default=65)
    total_marks: Mapped[int] = mapped_column(Integer, default=100)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=180)
    question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    question_order: Mapped[list] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="generated")
    generation_progress: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
```
**[ADDED]**
```
15        @field_validator("MCQ", "MSQ", "NAT")
16        @classmethod
17        def validate_ratio(cls, v: float) -> float:
18            if v < 0 or v > 1:
19                raise ValueError("Ratio values must be between 0 and 1")
20            return v
21    
22    
23    class ExamGenerateRequest(BaseModel):
24        paper: str
25        scope: str  # 'full' or 'topic'
26        selected_topics: Optional[list[str]] = None
27        difficulty: str  # 'easy', 'medium', 'hard', 'auto'
28        types_ratio: TypesRatio = TypesRatio()
29    
30        @field_validator("paper")
31        @classmethod
32        def validate_paper(cls, v: str) -> str:
33            v = v.upper()
34            if v not in ("CS", "DA"):
35                raise ValueError("paper must be 'CS' or 'DA'")
36            return v
37    
38        @field_validator("scope")
39        @classmethod
40        def validate_scope(cls, v: str) -> str:
41            v = v.lower()
42            if v not in ("full", "topic"):
43                raise ValueError("scope must be 'full' or 'topic'")
44            return v
45    
46        @field_validator("difficulty")
47        @classmethod
48        def validate_difficulty(cls, v: str) -> str:
49            v = v.lower()
50            if v not in ("easy", "medium", "hard", "auto"):
51                raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
52            return v
53    
54        @field_validator("selected_topics")
55        @classmethod
56        def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
57            return v
58    
59    
60    class ExamGenerateResponse(BaseModel):
61        exam_id: UUID
62        status: str
63        message: str
64    
65    
66    class ExamSummary(BaseModel):
67        id: UUID
68        paper: str
69        scope: str
70        selected_topics: Optional[list[str]] = None
71        difficulty: str
72        total_questions: int
73        total_marks: int
74        duration_minutes: int
75        status: str
76        created_at: datetime
77    
78        class Config:
79            from_attributes = True
80    
81    
82    # ── Part 8: Exam screen schemas ───────────────────────────────────────────────
83    
84    class QuestionItem(BaseModel):
85        """
86        Single question for the exam screen.
87        CRITICAL: Does NOT contain the answer field.
88        """
89        id: str
90        qno: int
91        question_type: str          # 'MCQ', 'MSQ', 'NAT'
92        marks: int                  # 1 or 2
93        section: str                # 'GA' or 'Subject'
94        section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
95        topic: str
96        stem_tex: str               # Question text with LaTeX math
97        code_snippet: Optional[str] = None
98        code_language: Optional[str] = None
99        choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
100       estimated_time_seconds: Optional[int] = None
101   
102   
103   class ExamScreenResponse(BaseModel):
104       """Full exam data returned for the exam screen."""
105       exam_id: str
106       paper: str
107       difficulty: str
108       total_questions: int
109       total_marks: int
110       duration_minutes: int
111       questions: list[QuestionItem]   # Ordered by qno, NO answers
112   
113   
114   class AttemptStartResponse(BaseModel):
115       """
116       Response from POST /exams/{id}/start.
117       Returns attempt ID, server start time, and any saved responses for resume.
118       """
119       attempt_id: str
120       exam_id: str
121       start_time: str         # ISO 8601 datetime string
122       remaining_seconds: int  # Seconds left in the exam
123       responses: dict         # Previously saved responses (for resume)
124       question_statuses: dict # Previously saved statuses (for resume)
125       submitted: bool         # True if already submitted (should not reach exam screen)
126       is_resume: bool = False # True if resuming an existing attempt
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\exam.py
*Saved at: 3/24/2026, 9:59:40 AM*

**[REMOVED]**
```
(from line ~1)
from datetime import datetime
from typing import Optional
from uuid import UUID

```
**[ADDED]**
```
1     import uuid
```
**[REMOVED]**
```
(from line ~3)
from pydantic import BaseModel, field_validator

```
**[ADDED]**
```
3     from sqlalchemy import String, Integer, JSON, Boolean, ForeignKey
4     from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
5     from sqlalchemy.orm import Mapped, mapped_column
6     from sqlalchemy import func
```
**[ADDED]**
```
8     from app.core.database import Base
```
**[REMOVED]**
```
(from line ~10)
# ── Existing schemas (unchanged) ──────────────────────────────────────────────

```
**[REMOVED]**
```
(from line ~11)
class TypesRatio(BaseModel):
    MCQ: float = 0.6
    MSQ: float = 0.2
    NAT: float = 0.2

```
**[ADDED]**
```
11    class Exam(Base):
12        __tablename__ = "exams"
```
**[REMOVED]**
```
(from line ~14)
    @field_validator("MCQ", "MSQ", "NAT")
    @classmethod
    def validate_ratio(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("Ratio values must be between 0 and 1")
        return v


class ExamGenerateRequest(BaseModel):
    paper: str
    scope: str  # 'full' or 'topic'
    selected_topics: Optional[list[str]] = None
    difficulty: str  # 'easy', 'medium', 'hard', 'auto'
    types_ratio: TypesRatio = TypesRatio()

    @field_validator("paper")
    @classmethod
    def validate_paper(cls, v: str) -> str:
        v = v.upper()
        if v not in ("CS", "DA"):
            raise ValueError("paper must be 'CS' or 'DA'")
        return v

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        v = v.lower()
        if v not in ("full", "topic"):
            raise ValueError("scope must be 'full' or 'topic'")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        v = v.lower()
        if v not in ("easy", "medium", "hard", "auto"):
            raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
        return v

    @field_validator("selected_topics")
    @classmethod
    def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
        return v


class ExamGenerateResponse(BaseModel):
    exam_id: UUID
    status: str
    message: str


class ExamSummary(BaseModel):
    id: UUID
    paper: str
    scope: str
    selected_topics: Optional[list[str]] = None
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Part 8: Exam screen schemas ───────────────────────────────────────────────

class QuestionItem(BaseModel):
    """
    Single question for the exam screen.
    CRITICAL: Does NOT contain the answer field.
    """
    id: str
    qno: int
    question_type: str          # 'MCQ', 'MSQ', 'NAT'
    marks: int                  # 1 or 2
    section: str                # 'GA' or 'Subject'
    section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
    topic: str
    stem_tex: str               # Question text with LaTeX math
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None
    choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
    estimated_time_seconds: Optional[int] = None


class ExamScreenResponse(BaseModel):
    """Full exam data returned for the exam screen."""
    exam_id: str
    paper: str
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    questions: list[QuestionItem]   # Ordered by qno, NO answers


class AttemptStartResponse(BaseModel):
    """
    Response from POST /exams/{id}/start.
    Returns attempt ID, server start time, and any saved responses for resume.
    """
    attempt_id: str
    exam_id: str
    start_time: str         # ISO 8601 datetime string
    remaining_seconds: int  # Seconds left in the exam
    responses: dict         # Previously saved responses (for resume)
    question_statuses: dict # Previously saved statuses (for resume)
    submitted: bool         # True if already submitted (should not reach exam screen)
    is_resume: bool = False # True if resuming an existing attempt
```
**[ADDED]**
```
14        id: Mapped[uuid.UUID] = mapped_column(
15            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
16        )
17        user_id: Mapped[uuid.UUID] = mapped_column(
18            PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
19        )
20        paper: Mapped[str] = mapped_column(String(10), nullable=False)
21        scope: Mapped[str] = mapped_column(String(20), nullable=False)
22        selected_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)
23        difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
24        use_pyq_reference: Mapped[bool] = mapped_column(Boolean, default=True)
25        types_ratio: Mapped[dict] = mapped_column(
26            JSON, default={"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
27        )
28        total_questions: Mapped[int] = mapped_column(Integer, default=65)
29        total_marks: Mapped[int] = mapped_column(Integer, default=100)
30        duration_minutes: Mapped[int] = mapped_column(Integer, default=180)
31        question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
32        question_order: Mapped[list] = mapped_column(JSON, nullable=False)
33        status: Mapped[str] = mapped_column(String(20), default="generated")
34        generation_progress: Mapped[dict | None] = mapped_column(JSON, nullable=True)
35        created_at: Mapped[str] = mapped_column(
36            TIMESTAMP(timezone=True), server_default=func.now()
37        )
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\exam.py
*Saved at: 3/24/2026, 9:58:57 AM*

**[REMOVED]**
```
(from line ~1)
import uuid

```
**[ADDED]**
```
1     from datetime import datetime
2     from typing import Optional
3     from uuid import UUID
```
**[REMOVED]**
```
(from line ~5)
from sqlalchemy import String, Integer, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

```
**[ADDED]**
```
5     from pydantic import BaseModel, field_validator
```
**[REMOVED]**
```
(from line ~7)
from app.core.database import Base

```
**[ADDED]**
```
8     # ── Existing schemas (unchanged) ──────────────────────────────────────────────
```
**[REMOVED]**
```
(from line ~10)
class Exam(Base):
    __tablename__ = "exams"

```
**[ADDED]**
```
10    class TypesRatio(BaseModel):
11        MCQ: float = 0.6
12        MSQ: float = 0.2
13        NAT: float = 0.2
```
**[REMOVED]**
```
(from line ~15)
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    paper: Mapped[str] = mapped_column(String(10), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    selected_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    use_pyq_reference: Mapped[bool] = mapped_column(Boolean, default=True)
    types_ratio: Mapped[dict] = mapped_column(
        JSON, default={"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
    )
    total_questions: Mapped[int] = mapped_column(Integer, default=65)
    total_marks: Mapped[int] = mapped_column(Integer, default=100)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=180)
    question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    question_order: Mapped[list] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="generated")
    generation_progress: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
```
**[ADDED]**
```
15        @field_validator("MCQ", "MSQ", "NAT")
16        @classmethod
17        def validate_ratio(cls, v: float) -> float:
18            if v < 0 or v > 1:
19                raise ValueError("Ratio values must be between 0 and 1")
20            return v
21    
22    
23    class ExamGenerateRequest(BaseModel):
24        paper: str
25        scope: str  # 'full' or 'topic'
26        selected_topics: Optional[list[str]] = None
27        difficulty: str  # 'easy', 'medium', 'hard', 'auto'
28        types_ratio: TypesRatio = TypesRatio()
29    
30        @field_validator("paper")
31        @classmethod
32        def validate_paper(cls, v: str) -> str:
33            v = v.upper()
34            if v not in ("CS", "DA"):
35                raise ValueError("paper must be 'CS' or 'DA'")
36            return v
37    
38        @field_validator("scope")
39        @classmethod
40        def validate_scope(cls, v: str) -> str:
41            v = v.lower()
42            if v not in ("full", "topic"):
43                raise ValueError("scope must be 'full' or 'topic'")
44            return v
45    
46        @field_validator("difficulty")
47        @classmethod
48        def validate_difficulty(cls, v: str) -> str:
49            v = v.lower()
50            if v not in ("easy", "medium", "hard", "auto"):
51                raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
52            return v
53    
54        @field_validator("selected_topics")
55        @classmethod
56        def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
57            return v
58    
59    
60    class ExamGenerateResponse(BaseModel):
61        exam_id: UUID
62        status: str
63        message: str
64    
65    
66    class ExamSummary(BaseModel):
67        id: UUID
68        paper: str
69        scope: str
70        selected_topics: Optional[list[str]] = None
71        difficulty: str
72        total_questions: int
73        total_marks: int
74        duration_minutes: int
75        status: str
76        created_at: datetime
77    
78        class Config:
79            from_attributes = True
80    
81    
82    # ── Part 8: Exam screen schemas ───────────────────────────────────────────────
83    
84    class QuestionItem(BaseModel):
85        """
86        Single question for the exam screen.
87        CRITICAL: Does NOT contain the answer field.
88        """
89        id: str
90        qno: int
91        question_type: str          # 'MCQ', 'MSQ', 'NAT'
92        marks: int                  # 1 or 2
93        section: str                # 'GA' or 'Subject'
94        section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
95        topic: str
96        stem_tex: str               # Question text with LaTeX math
97        code_snippet: Optional[str] = None
98        code_language: Optional[str] = None
99        choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
100       estimated_time_seconds: Optional[int] = None
101   
102   
103   class ExamScreenResponse(BaseModel):
104       """Full exam data returned for the exam screen."""
105       exam_id: str
106       paper: str
107       difficulty: str
108       total_questions: int
109       total_marks: int
110       duration_minutes: int
111       questions: list[QuestionItem]   # Ordered by qno, NO answers
112   
113   
114   class AttemptStartResponse(BaseModel):
115       """
116       Response from POST /exams/{id}/start.
117       Returns attempt ID, server start time, and any saved responses for resume.
118       """
119       attempt_id: str
120       exam_id: str
121       start_time: str         # ISO 8601 datetime string
122       remaining_seconds: int  # Seconds left in the exam
123       responses: dict         # Previously saved responses (for resume)
124       question_statuses: dict # Previously saved statuses (for resume)
125       submitted: bool         # True if already submitted (should not reach exam screen)
126       is_resume: bool = False # True if resuming an existing attempt
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\exam.py
*Saved at: 3/24/2026, 9:58:49 AM*

**[REMOVED]**
```
(from line ~1)
from datetime import datetime
from typing import Optional
from uuid import UUID

```
**[ADDED]**
```
1     import uuid
```
**[REMOVED]**
```
(from line ~3)
from pydantic import BaseModel, field_validator

```
**[ADDED]**
```
3     from sqlalchemy import String, Integer, JSON, Boolean, ForeignKey
4     from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
5     from sqlalchemy.orm import Mapped, mapped_column
6     from sqlalchemy import func
```
**[ADDED]**
```
8     from app.core.database import Base
```
**[REMOVED]**
```
(from line ~10)
# ── Existing schemas (unchanged) ──────────────────────────────────────────────

```
**[REMOVED]**
```
(from line ~11)
class TypesRatio(BaseModel):
    MCQ: float = 0.6
    MSQ: float = 0.2
    NAT: float = 0.2

```
**[ADDED]**
```
11    class Exam(Base):
12        __tablename__ = "exams"
```
**[REMOVED]**
```
(from line ~14)
    @field_validator("MCQ", "MSQ", "NAT")
    @classmethod
    def validate_ratio(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("Ratio values must be between 0 and 1")
        return v


class ExamGenerateRequest(BaseModel):
    paper: str
    scope: str  # 'full' or 'topic'
    selected_topics: Optional[list[str]] = None
    difficulty: str  # 'easy', 'medium', 'hard', 'auto'
    types_ratio: TypesRatio = TypesRatio()

    @field_validator("paper")
    @classmethod
    def validate_paper(cls, v: str) -> str:
        v = v.upper()
        if v not in ("CS", "DA"):
            raise ValueError("paper must be 'CS' or 'DA'")
        return v

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        v = v.lower()
        if v not in ("full", "topic"):
            raise ValueError("scope must be 'full' or 'topic'")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        v = v.lower()
        if v not in ("easy", "medium", "hard", "auto"):
            raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
        return v

    @field_validator("selected_topics")
    @classmethod
    def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
        return v


class ExamGenerateResponse(BaseModel):
    exam_id: UUID
    status: str
    message: str


class ExamSummary(BaseModel):
    id: UUID
    paper: str
    scope: str
    selected_topics: Optional[list[str]] = None
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Part 8: Exam screen schemas ───────────────────────────────────────────────

class QuestionItem(BaseModel):
    """
    Single question for the exam screen.
    CRITICAL: Does NOT contain the answer field.
    """
    id: str
    qno: int
    question_type: str          # 'MCQ', 'MSQ', 'NAT'
    marks: int                  # 1 or 2
    section: str                # 'GA' or 'Subject'
    section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
    topic: str
    stem_tex: str               # Question text with LaTeX math
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None
    choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
    estimated_time_seconds: Optional[int] = None


class ExamScreenResponse(BaseModel):
    """Full exam data returned for the exam screen."""
    exam_id: str
    paper: str
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    questions: list[QuestionItem]   # Ordered by qno, NO answers


class AttemptStartResponse(BaseModel):
    """
    Response from POST /exams/{id}/start.
    Returns attempt ID, server start time, and any saved responses for resume.
    """
    attempt_id: str
    exam_id: str
    start_time: str         # ISO 8601 datetime string
    remaining_seconds: int  # Seconds left in the exam
    responses: dict         # Previously saved responses (for resume)
    question_statuses: dict # Previously saved statuses (for resume)
    submitted: bool         # True if already submitted (should not reach exam screen)
    is_resume: bool = False # True if resuming an existing attempt
```
**[ADDED]**
```
14        id: Mapped[uuid.UUID] = mapped_column(
15            PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
16        )
17        user_id: Mapped[uuid.UUID] = mapped_column(
18            PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
19        )
20        paper: Mapped[str] = mapped_column(String(10), nullable=False)
21        scope: Mapped[str] = mapped_column(String(20), nullable=False)
22        selected_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)
23        difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
24        use_pyq_reference: Mapped[bool] = mapped_column(Boolean, default=True)
25        types_ratio: Mapped[dict] = mapped_column(
26            JSON, default={"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
27        )
28        total_questions: Mapped[int] = mapped_column(Integer, default=65)
29        total_marks: Mapped[int] = mapped_column(Integer, default=100)
30        duration_minutes: Mapped[int] = mapped_column(Integer, default=180)
31        question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
32        question_order: Mapped[list] = mapped_column(JSON, nullable=False)
33        status: Mapped[str] = mapped_column(String(20), default="generated")
34        generation_progress: Mapped[dict | None] = mapped_column(JSON, nullable=True)
35        created_at: Mapped[str] = mapped_column(
36            TIMESTAMP(timezone=True), server_default=func.now()
37        )
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\__init__.py
*Saved at: 3/24/2026, 9:57:35 AM*

**[REMOVED]**
```
(from line ~6)
from app.models.exam import Exam

```
**[ADDED]**
```
6     from app.models.exam import exam
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\package.json
*Saved at: 3/24/2026, 9:53:46 AM*

**[REMOVED]**
```
(from line ~31)
    "vite": "^8.0.0"

```
**[ADDED]**
```
31        "vite": "^7.3.0"
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\package.json
*Saved at: 3/24/2026, 9:50:51 AM*

**[REMOVED]**
```
(from line ~22)
        "@types/katex": "^0.16.7",

```
**[ADDED]**
```
22        "@types/katex": "^0.16.7",
```
**[REMOVED]**
```
(from line ~24)


```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\package.json
*Saved at: 3/24/2026, 9:50:48 AM*

**[REMOVED]**
```
(from line ~22)
    

```
**[ADDED]**
```
22            "@types/katex": "^0.16.7",
23        "@types/prismjs": "^1.26.4",
24    
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\package.json
*Saved at: 3/24/2026, 9:50:47 AM*

**[ADDED]**
```
22        
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\package.json
*Saved at: 3/24/2026, 9:50:35 AM*

**[REMOVED]**
```
(from line ~14)
        "katex": "^0.16.11",

```
**[ADDED]**
```
14        "katex": "^0.16.11",
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\package.json
*Saved at: 3/24/2026, 9:50:33 AM*

**[REMOVED]**
```
(from line ~16)


```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\package.json
*Saved at: 3/24/2026, 9:50:31 AM*

**[ADDED]**
```
14            "katex": "^0.16.11",
15        "prismjs": "^1.29.0",
16    
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\App.tsx
*Saved at: 3/24/2026, 9:49:34 AM*

**[ADDED]**
```
14    import ExamScreen from "./pages/ExamScreen";
```
**[ADDED]**
```
61              {/* Part 8: Exam Screen */}
```
**[ADDED]**
```
63                path="/exam/:examId"
64                element={
65                  <ProtectedRoute>
66                    <ExamScreen />
67                  </ProtectedRoute>
68                }
69              />
70              <Route
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\types\index.ts
*Saved at: 3/24/2026, 9:49:25 AM*

**[ADDED]**
```
69    /* ── Exam Screen (Part 8) ── */
70    
71    export type QuestionType = "MCQ" | "MSQ" | "NAT";
72    export type QuestionSection = "GA" | "Subject";
73    
74    /** Status of a question in the palette */
75    export type QuestionStatus =
76      | "not_visited"      // gray  — never opened
77      | "not_answered"     // red   — visited but no answer
78      | "answered"         // green — has an answer
79      | "marked"           // purple — marked for review, no answer
80      | "answered_marked"; // blue  — answered AND marked for review
81    
82    /** Single question item returned by GET /exams/{id} — NO answer field */
83    export interface QuestionItem {
84      id: string;
85      qno: number;
86      question_type: QuestionType;
87      marks: number;
88      section: QuestionSection;
89      section_name: string;
90      topic: string;
91      stem_tex: string;
92      code_snippet: string | null;
93      code_language: string | null;
94      choices: string[] | null;
95      estimated_time_seconds: number | null;
96    }
97    
98    /** Full exam data returned by GET /exams/{id} */
99    export interface ExamScreenData {
100     exam_id: string;
101     paper: string;
102     difficulty: string;
103     total_questions: number;
104     total_marks: number;
105     duration_minutes: number;
106     questions: QuestionItem[];
107   }
108   
109   /** Response from POST /exams/{id}/start */
110   export interface AttemptData {
111     attempt_id: string;
112     exam_id: string;
113     start_time: string;       // ISO 8601
114     remaining_seconds: number;
115     responses: Record<string, MCQAnswer | MSQAnswer | NATAnswer>;
116     question_statuses: Record<string, QuestionStatus>;
117     submitted: boolean;
118     is_resume: boolean;
119   }
120   
121   /** Answer types */
122   export interface MCQAnswer {
123     index: number;
124   }
125   export interface MSQAnswer {
126     indices: number[];
127   }
128   export interface NATAnswer {
129     value: string; // stored as string, parsed on submission
130   }
131   
132   export type AnyAnswer = MCQAnswer | MSQAnswer | NATAnswer;
133   
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\attempt.py
*Saved at: 3/24/2026, 9:48:51 AM*

**[ADDED]**
```
2     from datetime import datetime
```
**[REMOVED]**
```
(from line ~4)
from sqlalchemy import String, Float, Integer, JSON, ForeignKey, Boolean

```
**[ADDED]**
```
4     from sqlalchemy import String, Float, Integer, JSON, ForeignKey, Boolean, func
```
**[REMOVED]**
```
(from line ~18)
        PG_UUID(as_uuid=True), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True

```
**[ADDED]**
```
18            PG_UUID(as_uuid=True),
19            ForeignKey("exams.id", ondelete="CASCADE"),
20            nullable=False,
21            index=True,
```
**[REMOVED]**
```
(from line ~24)
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True

```
**[ADDED]**
```
24            PG_UUID(as_uuid=True),
25            ForeignKey("users.id", ondelete="CASCADE"),
26            nullable=False,
27            index=True,
```
**[REMOVED]**
```
(from line ~29)
    start_time: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    end_time: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

```
**[ADDED]**
```
29        start_time: Mapped[datetime | None] = mapped_column(
30            TIMESTAMP(timezone=True), nullable=True
31        )
32        end_time: Mapped[datetime | None] = mapped_column(
33            TIMESTAMP(timezone=True), nullable=True
34        )
```
**[REMOVED]**
```
(from line ~46)
    topic_analysis: Mapped[list | None] = mapped_column(JSON, nullable=True)
```
**[ADDED]**
```
46        topic_analysis: Mapped[list | None] = mapped_column(JSON, nullable=True)
47        created_at: Mapped[datetime] = mapped_column(
48            TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
49        )
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\models\exam.py
*Saved at: 3/24/2026, 9:48:39 AM*

**[REMOVED]**
```
(from line ~1)
import uuid

```
**[ADDED]**
```
1     from datetime import datetime
2     from typing import Optional
3     from uuid import UUID
```
**[REMOVED]**
```
(from line ~5)
from sqlalchemy import String, Integer, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

```
**[ADDED]**
```
5     from pydantic import BaseModel, field_validator
```
**[REMOVED]**
```
(from line ~7)
from app.core.database import Base

```
**[ADDED]**
```
8     # ── Existing schemas (unchanged) ──────────────────────────────────────────────
```
**[REMOVED]**
```
(from line ~10)
class Exam(Base):
    __tablename__ = "exams"

```
**[ADDED]**
```
10    class TypesRatio(BaseModel):
11        MCQ: float = 0.6
12        MSQ: float = 0.2
13        NAT: float = 0.2
```
**[REMOVED]**
```
(from line ~15)
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    paper: Mapped[str] = mapped_column(String(10), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    selected_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    use_pyq_reference: Mapped[bool] = mapped_column(Boolean, default=True)
    types_ratio: Mapped[dict] = mapped_column(
        JSON, default={"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
    )
    total_questions: Mapped[int] = mapped_column(Integer, default=65)
    total_marks: Mapped[int] = mapped_column(Integer, default=100)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=180)
    question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    question_order: Mapped[list] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="generated")
    generation_progress: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
```
**[ADDED]**
```
15        @field_validator("MCQ", "MSQ", "NAT")
16        @classmethod
17        def validate_ratio(cls, v: float) -> float:
18            if v < 0 or v > 1:
19                raise ValueError("Ratio values must be between 0 and 1")
20            return v
21    
22    
23    class ExamGenerateRequest(BaseModel):
24        paper: str
25        scope: str  # 'full' or 'topic'
26        selected_topics: Optional[list[str]] = None
27        difficulty: str  # 'easy', 'medium', 'hard', 'auto'
28        types_ratio: TypesRatio = TypesRatio()
29    
30        @field_validator("paper")
31        @classmethod
32        def validate_paper(cls, v: str) -> str:
33            v = v.upper()
34            if v not in ("CS", "DA"):
35                raise ValueError("paper must be 'CS' or 'DA'")
36            return v
37    
38        @field_validator("scope")
39        @classmethod
40        def validate_scope(cls, v: str) -> str:
41            v = v.lower()
42            if v not in ("full", "topic"):
43                raise ValueError("scope must be 'full' or 'topic'")
44            return v
45    
46        @field_validator("difficulty")
47        @classmethod
48        def validate_difficulty(cls, v: str) -> str:
49            v = v.lower()
50            if v not in ("easy", "medium", "hard", "auto"):
51                raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
52            return v
53    
54        @field_validator("selected_topics")
55        @classmethod
56        def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
57            return v
58    
59    
60    class ExamGenerateResponse(BaseModel):
61        exam_id: UUID
62        status: str
63        message: str
64    
65    
66    class ExamSummary(BaseModel):
67        id: UUID
68        paper: str
69        scope: str
70        selected_topics: Optional[list[str]] = None
71        difficulty: str
72        total_questions: int
73        total_marks: int
74        duration_minutes: int
75        status: str
76        created_at: datetime
77    
78        class Config:
79            from_attributes = True
80    
81    
82    # ── Part 8: Exam screen schemas ───────────────────────────────────────────────
83    
84    class QuestionItem(BaseModel):
85        """
86        Single question for the exam screen.
87        CRITICAL: Does NOT contain the answer field.
88        """
89        id: str
90        qno: int
91        question_type: str          # 'MCQ', 'MSQ', 'NAT'
92        marks: int                  # 1 or 2
93        section: str                # 'GA' or 'Subject'
94        section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
95        topic: str
96        stem_tex: str               # Question text with LaTeX math
97        code_snippet: Optional[str] = None
98        code_language: Optional[str] = None
99        choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
100       estimated_time_seconds: Optional[int] = None
101   
102   
103   class ExamScreenResponse(BaseModel):
104       """Full exam data returned for the exam screen."""
105       exam_id: str
106       paper: str
107       difficulty: str
108       total_questions: int
109       total_marks: int
110       duration_minutes: int
111       questions: list[QuestionItem]   # Ordered by qno, NO answers
112   
113   
114   class AttemptStartResponse(BaseModel):
115       """
116       Response from POST /exams/{id}/start.
117       Returns attempt ID, server start time, and any saved responses for resume.
118       """
119       attempt_id: str
120       exam_id: str
121       start_time: str         # ISO 8601 datetime string
122       remaining_seconds: int  # Seconds left in the exam
123       responses: dict         # Previously saved responses (for resume)
124       question_statuses: dict # Previously saved statuses (for resume)
125       submitted: bool         # True if already submitted (should not reach exam screen)
126       is_resume: bool = False # True if resuming an existing attempt
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\api\exams.py
*Saved at: 3/24/2026, 9:48:14 AM*

**[REMOVED]**
```
(from line ~2)
import uuid

```
**[ADDED]**
```
2     import uuid as uuid_module
3     from datetime import datetime, timezone
```
**[ADDED]**
```
13    from app.models.attempt import Attempt
```
**[REMOVED]**
```
(from line ~15)
from app.schemas.exam import ExamGenerateRequest, ExamGenerateResponse, ExamSummary

```
**[ADDED]**
```
15    from app.models.question_bank import QuestionBank
16    from app.schemas.exam import (
17        ExamGenerateRequest,
18        ExamGenerateResponse,
19        ExamSummary,
20        ExamScreenResponse,
21        QuestionItem,
22        AttemptStartResponse,
23    )
```
**[ADDED]**
```
29    # ── POST /exams/generate ──────────────────────────────────────────────────────
30    
```
**[REMOVED]**
```
(from line ~42)
    """
    Validates the exam configuration, creates an exam row with
    status 'generating', kicks off background generation, and returns exam_id.
    """


```
**[REMOVED]**
```
(from line ~64)
    # ── 3. If scope is 'topic', validate selected_topics ──

```
**[ADDED]**
```
64        # ── 3. Validate selected_topics if scope is 'topic' ──
```
**[REMOVED]**
```
(from line ~71)


```
**[REMOVED]**
```
(from line ~75)


```
**[REMOVED]**
```
(from line ~91)
    exam_id = uuid.uuid4()


```
**[ADDED]**
```
91        exam_id = uuid_module.uuid4()
```
**[REMOVED]**
```
(from line ~113)


```
**[ADDED]**
```
126   # ── GET /exams ────────────────────────────────────────────────────────────────
127   
```
**[REMOVED]**
```
(from line ~137)
    """Returns all exams created by the current user, newest first."""

```
**[REMOVED]**
```
(from line ~143)


```
**[ADDED]**
```
160   # ── GET /exams/{exam_id}/status ───────────────────────────────────────────────
161   
```
**[REMOVED]**
```
(from line ~167)
    exam_id: uuid.UUID,

```
**[ADDED]**
```
167       exam_id: uuid_module.UUID,
```
**[REMOVED]**
```
(from line ~171)
    """
    Returns current generation status and progress.
    Frontend polls this every 3 seconds during generation.
    """

```
**[REMOVED]**
```
(from line ~175)


```
**[REMOVED]**
```
(from line ~176)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found.",
        )

```
**[ADDED]**
```
176           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
```
**[REMOVED]**
```
(from line ~179)


```
**[ADDED]**
```
192   # ── POST /exams/{exam_id}/start ───────────────────────────────────────────────
193   
194   @router.post(
195       "/{exam_id}/start",
196       response_model=AttemptStartResponse,
197       summary="Start or resume an exam attempt",
198   )
199   async def start_exam(
200       exam_id: uuid_module.UUID,
201       user: User = Depends(get_current_user),
202       db: AsyncSession = Depends(get_db),
203   ):
204       """
205       Creates a new attempt for the exam, or resumes an existing in-progress one.
206       Records server-side start_time for the authoritative timer.
207       Returns the attempt with any previously saved responses (for resume).
208       """
209       # ── 1. Get exam ──
210       result = await db.execute(
211           select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
212       )
213       exam = result.scalar_one_or_none()
214       if exam is None:
215           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
216   
217       if exam.status == "generating":
218           raise HTTPException(
219               status_code=status.HTTP_400_BAD_REQUEST,
220               detail="Exam is still being generated. Please wait.",
221           )
222       if exam.status == "failed":
223           raise HTTPException(
224               status_code=status.HTTP_400_BAD_REQUEST,
225               detail="Exam generation failed. Please generate a new exam.",
226           )
227       if exam.status == "completed":
228           raise HTTPException(
229               status_code=status.HTTP_400_BAD_REQUEST,
230               detail="This exam has already been completed.",
231           )
232       if exam.status not in ("generated", "in_progress"):
233           raise HTTPException(
234               status_code=status.HTTP_400_BAD_REQUEST,
235               detail=f"Cannot start exam with status '{exam.status}'.",
236           )
237   
238       now = datetime.now(timezone.utc)
239       duration_seconds = exam.duration_minutes * 60
240   
241       # ── 2. Check for existing in-progress attempt (resume) ──
242       existing_result = await db.execute(
243           select(Attempt).where(
244               Attempt.exam_id == exam_id,
245               Attempt.user_id == user.id,
246               Attempt.submitted == False,  # noqa: E712
247           )
248       )
249       existing = existing_result.scalar_one_or_none()
250   
251       if existing is not None:
252           # Resume existing attempt
253           elapsed = (now - existing.start_time).total_seconds()
254           remaining = max(0, duration_seconds - int(elapsed))
255   
256           if remaining <= 0:
257               # Time has expired — auto-submit
258               existing.submitted = True
259               existing.auto_submitted = True
260               existing.end_time = now
261               exam.status = "completed"
262               await db.commit()
263               raise HTTPException(
264                   status_code=status.HTTP_400_BAD_REQUEST,
265                   detail="Exam time has expired. The attempt has been auto-submitted.",
266               )
267   
268           return AttemptStartResponse(
269               attempt_id=str(existing.id),
270               exam_id=str(exam.id),
271               start_time=existing.start_time.isoformat(),
272               remaining_seconds=remaining,
273               responses=existing.responses or {},
274               question_statuses=existing.question_statuses or {},
275               submitted=existing.submitted,
276               is_resume=True,
277           )
278   
279       # ── 3. Create new attempt ──
280       attempt = Attempt(
281           id=uuid_module.uuid4(),
282           exam_id=exam.id,
283           user_id=user.id,
284           start_time=now,
285           submitted=False,
286           auto_submitted=False,
287           responses={},
288           question_statuses={},
289           events_log=[],
290           max_score=exam.total_marks,
291       )
292       db.add(attempt)
293   
294       # Update exam status to in_progress
295       exam.status = "in_progress"
296       await db.commit()
297   
298       return AttemptStartResponse(
299           attempt_id=str(attempt.id),
300           exam_id=str(exam.id),
301           start_time=now.isoformat(),
302           remaining_seconds=duration_seconds,
303           responses={},
304           question_statuses={},
305           submitted=False,
306           is_resume=False,
307       )
308   
309   
310   # ── GET /exams/{exam_id} ──────────────────────────────────────────────────────
311   
312   @router.get(
313       "/{exam_id}",
314       response_model=ExamScreenResponse,
315       summary="Get exam questions for the exam screen (NO answers)",
316   )
317   async def get_exam(
318       exam_id: uuid_module.UUID,
319       user: User = Depends(get_current_user),
320       db: AsyncSession = Depends(get_db),
321   ):
322       """
323       Returns the exam with all questions in order, but WITHOUT correct answers.
324       Used by the exam screen to render questions.
325       """
326       # ── 1. Get exam ──
327       result = await db.execute(
328           select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
329       )
330       exam = result.scalar_one_or_none()
331       if exam is None:
332           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
333   
334       if exam.status == "generating":
335           raise HTTPException(
336               status_code=status.HTTP_400_BAD_REQUEST,
337               detail="Exam is still being generated.",
338           )
339       if exam.status == "failed":
340           raise HTTPException(
341               status_code=status.HTTP_400_BAD_REQUEST,
342               detail="Exam generation failed.",
343           )
344       if not exam.question_order:
345           raise HTTPException(
346               status_code=status.HTTP_400_BAD_REQUEST,
347               detail="Exam has no questions assembled yet.",
348           )
349   
350       # ── 2. Build question_id → order_entry map ──
351       question_order: list[dict] = exam.question_order
352       id_to_order: dict[str, dict] = {
353           entry["question_id"]: entry
354           for entry in question_order
355           if entry.get("question_id")
356       }
357   
358       # ── 3. Fetch questions from question_bank ──
359       valid_ids = list(id_to_order.keys())
360       if not valid_ids:
361           raise HTTPException(
362               status_code=status.HTTP_404_NOT_FOUND,
363               detail="No valid question IDs found in this exam.",
364           )
365   
366       # Convert string UUIDs to uuid objects for SQLAlchemy query
367       uuid_ids = []
368       for qid in valid_ids:
369           try:
370               uuid_ids.append(uuid_module.UUID(qid))
371           except ValueError:
372               pass
373   
374       qb_result = await db.execute(
375           select(QuestionBank).where(QuestionBank.id.in_(uuid_ids))
376       )
377       questions_map: dict[str, QuestionBank] = {
378           str(q.id): q for q in qb_result.scalars().all()
379       }
380   
381       # ── 4. Build ordered list without answers ──
382       questions: list[QuestionItem] = []
383       for entry in question_order:
384           qid = entry.get("question_id", "")
385           q = questions_map.get(qid)
386           if not q:
387               continue
388   
389           questions.append(
390               QuestionItem(
391                   id=str(q.id),
392                   qno=entry["qno"],
393                   question_type=q.question_type,
394                   marks=q.marks,
395                   section=entry.get("section", "Subject"),
396                   section_name=q.section_name,
397                   topic=q.topic,
398                   stem_tex=q.stem_tex,
399                   code_snippet=q.code_snippet,
400                   code_language=q.code_language,
401                   choices=q.choices,
402                   estimated_time_seconds=q.estimated_time_seconds,
403                   # NOTE: answer is intentionally excluded
404               )
405           )
406   
407       return ExamScreenResponse(
408           exam_id=str(exam.id),
409           paper=exam.paper,
410           difficulty=exam.difficulty,
411           total_questions=exam.total_questions,
412           total_marks=exam.total_marks,
413           duration_minutes=exam.duration_minutes,
414           questions=questions,
415       )
416   
417   
418   # ── DELETE /exams/{exam_id} ───────────────────────────────────────────────────
419   
```
**[REMOVED]**
```
(from line ~426)
    exam_id: uuid.UUID,

```
**[ADDED]**
```
426       exam_id: uuid_module.UUID,
```
**[REMOVED]**
```
(from line ~430)
    """Delete an exam and its associated data."""

```
**[REMOVED]**
```
(from line ~434)


```
**[REMOVED]**
```
(from line ~435)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found.",
        )

```
**[ADDED]**
```
435           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\pages\ExamScreen.tsx
*Saved at: 3/24/2026, 9:47:37 AM*

**[ADDED]**
```
1     /**
2      * ExamScreen — Part 8
3      *
4      * Full exam-taking UI:
5      *  • Two-panel layout  (question display left + palette right)
6      *  • Section tabs      (GA / Subject)
7      *  • Question palette  (color-coded by status)
8      *  • KaTeX math        (via katex npm package)
9      *  • Prism.js code     (syntax highlighting)
10     *  • MCQ / MSQ / NAT   (radio / checkbox / numeric)
11     *  • Navigation        (Previous, Save & Next, Mark for Review, Clear)
12     *  • POST /exams/{id}/start   → creates / resumes attempt
13     *  • GET  /exams/{id}         → loads questions (no answers)
14     */
15    
16    import { useEffect, useState, useCallback, useMemo, useRef } from "react";
17    import { useParams, useNavigate } from "react-router-dom";
18    import toast from "react-hot-toast";
19    
20    import api from "../services/api";
21    import LoadingSpinner from "../components/common/LoadingSpinner";
22    import type {
23      QuestionItem,
24      QuestionStatus,
25      QuestionSection,
26      ExamScreenData,
27      AttemptData,
28      MCQAnswer,
29      MSQAnswer,
30      NATAnswer,
31      AnyAnswer,
32    } from "../types";
33    
34    // ── KaTeX ─────────────────────────────────────────────────────────────────────
35    // Imported dynamically to avoid build failure if not installed.
36    // Run: npm install katex @types/katex
37    let katex: any = null;
38    try {
39      // @ts-ignore
40      katex = await import("katex").then((m) => m.default ?? m);
41    } catch {
42      // katex not installed — math will display as raw text
43    }
44    
45    // ── Prism.js ──────────────────────────────────────────────────────────────────
46    // Run: npm install prismjs @types/prismjs
47    let Prism: any = null;
48    try {
49      // @ts-ignore
50      Prism = await import("prismjs").then((m) => m.default ?? m);
51      // @ts-ignore
52      await import("prismjs/components/prism-python");
53      // @ts-ignore
54      await import("prismjs/components/prism-c");
55    } catch {
56      // prismjs not installed — code will display without highlighting
57    }
58    
59    // ── Status colours ─────────────────────────────────────────────────────────────
60    
61    const STATUS_BG: Record<QuestionStatus, string> = {
62      not_visited:     "bg-gray-200 text-gray-700 hover:bg-gray-300",
63      not_answered:    "bg-red-500  text-white   hover:bg-red-600",
64      answered:        "bg-green-500 text-white  hover:bg-green-600",
65      marked:          "bg-purple-500 text-white hover:bg-purple-600",
66      answered_marked: "bg-blue-500 text-white   hover:bg-blue-600",
67    };
68    
69    const STATUS_LEGEND: { status: QuestionStatus; label: string; bg: string }[] = [
70      { status: "answered",        label: "Answered",          bg: "bg-green-500"  },
71      { status: "not_answered",    label: "Not Answered",      bg: "bg-red-500"    },
72      { status: "marked",          label: "Marked for Review", bg: "bg-purple-500" },
73      { status: "answered_marked", label: "Answered & Marked", bg: "bg-blue-500"   },
74      { status: "not_visited",     label: "Not Visited",       bg: "bg-gray-200 border border-gray-400"   },
75    ];
76    
77    // ── Math renderer ─────────────────────────────────────────────────────────────
78    
79    function MathText({ text }: { text: string }) {
80      const rendered = useMemo(() => {
81        if (!katex) return null;
82        try {
83          // Split on $$...$$ (display) then $...$ (inline)
84          const parts: Array<{ type: "text" | "display" | "inline"; content: string }> = [];
85    
86          // Step 1: split on display math $$...$$
87          const displaySplit = text.split(/(\$\$[\s\S]*?\$\$)/g);
88          const stage1: Array<{ type: "text" | "display"; content: string }> = [];
89          for (const chunk of displaySplit) {
90            if (chunk.startsWith("$$") && chunk.endsWith("$$") && chunk.length > 4) {
91              stage1.push({ type: "display", content: chunk.slice(2, -2) });
92            } else {
93              stage1.push({ type: "text", content: chunk });
94            }
95          }
96    
97          // Step 2: split text chunks on inline math $...$
98          for (const s1 of stage1) {
99            if (s1.type === "display") {
100             parts.push(s1);
101           } else {
102             const inlineSplit = s1.content.split(/(\$[^$\n]+?\$)/g);
103             for (const chunk of inlineSplit) {
104               if (chunk.startsWith("$") && chunk.endsWith("$") && chunk.length > 2) {
105                 parts.push({ type: "inline", content: chunk.slice(1, -1) });
106               } else {
107                 parts.push({ type: "text", content: chunk });
108               }
109             }
110           }
111         }
112   
113         // Step 3: render
114         const htmlParts: string[] = parts.map((p) => {
115           if (p.type === "display") {
116             try {
117               return katex.renderToString(p.content, {
118                 displayMode: true,
119                 throwOnError: false,
120                 trust: false,
121               });
122             } catch {
123               return `<span class="text-red-500">[Math Error]</span>`;
124             }
125           } else if (p.type === "inline") {
126             try {
127               return katex.renderToString(p.content, {
128                 displayMode: false,
129                 throwOnError: false,
130                 trust: false,
131               });
132             } catch {
133               return `<span class="text-red-500">[Math Error]</span>`;
134             }
135           } else {
136             // Preserve newlines as <br>
137             return p.content
138               .replace(/&/g, "&amp;")
139               .replace(/</g, "&lt;")
140               .replace(/>/g, "&gt;")
141               .replace(/\n/g, "<br/>");
142           }
143         });
144   
145         return htmlParts.join("");
146       } catch {
147         return null;
148       }
149     }, [text]);
150   
151     if (rendered !== null) {
152       return (
153         <span
154           className="math-text leading-relaxed"
155           dangerouslySetInnerHTML={{ __html: rendered }}
156         />
157       );
158     }
159   
160     // Fallback: plain text if katex not available
161     return <span className="leading-relaxed whitespace-pre-wrap">{text}</span>;
162   }
163   
164   // ── Code block ─────────────────────────────────────────────────────────────────
165   
166   function CodeBlock({ code, language }: { code: string; language: string | null }) {
167     const ref = useRef<HTMLElement>(null);
168   
169     useEffect(() => {
170       if (Prism && ref.current) {
171         Prism.highlightElement(ref.current);
172       }
173     }, [code]);
174   
175     const langClass = language === "python" ? "language-python" : "language-c";
176   
177     return (
178       <div className="my-4 overflow-x-auto rounded-lg border border-gray-200 bg-gray-900">
179         <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
180           <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
181             {language ?? "code"}
182           </span>
183         </div>
184         <pre className="p-4 overflow-x-auto text-sm">
185           <code ref={ref} className={langClass}>
186             {code}
187           </code>
188         </pre>
189       </div>
190     );
191   }
192   
193   // ── Answer components ──────────────────────────────────────────────────────────
194   
195   function MCQOptions({
196     choices,
197     selected,
198     onChange,
199   }: {
200     choices: string[];
201     selected: number | null;
202     onChange: (idx: number) => void;
203   }) {
204     const labels = ["(A)", "(B)", "(C)", "(D)"];
205     return (
206       <div className="space-y-3 mt-4">
207         {choices.map((choice, idx) => (
208           <label
209             key={idx}
210             className={`flex items-start gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
211               selected === idx
212                 ? "border-blue-500 bg-blue-50"
213                 : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
214             }`}
215           >
216             <div className="flex-shrink-0 mt-0.5">
217               <div
218                 className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
219                   selected === idx
220                     ? "border-blue-500 bg-blue-500"
221                     : "border-gray-400"
222                 }`}
223               >
224                 {selected === idx && (
225                   <div className="w-2 h-2 rounded-full bg-white" />
226                 )}
227               </div>
228             </div>
229             <input
230               type="radio"
231               className="sr-only"
232               checked={selected === idx}
233               onChange={() => onChange(idx)}
234             />
235             <span className="flex gap-2 text-sm text-gray-800">
236               <span className="font-medium text-gray-500 flex-shrink-0">{labels[idx]}</span>
237               <MathText text={choice} />
238             </span>
239           </label>
240         ))}
241       </div>
242     );
243   }
244   
245   function MSQOptions({
246     choices,
247     selected,
248     onChange,
249   }: {
250     choices: string[];
251     selected: number[];
252     onChange: (indices: number[]) => void;
253   }) {
254     const labels = ["(A)", "(B)", "(C)", "(D)"];
255   
256     const toggle = (idx: number) => {
257       if (selected.includes(idx)) {
258         onChange(selected.filter((i) => i !== idx));
259       } else {
260         onChange([...selected, idx].sort((a, b) => a - b));
261       }
262     };
263   
264     return (
265       <div className="space-y-3 mt-4">
266         <p className="text-xs text-purple-700 font-medium bg-purple-50 border border-purple-200 px-3 py-1.5 rounded-lg inline-block">
267           Select one or more correct answers
268         </p>
269         {choices.map((choice, idx) => (
270           <label
271             key={idx}
272             className={`flex items-start gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
273               selected.includes(idx)
274                 ? "border-purple-500 bg-purple-50"
275                 : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
276             }`}
277           >
278             <div className="flex-shrink-0 mt-0.5">
279               <div
280                 className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
281                   selected.includes(idx)
282                     ? "border-purple-500 bg-purple-500"
283                     : "border-gray-400"
284                 }`}
285               >
286                 {selected.includes(idx) && (
287                   <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
288                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
289                   </svg>
290                 )}
291               </div>
292             </div>
293             <input
294               type="checkbox"
295               className="sr-only"
296               checked={selected.includes(idx)}
297               onChange={() => toggle(idx)}
298             />
299             <span className="flex gap-2 text-sm text-gray-800">
300               <span className="font-medium text-gray-500 flex-shrink-0">{labels[idx]}</span>
301               <MathText text={choice} />
302             </span>
303           </label>
304         ))}
305       </div>
306     );
307   }
308   
309   function NATInput({
310     value,
311     onChange,
312   }: {
313     value: string;
314     onChange: (v: string) => void;
315   }) {
316     return (
317       <div className="mt-4">
318         <p className="text-xs text-orange-700 font-medium bg-orange-50 border border-orange-200 px-3 py-1.5 rounded-lg inline-block mb-3">
319           Numerical Answer Type — enter a numeric value
320         </p>
321         <div className="flex items-center gap-3">
322           <input
323             type="number"
324             step="any"
325             value={value}
326             onChange={(e) => onChange(e.target.value)}
327             placeholder="Enter your answer..."
328             className="w-64 px-4 py-2.5 rounded-lg border-2 border-gray-300 text-sm font-mono
329                        focus:border-orange-400 focus:ring-1 focus:ring-orange-400 focus:outline-none
330                        placeholder-gray-400"
331           />
332           {value && (
333             <span className="text-sm text-gray-500">
334               Your answer: <strong className="text-gray-900">{value}</strong>
335             </span>
336           )}
337         </div>
338       </div>
339     );
340   }
341   
342   // ── Question palette ───────────────────────────────────────────────────────────
343   
344   function QuestionPalette({
345     questions,
346     questionStatuses,
347     currentQno,
348     activeSection,
349     onNavigate,
350     onSectionChange,
351     onSubmit,
352     responses,
353   }: {
354     questions: QuestionItem[];
355     questionStatuses: Record<string, QuestionStatus>;
356     currentQno: number;
357     activeSection: "all" | QuestionSection;
358     onNavigate: (qno: number) => void;
359     onSectionChange: (section: "all" | QuestionSection) => void;
360     onSubmit: () => void;
361     responses: Record<string, AnyAnswer>;
362   }) {
363     const gaQuestions = questions.filter((q) => q.section === "GA");
364     const subjectQuestions = questions.filter((q) => q.section === "Subject");
365   
366     const filteredQuestions =
367       activeSection === "GA"
368         ? gaQuestions
369         : activeSection === "Subject"
370         ? subjectQuestions
371         : questions;
372   
373     // Compute summary counts
374     const counts = useMemo(() => {
375       let answered = 0, notAnswered = 0, marked = 0, answeredMarked = 0, notVisited = 0;
376       for (const q of questions) {
377         const st = questionStatuses[q.id] ?? "not_visited";
378         if (st === "answered") answered++;
379         else if (st === "not_answered") notAnswered++;
380         else if (st === "marked") marked++;
381         else if (st === "answered_marked") answeredMarked++;
382         else notVisited++;
383       }
384       return { answered, notAnswered, marked, answeredMarked, notVisited };
385     }, [questions, questionStatuses]);
386   
387     return (
388       <div className="w-64 flex-shrink-0 flex flex-col bg-white border-l border-gray-200 h-full">
389         {/* Section tabs */}
390         <div className="flex border-b border-gray-200 text-xs font-medium">
391           {(["all", "GA", "Subject"] as const).map((sec) => (
392             <button
393               key={sec}
394               onClick={() => onSectionChange(sec)}
395               className={`flex-1 py-2 transition-colors ${
396                 activeSection === sec
397                   ? "border-b-2 border-blue-600 text-blue-700 bg-blue-50"
398                   : "text-gray-600 hover:bg-gray-50"
399               }`}
400             >
401               {sec === "all" ? "All" : sec === "GA" ? `GA (${gaQuestions.length})` : `Subject (${subjectQuestions.length})`}
402             </button>
403           ))}
404         </div>
405   
406         {/* Summary legend */}
407         <div className="px-3 py-3 border-b border-gray-100 space-y-1.5">
408           {STATUS_LEGEND.map(({ status, label, bg }) => {
409             const count =
410               status === "answered" ? counts.answered
411               : status === "not_answered" ? counts.notAnswered
412               : status === "marked" ? counts.marked
413               : status === "answered_marked" ? counts.answeredMarked
414               : counts.notVisited;
415             return (
416               <div key={status} className="flex items-center gap-2 text-xs text-gray-700">
417                 <div className={`w-5 h-5 rounded flex-shrink-0 ${bg}`} />
418                 <span className="flex-1">{label}</span>
419                 <span className="font-semibold">{count}</span>
420               </div>
421             );
422           })}
423         </div>
424   
425         {/* Question grid */}
426         <div className="flex-1 overflow-y-auto p-3">
427           <div className="grid grid-cols-5 gap-1">
428             {filteredQuestions.map((q) => {
429               const status = questionStatuses[q.id] ?? "not_visited";
430               const isCurrent = q.qno === currentQno;
431               return (
432                 <button
433                   key={q.id}
434                   onClick={() => onNavigate(q.qno)}
435                   title={`Q${q.qno} — ${q.question_type} — ${q.marks}M — ${status.replace("_", " ")}`}
436                   className={`
437                     w-10 h-10 rounded text-xs font-semibold transition-all
438                     ${STATUS_BG[status]}
439                     ${isCurrent ? "ring-2 ring-offset-1 ring-gray-800 scale-110" : ""}
440                   `}
441                 >
442                   {q.qno}
443                 </button>
444               );
445             })}
446           </div>
447         </div>
448   
449         {/* Submit button */}
450         <div className="p-3 border-t border-gray-200">
451           <button
452             onClick={onSubmit}
453             className="w-full bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors"
454           >
455             Submit Exam
456           </button>
457           <p className="text-xs text-gray-400 text-center mt-1.5">
458             {counts.answered + counts.answeredMarked}/{questions.length} answered
459           </p>
460         </div>
461       </div>
462     );
463   }
464   
465   // ── Main ExamScreen component ─────────────────────────────────────────────────
466   
467   export default function ExamScreen() {
468     const { examId } = useParams<{ examId: string }>();
469     const navigate = useNavigate();
470   
471     // ── Data state ──────────────────────────────────────────────────────────────
472     const [exam, setExam] = useState<ExamScreenData | null>(null);
473     const [attempt, setAttempt] = useState<AttemptData | null>(null);
474     const [loadingExam, setLoadingExam] = useState(true);
475     const [loadingStart, setLoadingStart] = useState(true);
476     const [error, setError] = useState<string | null>(null);
477   
478     // ── Answer / navigation state ───────────────────────────────────────────────
479     const [currentQno, setCurrentQno] = useState(1);
480     const [responses, setResponses] = useState<Record<string, AnyAnswer>>({});
481     const [questionStatuses, setQuestionStatuses] = useState<Record<string, QuestionStatus>>({});
482     const [activeSection, setActiveSection] = useState<"all" | QuestionSection>("all");
483     const [showSubmitModal, setShowSubmitModal] = useState(false);
484   
485     // ── Load exam questions ─────────────────────────────────────────────────────
486     useEffect(() => {
487       if (!examId) return;
488       const load = async () => {
489         try {
490           const { data } = await api.get<ExamScreenData>(`/exams/${examId}`);
491           setExam(data);
492         } catch (err: any) {
493           const msg = err?.response?.data?.detail ?? "Failed to load exam questions.";
494           setError(msg);
495           toast.error(msg);
496         } finally {
497           setLoadingExam(false);
498         }
499       };
500       load();
501     }, [examId]);
502   
503     // ── Start / resume attempt ──────────────────────────────────────────────────
504     useEffect(() => {
505       if (!examId || loadingExam || error) return;
506       const start = async () => {
507         try {
508           const { data } = await api.post<AttemptData>(`/exams/${examId}/start`, {});
509           setAttempt(data);
510   
511           // Restore saved responses & statuses (resume)
512           if (data.responses && Object.keys(data.responses).length > 0) {
513             setResponses(data.responses as Record<string, AnyAnswer>);
514           }
515           if (data.question_statuses && Object.keys(data.question_statuses).length > 0) {
516             setQuestionStatuses(data.question_statuses as Record<string, QuestionStatus>);
517           }
518   
519           if (data.is_resume) {
520             toast.success("Resuming your exam session.", { icon: "🔄" });
521           }
522         } catch (err: any) {
523           const msg = err?.response?.data?.detail ?? "Failed to start exam attempt.";
524           setError(msg);
525           toast.error(msg);
526         } finally {
527           setLoadingStart(false);
528         }
529       };
530       start();
531     }, [examId, loadingExam, error]);
532   
533     // ── Derived values ──────────────────────────────────────────────────────────
534     const questions = exam?.questions ?? [];
535   
536     const currentQuestion = useMemo(
537       () => questions.find((q) => q.qno === currentQno) ?? null,
538       [questions, currentQno]
539     );
540   
541     // ── Mark question as visited when navigating to it ─────────────────────────
542     const markVisited = useCallback(
543       (question: QuestionItem) => {
544         setQuestionStatuses((prev) => {
545           const current = prev[question.id] ?? "not_visited";
546           if (current === "not_visited") {
547             return { ...prev, [question.id]: "not_answered" };
548           }
549           return prev;
550         });
551       },
552       []
553     );
554   
555     // When currentQno changes, mark the new question as visited
556     useEffect(() => {
557       if (currentQuestion) markVisited(currentQuestion);
558     }, [currentQno, currentQuestion, markVisited]);
559   
560     // ── Answer handlers ─────────────────────────────────────────────────────────
561   
562     const handleAnswerMCQ = useCallback(
563       (idx: number) => {
564         if (!currentQuestion) return;
565         const qid = currentQuestion.id;
566         const answer: MCQAnswer = { index: idx };
567         setResponses((prev) => ({ ...prev, [qid]: answer }));
568         setQuestionStatuses((prev) => {
569           const current = prev[qid] ?? "not_visited";
570           const next = current === "marked" || current === "answered_marked"
571             ? "answered_marked"
572             : "answered";
573           return { ...prev, [qid]: next };
574         });
575       },
576       [currentQuestion]
577     );
578   
579     const handleAnswerMSQ = useCallback(
580       (indices: number[]) => {
581         if (!currentQuestion) return;
582         const qid = currentQuestion.id;
583         if (indices.length === 0) {
584           // Treat as cleared
585           setResponses((prev) => {
586             const next = { ...prev };
587             delete next[qid];
588             return next;
589           });
590           setQuestionStatuses((prev) => {
591             const current = prev[qid] ?? "not_answered";
592             const next = current === "answered_marked" ? "marked" : "not_answered";
593             return { ...prev, [qid]: next };
594           });
595         } else {
596           const answer: MSQAnswer = { indices };
597           setResponses((prev) => ({ ...prev, [qid]: answer }));
598           setQuestionStatuses((prev) => {
599             const current = prev[qid] ?? "not_visited";
600             const next = current === "marked" || current === "answered_marked"
601               ? "answered_marked"
602               : "answered";
603             return { ...prev, [qid]: next };
604           });
605         }
606       },
607       [currentQuestion]
608     );
609   
610     const handleAnswerNAT = useCallback(
611       (value: string) => {
612         if (!currentQuestion) return;
613         const qid = currentQuestion.id;
614         if (value.trim() === "") {
615           setResponses((prev) => {
616             const next = { ...prev };
617             delete next[qid];
618             return next;
619           });
620           setQuestionStatuses((prev) => {
621             const current = prev[qid] ?? "not_answered";
622             const next = current === "answered_marked" ? "marked" : "not_answered";
623             return { ...prev, [qid]: next };
624           });
625         } else {
626           const answer: NATAnswer = { value };
627           setResponses((prev) => ({ ...prev, [qid]: answer }));
628           setQuestionStatuses((prev) => {
629             const current = prev[qid] ?? "not_visited";
630             const next = current === "marked" || current === "answered_marked"
631               ? "answered_marked"
632               : "answered";
633             return { ...prev, [qid]: next };
634           });
635         }
636       },
637       [currentQuestion]
638     );
639   
640     // ── Navigation handlers ─────────────────────────────────────────────────────
641   
642     const handleNavigateTo = useCallback(
643       (qno: number) => {
644         setCurrentQno(qno);
645       },
646       []
647     );
648   
649     const handlePrevious = useCallback(() => {
650       if (currentQno > 1) {
651         setCurrentQno((n) => n - 1);
652       }
653     }, [currentQno]);
654   
655     const handleSaveAndNext = useCallback(() => {
656       // If no answer yet for MCQ/MSQ, mark as not_answered (already done by markVisited)
657       const nextQno = currentQno + 1;
658       if (nextQno <= questions.length) {
659         setCurrentQno(nextQno);
660       }
661     }, [currentQno, questions.length]);
662   
663     const handleMarkForReview = useCallback(() => {
664       if (!currentQuestion) return;
665       const qid = currentQuestion.id;
666       setQuestionStatuses((prev) => {
667         const hasAnswer = !!responses[qid];
668         const next: QuestionStatus = hasAnswer ? "answered_marked" : "marked";
669         return { ...prev, [qid]: next };
670       });
671       // Navigate to next question
672       const nextQno = currentQno + 1;
673       if (nextQno <= questions.length) {
674         setCurrentQno(nextQno);
675       }
676     }, [currentQuestion, responses, currentQno, questions.length]);
677   
678     const handleClearResponse = useCallback(() => {
679       if (!currentQuestion) return;
680       const qid = currentQuestion.id;
681       setResponses((prev) => {
682         const next = { ...prev };
683         delete next[qid];
684         return next;
685       });
686       setQuestionStatuses((prev) => {
687         const current = prev[qid] ?? "not_answered";
688         const next: QuestionStatus =
689           current === "answered_marked" ? "marked" : "not_answered";
690         return { ...prev, [qid]: next };
691       });
692     }, [currentQuestion]);
693   
694     // ── Submit ──────────────────────────────────────────────────────────────────
695   
696     const handleSubmit = useCallback(() => {
697       setShowSubmitModal(true);
698     }, []);
699   
700     // ── Loading / error states ──────────────────────────────────────────────────
701   
702     if (loadingExam || loadingStart) {
703       return <LoadingSpinner fullScreen />;
704     }
705   
706     if (error) {
707       return (
708         <div className="min-h-screen flex items-center justify-center bg-gray-50">
709           <div className="text-center max-w-md p-8 bg-white rounded-xl border border-red-200">
710             <div className="text-4xl mb-4">⚠️</div>
711             <h2 className="text-lg font-bold text-gray-900 mb-2">Cannot Start Exam</h2>
712             <p className="text-sm text-red-600 mb-6">{error}</p>
713             <button
714               onClick={() => navigate("/dashboard")}
715               className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700"
716             >
717               Back to Dashboard
718             </button>
719           </div>
720         </div>
721       );
722     }
723   
724     if (!exam || !currentQuestion) {
725       return <LoadingSpinner fullScreen />;
726     }
727   
728     // ── Current answer ──────────────────────────────────────────────────────────
729     const currentAnswer = responses[currentQuestion.id];
730     const mcqSelected =
731       currentQuestion.question_type === "MCQ" && currentAnswer
732         ? (currentAnswer as MCQAnswer).index
733         : null;
734     const msqSelected =
735       currentQuestion.question_type === "MSQ" && currentAnswer
736         ? (currentAnswer as MSQAnswer).indices ?? []
737         : [];
738     const natValue =
739       currentQuestion.question_type === "NAT" && currentAnswer
740         ? (currentAnswer as NATAnswer).value ?? ""
741         : "";
742   
743     const currentStatus = questionStatuses[currentQuestion.id] ?? "not_visited";
744     const isCurrentMarked =
745       currentStatus === "marked" || currentStatus === "answered_marked";
746   
747     // ── Summary counts for submit modal ────────────────────────────────────────
748     const summaryForModal = useMemo(() => {
749       let answered = 0, notAnswered = 0, notVisited = 0, marked = 0;
750       for (const q of questions) {
751         const st = questionStatuses[q.id] ?? "not_visited";
752         if (st === "answered" || st === "answered_marked") answered++;
753         else if (st === "not_answered") notAnswered++;
754         else if (st === "marked") marked++;
755         else notVisited++;
756       }
757       return { answered, notAnswered, notVisited, marked };
758     }, [questions, questionStatuses]);
759   
760     // ── Type badge ──────────────────────────────────────────────────────────────
761     const typeBadgeClass =
762       currentQuestion.question_type === "MCQ"
763         ? "bg-blue-100 text-blue-700"
764         : currentQuestion.question_type === "MSQ"
765         ? "bg-purple-100 text-purple-700"
766         : "bg-orange-100 text-orange-700";
767   
768     // ── Render ──────────────────────────────────────────────────────────────────
769     return (
770       <div className="h-screen flex flex-col bg-gray-100 overflow-hidden">
771   
772         {/* ── Top bar ── */}
773         <div className="flex-shrink-0 bg-blue-800 text-white px-4 py-2 flex items-center justify-between shadow-md">
774           <div className="flex items-center gap-3">
775             <span className="text-lg font-bold">GATE 2026 Mock Test</span>
776             <span className="text-blue-300">|</span>
777             <span className="text-sm text-blue-200">
778               Paper: <strong className="text-white">{exam.paper}</strong>
779             </span>
780             <span className="text-blue-300">|</span>
781             <span className="text-sm text-blue-200">
782               <strong className="text-white capitalize">{exam.difficulty}</strong> difficulty
783             </span>
784             <span className="text-blue-300">|</span>
785             <span className="text-sm text-blue-200">
786               <strong className="text-white">{exam.total_questions}</strong> Qs ·{" "}
787               <strong className="text-white">{exam.total_marks}</strong> Marks
788             </span>
789           </div>
790   
791           {/* Timer placeholder (Part 9) */}
792           <div className="flex items-center gap-4">
793             <div className="bg-blue-900 px-4 py-1.5 rounded-lg">
794               <span className="text-sm font-mono font-bold tracking-wider">
795                 ⏱ {Math.floor((attempt?.remaining_seconds ?? exam.duration_minutes * 60) / 3600)
796                     .toString().padStart(2, "0")}:
797                 {Math.floor(((attempt?.remaining_seconds ?? exam.duration_minutes * 60) % 3600) / 60)
798                     .toString().padStart(2, "0")}:
799                 {((attempt?.remaining_seconds ?? exam.duration_minutes * 60) % 60)
800                     .toString().padStart(2, "0")}
801               </span>
802             </div>
803             <button
804               onClick={() => navigate("/dashboard")}
805               className="text-xs text-blue-300 hover:text-white transition-colors"
806             >
807               ✕ Exit
808             </button>
809           </div>
810         </div>
811   
812         {/* ── Main body ── */}
813         <div className="flex-1 flex overflow-hidden">
814   
815           {/* ── Left: Question display ── */}
816           <div className="flex-1 flex flex-col overflow-hidden">
817   
818             {/* Question header */}
819             <div className="flex-shrink-0 bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-3">
820               <span className="text-sm font-bold text-gray-800">
821                 Question {currentQuestion.qno} of {questions.length}
822               </span>
823               <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${typeBadgeClass}`}>
824                 {currentQuestion.question_type}
825               </span>
826               <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-gray-100 text-gray-700">
827                 {currentQuestion.marks} Mark{currentQuestion.marks > 1 ? "s" : ""}
828               </span>
829               <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700">
830                 {currentQuestion.section_name}
831               </span>
832               {currentQuestion.marks === 1 ? (
833                 <span className="text-xs text-red-600 ml-auto">
834                   Wrong answer: −{(1/3).toFixed(2)} marks
835                 </span>
836               ) : currentQuestion.marks === 2 && currentQuestion.question_type === "MCQ" ? (
837                 <span className="text-xs text-red-600 ml-auto">
838                   Wrong answer: −{(2/3).toFixed(2)} marks
839                 </span>
840               ) : (
841                 <span className="text-xs text-green-700 ml-auto">
842                   No negative marking
843                 </span>
844               )}
845             </div>
846   
847             {/* Question content (scrollable) */}
848             <div className="flex-1 overflow-y-auto px-6 py-5">
849               {/* Stem */}
850               <div className="text-base text-gray-900 leading-relaxed">
851                 <MathText text={currentQuestion.stem_tex} />
852               </div>
853   
854               {/* Code snippet */}
855               {currentQuestion.code_snippet && (
856                 <CodeBlock
857                   code={currentQuestion.code_snippet}
858                   language={currentQuestion.code_language}
859                 />
860               )}
861   
862               {/* Answer section */}
863               <div className="mt-6">
864                 {currentQuestion.question_type === "MCQ" && currentQuestion.choices && (
865                   <MCQOptions
866                     choices={currentQuestion.choices}
867                     selected={mcqSelected}
868                     onChange={handleAnswerMCQ}
869                   />
870                 )}
871   
872                 {currentQuestion.question_type === "MSQ" && currentQuestion.choices && (
873                   <MSQOptions
874                     choices={currentQuestion.choices}
875                     selected={msqSelected}
876                     onChange={handleAnswerMSQ}
877                   />
878                 )}
879   
880                 {currentQuestion.question_type === "NAT" && (
881                   <NATInput value={natValue} onChange={handleAnswerNAT} />
882                 )}
883               </div>
884             </div>
885   
886             {/* ── Navigation bar ── */}
887             <div className="flex-shrink-0 bg-white border-t border-gray-200 px-6 py-3 flex items-center gap-3">
888               {/* Previous */}
889               <button
890                 onClick={handlePrevious}
891                 disabled={currentQno === 1}
892                 className="px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700
893                            hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
894               >
895                 ← Previous
896               </button>
897   
898               <div className="flex-1" />
899   
900               {/* Clear Response */}
901               <button
902                 onClick={handleClearResponse}
903                 disabled={!responses[currentQuestion.id]}
904                 className="px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700
905                            hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
906               >
907                 Clear Response
908               </button>
909   
910               {/* Mark for Review & Next */}
911               <button
912                 onClick={handleMarkForReview}
913                 className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
914                   isCurrentMarked
915                     ? "border-purple-400 bg-purple-50 text-purple-700 hover:bg-purple-100"
916                     : "border-purple-300 text-purple-700 hover:bg-purple-50"
917                 }`}
918               >
919                 {isCurrentMarked ? "✓ Marked" : "Mark for Review"} & Next
920               </button>
921   
922               {/* Save & Next */}
923               <button
924                 onClick={handleSaveAndNext}
925                 className="px-5 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold
926                            hover:bg-blue-700 transition-colors"
927               >
928                 {currentQno === questions.length ? "Save" : "Save & Next →"}
929               </button>
930             </div>
931           </div>
932   
933           {/* ── Right: Question Palette ── */}
934           <QuestionPalette
935             questions={questions}
936             questionStatuses={questionStatuses}
937             currentQno={currentQno}
938             activeSection={activeSection}
939             onNavigate={handleNavigateTo}
940             onSectionChange={setActiveSection}
941             onSubmit={handleSubmit}
942             responses={responses}
943           />
944         </div>
945   
946         {/* ── Submit confirmation modal ── */}
947         {showSubmitModal && (
948           <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
949             <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
950               <h2 className="text-xl font-bold text-gray-900 mb-2">Submit Exam?</h2>
951               <p className="text-sm text-gray-500 mb-6">
952                 Please review your attempt summary before submitting.
953               </p>
954   
955               <div className="grid grid-cols-2 gap-3 mb-6">
956                 <div className="bg-green-50 rounded-lg p-3 text-center">
957                   <p className="text-2xl font-bold text-green-700">{summaryForModal.answered}</p>
958                   <p className="text-xs text-green-600 mt-0.5">Answered</p>
959                 </div>
960                 <div className="bg-red-50 rounded-lg p-3 text-center">
961                   <p className="text-2xl font-bold text-red-700">{summaryForModal.notAnswered}</p>
962                   <p className="text-xs text-red-600 mt-0.5">Not Answered</p>
963                 </div>
964                 <div className="bg-purple-50 rounded-lg p-3 text-center">
965                   <p className="text-2xl font-bold text-purple-700">{summaryForModal.marked}</p>
966                   <p className="text-xs text-purple-600 mt-0.5">Marked for Review</p>
967                 </div>
968                 <div className="bg-gray-50 rounded-lg p-3 text-center">
969                   <p className="text-2xl font-bold text-gray-700">{summaryForModal.notVisited}</p>
970                   <p className="text-xs text-gray-500 mt-0.5">Not Visited</p>
971                 </div>
972               </div>
973   
974               <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 px-3 py-2 rounded-lg mb-6">
975                 ⚠️ Once submitted, you cannot change your answers. Marked-for-review
976                 questions will also be evaluated.
977               </p>
978   
979               <div className="flex gap-3">
980                 <button
981                   onClick={() => setShowSubmitModal(false)}
982                   className="flex-1 py-2.5 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
983                 >
984                   Cancel — Keep Attempting
985                 </button>
986                 <button
987                   onClick={() => {
988                     setShowSubmitModal(false);
989                     // Part 10 will implement actual submission
990                     toast.success("Submission coming in Part 10!", { icon: "🔜" });
991                   }}
992                   className="flex-1 py-2.5 rounded-lg bg-red-600 text-white text-sm font-semibold hover:bg-red-700 transition-colors"
993                 >
994                   Yes, Submit Now
995                 </button>
996               </div>
997             </div>
998           </div>
999         )}
1000      </div>
1001    );
1002  }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\.env
*Saved at: 3/23/2026, 4:48:03 PM*

**[ADDED]**
```
11    
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\llm_service.py
*Saved at: 3/23/2026, 4:46:23 PM*

**[REMOVED]**
```
(from line ~91)
    Fix LaTeX backslashes that are not properly escaped for JSON.

```
**[ADDED]**
```
91        Character-by-character fix for unescaped LaTeX backslashes inside JSON strings.
```
**[REMOVED]**
```
(from line ~93)
    LLMs often output LaTeX like \\pi, \\frac, \\sigma, \\lambda with a single
    backslash inside JSON strings, which is invalid JSON and causes parse errors.

```
**[ADDED]**
```
93        LLMs frequently output LaTeX commands with single backslashes inside JSON,
94        e.g.:  \\pi  \\frac  \\sigma  \\mathbb  \\nabla  \\texttt  \\{  \\}
95        These are INVALID JSON escape sequences and cause json.loads to crash.
```
**[REMOVED]**
```
(from line ~97)
    Two-pass approach:
      Pass 1 – Fix clearly invalid JSON escape sequences:
               \\p, \\m, \\l, \\s, \\J, \\{, \\(, \\^ etc. → \\\\p, \\\\m …
      Pass 2 – Fix ambiguous escapes (\\b, \\f, \\n, \\r, \\t) when followed by
               letters, meaning they are LaTeX commands (\\begin, \\frac,
               \\nabla, \\right, \\times) not JSON control characters.

```
**[ADDED]**
```
97        JSON only allows these escape sequences:
98            \\"  \\\\  \\/  \\b  \\f  \\n  \\r  \\t  \\uXXXX
99    
100       Anything else (\\p, \\m, \\s, \\{, \\J, \\l, etc.) is invalid.
101       Also \\f, \\n, \\b, \\r, \\t followed by a letter means a LaTeX command
102       (\\frac, \\nabla, \\begin, \\right, \\times) not a JSON control char.
103   
104       Strategy: walk character-by-character, track whether we are inside a JSON
105       string, and whenever we see a backslash that starts an invalid escape,
106       double it.
```
**[REMOVED]**
```
(from line ~108)
    # Pass 1: replace \X where X is NOT a valid JSON escape character.
    # Valid JSON escape chars after \: " \ / b f n r t u
    text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)

```
**[ADDED]**
```
108       result = []
109       i = 0
110       in_string = False
```
**[REMOVED]**
```
(from line ~112)
    # Pass 2: fix \b \f \n \r \t that start LaTeX command words
    # e.g. \times → \\times, \frac → \\frac, \begin → \\begin, \nabla → \\nabla
    # Negative lookbehind (?<!\\) prevents double-fixing already-escaped \\times
    text = re.sub(r'(?<!\\)\\([bfnrt])(?=[a-zA-Z])', r'\\\\\1', text)

```
**[ADDED]**
```
112       while i < len(text):
113           c = text[i]
```
**[REMOVED]**
```
(from line ~115)
    return text

```
**[ADDED]**
```
115           # ── Outside a JSON string ─────────────────────────────────────────────
116           if not in_string:
117               result.append(c)
118               if c == '"':
119                   in_string = True
120               i += 1
121               continue
```
**[ADDED]**
```
123           # ── Inside a JSON string ──────────────────────────────────────────────
124           if c == '"':
125               # Unescaped quote ends the string
126               in_string = False
127               result.append(c)
128               i += 1
129               continue
```
**[ADDED]**
```
131           if c != '\\':
132               result.append(c)
133               i += 1
134               continue
135   
136           # ── We have a backslash inside a JSON string ──────────────────────────
137           if i + 1 >= len(text):
138               # Backslash at very end of input — keep as-is
139               result.append(c)
140               i += 1
141               continue
142   
143           nxt = text[i + 1]
144   
145           # Always-valid JSON escape sequences: \", \\, \/
146           if nxt in '"\\/':
147               result.append(c)
148               result.append(nxt)
149               i += 2
150               continue
151   
152           # Unicode escape \uXXXX — valid only if followed by exactly 4 hex digits
153           if nxt == 'u':
154               hex_chars = text[i + 2: i + 6]
155               if len(hex_chars) == 4 and all(
156                   h in '0123456789abcdefABCDEF' for h in hex_chars
157               ):
158                   # Valid \uXXXX — keep all 6 chars
159                   result.append(c)
160                   result.append(nxt)
161                   i += 2
162                   continue
163               else:
164                   # \u NOT followed by 4 hex digits → LaTeX (\underbrace, \uparrow…)
165                   result.append('\\')
166                   result.append('\\')
167                   i += 1
168                   continue
169   
170           # Ambiguous: \b \f \n \r \t
171           # These are valid JSON control chars BUT also start many LaTeX commands:
172           #   \frac \nabla \begin \right \times \boldsymbol \newline ...
173           # Heuristic: if the char AFTER nxt is a letter → it is a LaTeX command.
174           #   \frac{  → nxt='f', after='r' (letter) → double backslash
175           #   \nabla  → nxt='n', after='a' (letter) → double backslash
176           #   "text\n"→ nxt='n', after='"' (not letter) → keep as JSON \n
177           if nxt in 'bfnrt':
178               after_nxt = text[i + 2] if i + 2 < len(text) else ''
179               if after_nxt.isalpha():
180                   # LaTeX command → double the backslash, don't consume nxt
181                   result.append('\\')
182                   result.append('\\')
183                   i += 1
184               else:
185                   # Legitimate JSON control character
186                   result.append(c)
187                   result.append(nxt)
188                   i += 2
189               continue
190   
191           # Everything else: \p \m \s \l \a \c \d \{ \} \( \) \^ \_ \| \> \J …
192           # All invalid in JSON → double the backslash, leave next char in stream
193           result.append('\\')
194           result.append('\\')
195           i += 1
196   
197       return ''.join(result)
198   
199   
```
**[REMOVED]**
```
(from line ~203)
    Handles markdown code fences, extra surrounding text,
    and unescaped LaTeX backslashes.

```
**[ADDED]**
```
203   
204       Steps:
205         1. Strip markdown code fences if present.
206         2. Find the outermost [ ... ] array.
207         3. Fix any unescaped LaTeX backslashes (character-by-character).
208         4. Parse JSON and return.
```
**[REMOVED]**
```
(from line ~212)
    # 1. Try markdown code fence: ```json ... ``` or ``` ... ```
    fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    match = re.search(fence_pattern, cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()

```
**[ADDED]**
```
212       # Step 1 — strip ```json ... ``` or ``` ... ``` fences
213       fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", cleaned, re.DOTALL)
214       if fence_match:
215           cleaned = fence_match.group(1).strip()
```
**[REMOVED]**
```
(from line ~217)
    # 2. Find the outermost [ ... ]

```
**[ADDED]**
```
217       # Step 2 — find outermost [ ... ]
```
**[REMOVED]**
```
(from line ~221)
        cleaned = cleaned[start : end + 1]

```
**[ADDED]**
```
221           cleaned = cleaned[start: end + 1]
```
**[REMOVED]**
```
(from line ~223)
    # 3. Fix LaTeX backslash escaping before JSON parse
    cleaned = _fix_json_latex_escapes(cleaned)

```
**[ADDED]**
```
223       # Step 3 — fix LaTeX backslash escaping before parsing
224       fixed = _fix_json_latex_escapes(cleaned)
```
**[REMOVED]**
```
(from line ~226)
    # 4. Parse JSON

```
**[ADDED]**
```
226       # Step 4 — parse JSON
```
**[REMOVED]**
```
(from line ~228)
        parsed = json.loads(cleaned)

```
**[ADDED]**
```
228           parsed = json.loads(fixed)
```
**[REMOVED]**
```
(from line ~230)
        logger.error(f"JSON parse error: {exc}\nRaw text:\n{text[:500]}")

```
**[ADDED]**
```
230           # Log BOTH original and fixed text so we can diagnose remaining issues
231           logger.error(
232               f"JSON parse error after escape-fix: {exc}\n"
233               f"--- Original LLM text (first 600 chars) ---\n{text[:600]}\n"
234               f"--- Fixed text (first 600 chars) ---\n{fixed[:600]}"
235           )
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\core\config.py
*Saved at: 3/23/2026, 4:43:47 PM*

**[REMOVED]**
```
(from line ~29)
    NEBIUS_MODEL: str = os.getenv("NEBIUS_MODEL", "google/gemma-3-27b-it")

```
**[ADDED]**
```
29        NEBIUS_MODEL: str = os.getenv("NEBIUS_MODEL", "deepseek-ai/DeepSeek-V3.2")
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\question_generator.py
*Saved at: 3/23/2026, 4:28:57 PM*

**[REMOVED]**
```
(from line ~450)
    """Mark an exam generation as failed via generation_progress."""

```
**[ADDED]**
```
450       """Mark an exam generation as failed."""
```
**[ADDED]**
```
453           exam.status = "failed"
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\prompts\generate_ga.json
*Saved at: 3/23/2026, 4:28:10 PM*

**[REMOVED]**
```
(from line ~3)
  "system_prompt": "You are an expert GATE General Aptitude question author for GATE 2026.\n\nSTRICT OUTPUT FORMAT:\nReturn ONLY a valid JSON array. No text before or after. No markdown. No explanation.\n\nEach element must be a JSON object with EXACTLY these keys:\n- \"stem_tex\" (string): Question text. Use LaTeX for math where needed.\n- \"code_snippet\": null (GA questions never have code)\n- \"code_language\": null\n- \"choices\" (array): Exactly 4 option strings.\n- \"answer\" (object): {\"index\": N} where N is the 0-based index of the correct choice.\n- \"question_type\": \"MCQ\"\n- \"marks\" (integer): 1 or 2 as specified.\n- \"difficulty\" (string): \"easy\", \"medium\", or \"hard\".\n- \"difficulty_score\" (float): 0.0 to 1.0.\n- \"section_name\": \"General Aptitude\"\n- \"topic\" (string): The specific GA topic (e.g., \"Verbal Aptitude\", \"Data interpretation\").\n- \"estimated_time_seconds\" (integer): 60-120 for 1-mark, 120-180 for 2-mark.\n- \"solution_tex\" (string): Step-by-step solution.\n\nRULES:\n1. GA questions are ALWAYS MCQ with exactly 4 options.\n2. Cover a mix of Verbal, Quantitative, Analytical, and Spatial aptitude.\n3. Verbal questions: grammar, vocabulary, reading comprehension, sentence completion.\n4. Quantitative questions: data interpretation, arithmetic, percentages, ratios.\n5. Analytical questions: logic, deduction, series, puzzles, coding-decoding.\n6. Spatial questions: pattern recognition, figure completion, transformations.\n7. 1-mark questions should be solvable in ~1 minute.\n8. 2-mark questions should require ~2-3 minutes and multi-step reasoning.\n9. Generate ORIGINAL questions. Do NOT copy from any source.\n10. Do NOT include any text outside the JSON array.",

```
**[ADDED]**
```
3       "system_prompt": "You are an expert GATE General Aptitude question author for GATE 2026.\n\nSTRICT OUTPUT FORMAT:\nReturn ONLY a valid JSON array. No text before or after. No markdown. No explanation.\n\nCRITICAL JSON RULE — BACKSLASH ESCAPING:\nEvery LaTeX backslash MUST be doubled in JSON strings.\nWrite \\\\frac (not \\frac), \\\\sqrt (not \\sqrt), \\\\times (not \\times).\nExample of CORRECT JSON: {\"stem_tex\": \"$\\\\frac{1}{2}$\"}\nExample of WRONG JSON:   {\"stem_tex\": \"$\\frac{1}{2}$\"}\n\nEach element must be a JSON object with EXACTLY these keys:\n- \"stem_tex\" (string): Question text. Use LaTeX for math where needed. Double all backslashes.\n- \"code_snippet\": null (GA questions never have code)\n- \"code_language\": null\n- \"choices\" (array): Exactly 4 option strings.\n- \"answer\" (object): {\"index\": N} where N is the 0-based index of the correct choice.\n- \"question_type\": \"MCQ\"\n- \"marks\" (integer): 1 or 2 as specified.\n- \"difficulty\" (string): \"easy\", \"medium\", or \"hard\".\n- \"difficulty_score\" (float): 0.0 to 1.0.\n- \"section_name\": \"General Aptitude\"\n- \"topic\" (string): The specific GA topic (e.g., \"Verbal Aptitude\", \"Data interpretation\").\n- \"estimated_time_seconds\" (integer): 60-120 for 1-mark, 120-180 for 2-mark.\n- \"solution_tex\" (string): Step-by-step solution. Double all backslashes in any LaTeX.\n\nRULES:\n1. GA questions are ALWAYS MCQ with exactly 4 options.\n2. Cover a mix of Verbal, Quantitative, Analytical, and Spatial aptitude.\n3. Verbal questions: grammar, vocabulary, reading comprehension, sentence completion.\n4. Quantitative questions: data interpretation, arithmetic, percentages, ratios.\n5. Analytical questions: logic, deduction, series, puzzles, coding-decoding.\n6. Spatial questions: pattern recognition, figure completion, transformations.\n7. 1-mark questions should be solvable in ~1 minute.\n8. 2-mark questions should require ~2-3 minutes and multi-step reasoning.\n9. Generate ORIGINAL questions. Do NOT copy from any source.\n10. Do NOT include any text outside the JSON array.",
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\prompts\generate_batch.json
*Saved at: 3/23/2026, 4:28:02 PM*

**[REMOVED]**
```
(from line ~3)
  "system_prompt": "You are an expert GATE exam question author for the GATE 2026 examination conducted by IIT Guwahati.\n\nSTRICT OUTPUT FORMAT:\nReturn ONLY a valid JSON array. No text before or after. No markdown code fences. No explanation.\n\nEach element in the array must be a JSON object with EXACTLY these keys:\n\n- \"stem_tex\" (string): Question text. Use LaTeX for math: $...$ for inline, $$...$$ for display math.\n- \"code_snippet\" (string or null): Code block if the question involves code, otherwise null.\n- \"code_language\" (string or null): \"c\" or \"python\" if code_snippet is present, otherwise null.\n- \"choices\" (array or null): Exactly 4 option strings for MCQ/MSQ. null for NAT.\n- \"answer\" (object): Format depends on type:\n    MCQ: {\"index\": N} where N is 0-based index of the single correct choice.\n    MSQ: {\"indices\": [N1, N2]} array of ALL correct 0-based indices (1 to 3 correct).\n    NAT: {\"value\": <number>, \"tolerance\": <number>} the numeric answer and acceptable tolerance.\n- \"question_type\" (string): \"MCQ\", \"MSQ\", or \"NAT\" — must match what was requested.\n- \"marks\" (integer): 1 or 2 — must match what was requested.\n- \"difficulty\" (string): \"easy\", \"medium\", or \"hard\".\n- \"difficulty_score\" (float): 0.0 (easiest) to 1.0 (hardest).\n- \"section_name\" (string): The section this question belongs to.\n- \"topic\" (string): The specific syllabus topic this question tests.\n- \"estimated_time_seconds\" (integer): Expected time to solve (60-180 for 1-mark, 120-300 for 2-mark).\n- \"solution_tex\" (string): Complete step-by-step solution. Use LaTeX for all math.\n\nRULES:\n1. Generate ORIGINAL questions — never copy from any source.\n2. Each question must test a DIFFERENT topic or sub-concept.\n3. All answers must be mathematically and logically CORRECT.\n4. Solutions must be detailed, step-by-step, and verifiable.\n5. For MSQ, there must be 1 to 3 correct options (never 0 or 4).\n6. For NAT, tolerance should be small (0.001 to 0.1 depending on the answer magnitude).\n7. Questions should be at authentic GATE difficulty — not textbook-easy.\n8. Do NOT include any text outside the JSON array.",

```
**[ADDED]**
```
3       "system_prompt": "You are an expert GATE exam question author for the GATE 2026 examination conducted by IIT Guwahati.\n\nSTRICT OUTPUT FORMAT:\nReturn ONLY a valid JSON array. No text before or after. No markdown code fences. No explanation.\n\nCRITICAL JSON RULE — BACKSLASH ESCAPING:\nEvery LaTeX backslash MUST be doubled in JSON strings.\nWrite \\\\pi (not \\pi), \\\\frac (not \\frac), \\\\sigma (not \\sigma), \\\\mathbb (not \\mathbb), \\\\begin (not \\begin), \\\\end (not \\end), \\\\times (not \\times), \\\\lambda (not \\lambda), \\\\sum (not \\sum), \\\\int (not \\int).\nExample of CORRECT JSON: {\"stem_tex\": \"Find $\\\\frac{d}{dx}(x^2)$\"}\nExample of WRONG JSON:   {\"stem_tex\": \"Find $\\frac{d}{dx}(x^2)$\"}\nA single backslash before any letter (except n, t, r, b, f, u, \\\", \\\\, /) is INVALID JSON and will cause a parse error.\n\nEach element in the array must be a JSON object with EXACTLY these keys:\n\n- \"stem_tex\" (string): Question text. Use LaTeX for math: $...$ for inline, $$...$$ for display math. Remember to double all backslashes.\n- \"code_snippet\" (string or null): Code block if the question involves code, otherwise null.\n- \"code_language\" (string or null): \"c\" or \"python\" if code_snippet is present, otherwise null.\n- \"choices\" (array or null): Exactly 4 option strings for MCQ/MSQ. null for NAT.\n- \"answer\" (object): Format depends on type:\n    MCQ: {\"index\": N} where N is 0-based index of the single correct choice.\n    MSQ: {\"indices\": [N1, N2]} array of ALL correct 0-based indices (1 to 3 correct).\n    NAT: {\"value\": <number>, \"tolerance\": <number>} the numeric answer and acceptable tolerance.\n- \"question_type\" (string): \"MCQ\", \"MSQ\", or \"NAT\" — must match what was requested.\n- \"marks\" (integer): 1 or 2 — must match what was requested.\n- \"difficulty\" (string): \"easy\", \"medium\", or \"hard\".\n- \"difficulty_score\" (float): 0.0 (easiest) to 1.0 (hardest).\n- \"section_name\" (string): The section this question belongs to.\n- \"topic\" (string): The specific syllabus topic this question tests.\n- \"estimated_time_seconds\" (integer): Expected time to solve (60-180 for 1-mark, 120-300 for 2-mark).\n- \"solution_tex\" (string): Complete step-by-step solution. Use LaTeX for all math. Remember to double all backslashes.\n\nRULES:\n1. Generate ORIGINAL questions — never copy from any source.\n2. Each question must test a DIFFERENT topic or sub-concept.\n3. All answers must be mathematically and logically CORRECT.\n4. Solutions must be detailed, step-by-step, and verifiable.\n5. For MSQ, there must be 1 to 3 correct options (never 0 or 4).\n6. For NAT, tolerance should be small (0.001 to 0.1 depending on the answer magnitude).\n7. Questions should be at authentic GATE difficulty — not textbook-easy.\n8. Do NOT include any text outside the JSON array.",
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\llm_service.py
*Saved at: 3/23/2026, 4:27:32 PM*

**[ADDED]**
```
89    def _fix_json_latex_escapes(text: str) -> str:
90        """
91        Fix LaTeX backslashes that are not properly escaped for JSON.
92    
93        LLMs often output LaTeX like \\pi, \\frac, \\sigma, \\lambda with a single
94        backslash inside JSON strings, which is invalid JSON and causes parse errors.
95    
96        Two-pass approach:
97          Pass 1 – Fix clearly invalid JSON escape sequences:
98                   \\p, \\m, \\l, \\s, \\J, \\{, \\(, \\^ etc. → \\\\p, \\\\m …
99          Pass 2 – Fix ambiguous escapes (\\b, \\f, \\n, \\r, \\t) when followed by
100                  letters, meaning they are LaTeX commands (\\begin, \\frac,
101                  \\nabla, \\right, \\times) not JSON control characters.
102       """
103       # Pass 1: replace \X where X is NOT a valid JSON escape character.
104       # Valid JSON escape chars after \: " \ / b f n r t u
105       text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)
106   
107       # Pass 2: fix \b \f \n \r \t that start LaTeX command words
108       # e.g. \times → \\times, \frac → \\frac, \begin → \\begin, \nabla → \\nabla
109       # Negative lookbehind (?<!\\) prevents double-fixing already-escaped \\times
110       text = re.sub(r'(?<!\\)\\([bfnrt])(?=[a-zA-Z])', r'\\\\\1', text)
111   
112       return text
113   
114   
```
**[REMOVED]**
```
(from line ~118)
    Handles markdown code fences and extra surrounding text.

```
**[ADDED]**
```
118       Handles markdown code fences, extra surrounding text,
119       and unescaped LaTeX backslashes.
```
**[REMOVED]**
```
(from line ~135)
    # 3. Parse JSON

```
**[ADDED]**
```
135       # 3. Fix LaTeX backslash escaping before JSON parse
136       cleaned = _fix_json_latex_escapes(cleaned)
137   
138       # 4. Parse JSON
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:21:37 PM*

**[ADDED]**
```
8     
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:21:36 PM*

**[REMOVED]**
```
(from line ~6)


```
**[ADDED]**
```
6     Part 7: Exam Generation Progress Page
7     Frontend page that appears after clicking "Generate Exam". Shows progress bar with "Generating questions... 42/65", updates by polling GET /exams/{id}/status every 3 seconds. Shows estimated time remaining. On completion (status = generated), shows success message with "Start Exam" button that navigates to exam screen. Handle error states (generation failed, partial failure).
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:21:28 PM*

**[ADDED]**
```
5     
6     
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:21:19 PM*

**[REMOVED]**
```
(from line ~3)



```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:21:17 PM*

**[REMOVED]**
```
(from line ~1)
Implemented the Part-6 and Part-7, testing is not done but the code has some 

```
**[ADDED]**
```
1     Implemented the Part-6 and Part-7, testing is not done but the code has some issue.
```
**[ADDED]**
```
3     
4     
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:21:13 PM*

**[REMOVED]**
```
(from line ~1)
Implemented the Part-6 and Part-7, testing is not done 

```
**[ADDED]**
```
1     Implemented the Part-6 and Part-7, testing is not done but the code has some 
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:21:04 PM*

**[REMOVED]**
```
(from line ~1)
Implemented the Part-6 and Part-7

```
**[ADDED]**
```
1     Implemented the Part-6 and Part-7, testing is not done 
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:20:55 PM*

**[REMOVED]**
```
(from line ~1)
Implemented the Part-6 and Part

```
**[ADDED]**
```
1     Implemented the Part-6 and Part-7
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:20:52 PM*

**[REMOVED]**
```
(from line ~1)
Implemented the Part-6 and 

```
**[ADDED]**
```
1     Implemented the Part-6 and Part
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:20:49 PM*

**[REMOVED]**
```
(from line ~1)
Implemented the Part

```
**[ADDED]**
```
1     Implemented the Part-6 and 
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:20:45 PM*

**[ADDED]**
```
1     Implemented the Part
```
**[REMOVED]**
```
(from line ~3)


```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:20:32 PM*

**[ADDED]**
```
1     
2     
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\.git\COMMIT_EDITMSG
*Saved at: 3/23/2026, 3:20:23 PM*

**[REMOVED]**
```
(from line ~1)


```
**[ADDED]**
```
1     Part 6: LLM Integration & Question Generation Pipeline
2     Nebius API client wrapper (llm_service.py), LLM async queue (llm_queue.py), prompt templates JSON files, question generator orchestrator (question_generator.py) that: determines question distribution, retrieves syllabus context, retrieves PYQ examples via pgvector if toggle ON, constructs prompts, calls Kimi-K2.5 in batches of 5, parses JSON responses. Question validator (question_validator.py): JSON schema validation, SymPy verification for NAT answers, embedding uniqueness check. Exam assembler (exam_assembler.py): selects 65 questions following GATE distribution (GA 10 + Subject 55, marks split, type ratio). Updates exam status and generation_progress in database. GET /exams/{id}/status polling endpoint.
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\main.py
*Saved at: 3/23/2026, 2:38:11 PM*

**[ADDED]**
```
1     import asyncio
```
**[REMOVED]**
```
(from line ~6)
from sqlalchemy import text, select, func

```
**[ADDED]**
```
6     from sqlalchemy import text, select, func, update
```
**[REMOVED]**
```
(from line ~9)
from app.core.database import engine,  AsyncSessionLocal

```
**[ADDED]**
```
9     from app.core.database import engine, AsyncSessionLocal
```
**[ADDED]**
```
13    from app.models.exam import Exam
```
**[ADDED]**
```
15    from app.services.llm_queue import run_worker, shutdown_queue, GenerationJob
16    from app.services.question_generator import generate_exam_questions
17    from app.services.exam_assembler import assemble_exam
```
**[ADDED]**
```
19    # Module-level worker task handle
20    worker_task: asyncio.Task | None = None
```
**[ADDED]**
```
22    
23    async def process_generation_job(job: GenerationJob) -> None:
24        """
25        Top-level handler that wires together generation + assembly for a single exam.
26        Run by the LLM queue worker.
27        """
28        async with AsyncSessionLocal() as db:
29            try:
30                questions, _ = await generate_exam_questions(
31                    db=db,
32                    exam_id=str(job.exam_id),
33                    paper=job.paper,
34                    scope=job.scope,
35                    selected_topics=job.selected_topics,
36                    difficulty=job.difficulty,
37                    types_ratio=job.types_ratio,
38                )
39                await assemble_exam(
40                    db=db,
41                    exam_id=str(job.exam_id),
42                    all_questions=questions,
43                    types_ratio=job.types_ratio,
44                )
45                print(f"[generation] Exam {job.exam_id} completed successfully")
46            except Exception as exc:
47                print(f"[generation] Exam {job.exam_id} failed: {exc}")
48                await db.execute(
49                    update(Exam)
50                    .where(Exam.id == job.exam_id)
51                    .values(status="failed")
52                )
53                await db.commit()
54    
55    
```
**[ADDED]**
```
59        global worker_task
60    
```
**[ADDED]**
```
95        # 4. Start LLM queue worker
96        worker_task = asyncio.create_task(run_worker(process_generation_job))
97        print("✅  LLM queue worker started")
98    
```
**[ADDED]**
```
102       await shutdown_queue()
103       if worker_task:
104           worker_task.cancel()
105           try:
106               await worker_task
107           except asyncio.CancelledError:
108               pass
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\main.py
*Saved at: 3/23/2026, 2:37:59 PM*

**[REMOVED]**
```
(from line ~1)
import asyncio

```
**[REMOVED]**
```
(from line ~5)
from sqlalchemy import text, select, func, update

```
**[ADDED]**
```
5     from sqlalchemy import text, select, func
```
**[REMOVED]**
```
(from line ~8)
from app.core.database import engine, AsyncSessionLocal

```
**[ADDED]**
```
8     from app.core.database import engine,  AsyncSessionLocal
```
**[REMOVED]**
```
(from line ~12)
from app.models.exam import Exam

```
**[REMOVED]**
```
(from line ~13)
from app.services.llm_queue import run_worker, shutdown_queue, GenerationJob
from app.services.question_generator import generate_exam_questions
from app.services.exam_assembler import assemble_exam

```
**[REMOVED]**
```
(from line ~14)
# Module-level worker task handle
worker_task: asyncio.Task | None = None

```
**[REMOVED]**
```
(from line ~15)

async def process_generation_job(job: GenerationJob) -> None:
    """
    Top-level handler that wires together generation + assembly for a single exam.
    Run by the LLM queue worker.
    """
    async with AsyncSessionLocal() as db:
        try:
            questions, _ = await generate_exam_questions(
                db=db,
                exam_id=str(job.exam_id),
                paper=job.paper,
                scope=job.scope,
                selected_topics=job.selected_topics,
                difficulty=job.difficulty,
                types_ratio=job.types_ratio,
            )
            await assemble_exam(
                db=db,
                exam_id=str(job.exam_id),
                all_questions=questions,
                types_ratio=job.types_ratio,
            )
            print(f"[generation] Exam {job.exam_id} completed successfully")
        except Exception as exc:
            print(f"[generation] Exam {job.exam_id} failed: {exc}")
            await db.execute(
                update(Exam)
                .where(Exam.id == job.exam_id)
                .values(status="failed")
            )
            await db.commit()



```
**[REMOVED]**
```
(from line ~18)
    global worker_task


```
**[REMOVED]**
```
(from line ~52)
    # 4. Start LLM queue worker
    worker_task = asyncio.create_task(run_worker(process_generation_job))
    print("✅  LLM queue worker started")


```
**[REMOVED]**
```
(from line ~55)
    await shutdown_queue()
    if worker_task:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\main.py
*Saved at: 3/23/2026, 2:37:31 PM*

**[REMOVED]**
```
(from line ~18)
backend/app/main.py

```
**[ADDED]**
```
18    
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\main.py
*Saved at: 3/23/2026, 2:37:30 PM*

**[REMOVED]**
```
(from line ~18)


```
**[ADDED]**
```
18    backend/app/main.py
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\llm_queue.py
*Saved at: 3/23/2026, 2:36:19 PM*

**[REMOVED]**
```
(from line ~14)


```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\pages\ExamProgress.tsx
*Saved at: 3/23/2026, 1:52:31 PM*

**[REMOVED]**
```
(from line ~308)
              
```
**[ADDED]**
```
308                 >
309                   <svg
310                     className="h-5 w-5"
311                     fill="none"
312                     stroke="currentColor"
313                     viewBox="0 0 24 24"
314                   >
315                     <path
316                       strokeLinecap="round"
317                       strokeLinejoin="round"
318                       strokeWidth={2}
319                       d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
320                     />
321                     <path
322                       strokeLinecap="round"
323                       strokeLinejoin="round"
324                       strokeWidth={2}
325                       d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
326                     />
327                   </svg>
328                   Start Exam
329                 </button>
330   
331                 <Link
332                   to="/dashboard"
333                   className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-6 py-3.5 text-sm font-medium text-gray-700 hover:bg-gray-50 sm:w-auto"
334                 >
335                   Save for Later
336                 </Link>
337               </div>
338   
339               <p className="mt-4 text-center text-xs text-gray-400">
340                 You can also start this exam later from your Dashboard.
341               </p>
342             </div>
343           )}
344   
345           {/* ── FAILED: Generation error ── */}
346           {phase === "failed" && (
347             <div className="rounded-xl border border-red-200 bg-white p-8 shadow-sm">
348               <div className="text-center">
349                 <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-50">
350                   <svg
351                     className="h-10 w-10 text-red-500"
352                     fill="none"
353                     stroke="currentColor"
354                     viewBox="0 0 24 24"
355                   >
356                     <path
357                       strokeLinecap="round"
358                       strokeLinejoin="round"
359                       strokeWidth={2}
360                       d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
361                     />
362                   </svg>
363                 </div>
364                 <h1 className="mt-6 text-2xl font-bold text-gray-900">
365                   Generation Failed
366                 </h1>
367                 <p className="mt-2 text-gray-500">
368                   Something went wrong while generating your exam.
369                 </p>
370               </div>
371   
372               {/* Error detail */}
373               {progress.error && (
374                 <div className="mt-6 rounded-lg bg-red-50 p-4">
375                   <p className="text-sm font-medium text-red-800">Error details:</p>
376                   <p className="mt-1 text-sm text-red-600">{progress.error}</p>
377                 </div>
378               )}
379   
380               {/* Partial progress */}
381               {progress.completed > 0 && (
382                 <div className="mt-4">
383                   <p className="mb-2 text-sm text-gray-500">
384                     Progress before failure:
385                   </p>
386                   <ProgressBar
387                     value={Math.round(
388                       (progress.completed / progress.total) * 100
389                     )}
390                     color="red"
391                     size="md"
392                     animate={false}
393                   />
394                   <p className="mt-1 text-xs text-gray-400">
395                     {progress.completed}/{progress.total} questions generated
396                   </p>
397                 </div>
398               )}
399   
400               {/* Actions */}
401               <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
402                 <Link
403                   to="/generate-exam"
404                   className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 sm:w-auto"
405                 >
406                   <svg
407                     className="h-4 w-4"
408                     fill="none"
409                     stroke="currentColor"
410                     viewBox="0 0 24 24"
411                   >
412                     <path
413                       strokeLinecap="round"
414                       strokeLinejoin="round"
415                       strokeWidth={2}
416                       d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
417                     />
418                   </svg>
419                   Try Again
420                 </Link>
421                 <Link
422                   to="/dashboard"
423                   className="inline-flex w-full items-center justify-center rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 sm:w-auto"
424                 >
425                   Back to Dashboard
426                 </Link>
427               </div>
428             </div>
429           )}
430   
431           {/* ── NOT FOUND ── */}
432           {phase === "not_found" && (
433             <div className="rounded-xl border border-gray-200 bg-white p-8 text-center shadow-sm">
434               <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
435                 <span className="text-3xl">🔍</span>
436               </div>
437               <h1 className="mt-6 text-2xl font-bold text-gray-900">
438                 Exam Not Found
439               </h1>
440               <p className="mt-2 text-gray-500">
441                 The exam ID <code className="rounded bg-gray-100 px-1.5 py-0.5 text-sm text-gray-600">{examId}</code>{" "}
442                 doesn't exist or doesn't belong to your account.
443               </p>
444               <Link
445                 to="/dashboard"
446                 className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700"
447               >
448                 Back to Dashboard
449               </Link>
450             </div>
451           )}
452   
453           {/* ── Tips (shown during polling) ── */}
454           {phase === "polling" && (
455             <div className="mt-8 rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
456               <h3 className="text-sm font-semibold text-gray-700">
457                 💡 While you wait...
458               </h3>
459               <ul className="mt-3 space-y-2 text-sm text-gray-500">
460                 <li className="flex items-start gap-2">
461                   <span className="mt-0.5 text-blue-500">•</span>
462                   Each question is uniquely generated by AI — no two exams are alike.
463                 </li>
464                 <li className="flex items-start gap-2">
465                   <span className="mt-0.5 text-blue-500">•</span>
466                   Questions go through validation to ensure correctness.
467                 </li>
468                 <li className="flex items-start gap-2">
469                   <span className="mt-0.5 text-blue-500">•</span>
470                   The exam follows the official GATE 2026 pattern: 65 Qs, 100 marks, 3 hours.
471                 </li>
472                 <li className="flex items-start gap-2">
473                   <span className="mt-0.5 text-blue-500">•</span>
474                   MCQs have negative marking (−⅓ or −⅔). MSQ and NAT have no negative marking.
475                 </li>
476               </ul>
477             </div>
478           )}
479         </main>
480       </div>
481     );
482   }
483   
484   /* ── Sub-components ── */
485   
486   function Step({
487     done,
488     active,
489     label,
490   }: {
491     done: boolean;
492     active: boolean;
493     label: string;
494   }) {
495     return (
496       <div className="flex items-center gap-3">
497         {done ? (
498           <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-green-100">
499             <svg
500               className="h-4 w-4 text-green-600"
501               fill="none"
502               stroke="currentColor"
503               viewBox="0 0 24 24"
504             >
505               <path
506                 strokeLinecap="round"
507                 strokeLinejoin="round"
508                 strokeWidth={2}
509                 d="M5 13l4 4L19 7"
510               />
511             </svg>
512           </div>
513         ) : active ? (
514           <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-blue-100">
515             <div className="h-3 w-3 animate-spin rounded-full border-2 border-blue-300 border-t-blue-600" />
516           </div>
517         ) : (
518           <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-gray-100">
519             <div className="h-2 w-2 rounded-full bg-gray-300" />
520           </div>
521         )}
522         <span
523           className={`text-sm ${
524             done
525               ? "text-green-700"
526               : active
527                 ? "font-medium text-blue-700"
528                 : "text-gray-400"
529           }`}
530         >
531           {label}
532         </span>
533       </div>
534     );
535   }
536   
537   function SummaryCard({ label, value }: { label: string; value: string }) {
538     return (
539       <div className="rounded-lg bg-green-50 p-3 text-center">
540         <p className="text-xs text-green-600">{label}</p>
541         <p className="mt-1 text-sm font-bold text-green-800">{value}</p>
542       </div>
543     );
544   }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\pages\ExamProgress.tsx
*Saved at: 3/23/2026, 1:52:04 PM*

**[REMOVED]**
```
(from line ~1)
import { useParams, Link } from "react-router-dom";

```
**[ADDED]**
```
1     import { useEffect, useState, useRef, useCallback } from "react";
2     import { useParams, useNavigate, Link } from "react-router-dom";
3     import toast from "react-hot-toast";
4     
5     import api from "../services/api";
```
**[ADDED]**
```
7     import ProgressBar from "../components/common/ProgressBar";
```
**[ADDED]**
```
9     /* ── Types ── */
10    interface ProgressData {
11      total: number;
12      completed: number;
13      failed: number;
14      batch?: string | null;
15      error?: string | null;
16    }
17    
18    interface StatusResponse {
19      exam_id: string;
20      status: string;
21      progress: ProgressData;
22    }
23    
24    type Phase =
25      | "polling"      // Generation in progress
26      | "completed"    // Successfully generated
27      | "failed"       // Generation failed
28      | "not_found";   // Exam ID invalid
29    
30    /* ── Constants ── */
31    const POLL_INTERVAL_MS = 3000;
32    const ESTIMATED_SECONDS_PER_QUESTION = 5; // rough estimate
33    
```
**[ADDED]**
```
36      const navigate = useNavigate();
```
**[ADDED]**
```
38      const [phase, setPhase] = useState<Phase>("polling");
39      const [progress, setProgress] = useState<ProgressData>({
40        total: 65,
41        completed: 0,
42        failed: 0,
43      });
44      const [startTime] = useState(() => Date.now());
45      const [elapsedSeconds, setElapsedSeconds] = useState(0);
46      const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
47      const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
48    
49      /* ── Poll for status ── */
50      const pollStatus = useCallback(async () => {
51        if (!examId) return;
52    
53        try {
54          const { data } = await api.get<StatusResponse>(
55            `/exams/${examId}/status`
56          );
57    
58          setProgress(data.progress);
59    
60          if (data.status === "generated") {
61            setPhase("completed");
62            // Stop polling
63            if (intervalRef.current) {
64              clearInterval(intervalRef.current);
65              intervalRef.current = null;
66            }
67          } else if (data.progress.error) {
68            setPhase("failed");
69            if (intervalRef.current) {
70              clearInterval(intervalRef.current);
71              intervalRef.current = null;
72            }
73          }
74        } catch (err: any) {
75          if (err?.response?.status === 404) {
76            setPhase("not_found");
77            if (intervalRef.current) {
78              clearInterval(intervalRef.current);
79              intervalRef.current = null;
80            }
81          }
82          // Other errors: keep polling (transient network issues)
83        }
84      }, [examId]);
85    
86      /* ── Start polling on mount ── */
87      useEffect(() => {
88        // Initial poll immediately
89        pollStatus();
90    
91        // Then poll every 3 seconds
92        intervalRef.current = setInterval(pollStatus, POLL_INTERVAL_MS);
93    
94        // Elapsed time ticker
95        timerRef.current = setInterval(() => {
96          setElapsedSeconds(Math.floor((Date.now() - startTime) / 1000));
97        }, 1000);
98    
99        return () => {
100         if (intervalRef.current) clearInterval(intervalRef.current);
101         if (timerRef.current) clearInterval(timerRef.current);
102       };
103     }, [pollStatus, startTime]);
104   
105     /* ── Stop timer when generation completes ── */
106     useEffect(() => {
107       if (phase === "completed" || phase === "failed" || phase === "not_found") {
108         if (timerRef.current) {
109           clearInterval(timerRef.current);
110           timerRef.current = null;
111         }
112       }
113     }, [phase]);
114   
115     /* ── Derived values ── */
116     const pct =
117       progress.total > 0
118         ? Math.round((progress.completed / progress.total) * 100)
119         : 0;
120   
121     const remaining =
122       progress.completed > 0
123         ? Math.max(
124             0,
125             Math.round(
126               ((progress.total - progress.completed) /
127                 progress.completed) *
128                 elapsedSeconds
129             )
130           )
131         : progress.total * ESTIMATED_SECONDS_PER_QUESTION;
132   
133     const formatTime = (secs: number): string => {
134       const m = Math.floor(secs / 60);
135       const s = secs % 60;
136       if (m > 0) return `${m}m ${s}s`;
137       return `${s}s`;
138     };
139   
140     const handleStartExam = () => {
141       toast.success("Navigating to exam...");
142       navigate(`/exam/${examId}`);
143     };
144   
145     /* ── Render ── */
```
**[REMOVED]**
```
(from line ~150)
      <main className="mx-auto max-w-2xl px-4 py-16 text-center sm:px-6 lg:px-8">
        <div className="rounded-xl border border-gray-200 bg-white p-12 shadow-sm">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-blue-50">
            <span className="text-3xl">⏳</span>
          </div>

```
**[ADDED]**
```
150         <main className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
151           {/* ── POLLING: Generation in progress ── */}
152           {phase === "polling" && (
153             <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
154               {/* Header */}
155               <div className="text-center">
156                 <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-blue-50">
157                   <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
158                 </div>
159                 <h1 className="mt-6 text-2xl font-bold text-gray-900">
160                   Generating Your Exam
161                 </h1>
162                 <p className="mt-2 text-sm text-gray-500">
163                   AI is crafting original GATE-style questions. This usually takes
164                   3–7 minutes.
165                 </p>
166               </div>
```
**[REMOVED]**
```
(from line ~168)
          <h1 className="mt-6 text-2xl font-bold text-gray-900">
            Exam Generation In Progress
          </h1>
          <p className="mx-auto mt-3 max-w-md text-gray-500">
            AI is generating your exam questions. This page will show a live
            progress bar in the next module.
          </p>

```
**[ADDED]**
```
168               {/* Progress bar */}
169               <div className="mt-8">
170                 <div className="mb-2 flex items-center justify-between text-sm">
171                   <span className="font-medium text-gray-700">
172                     Generating questions...
173                   </span>
174                   <span className="font-semibold text-blue-600">
175                     {progress.completed}/{progress.total}
176                   </span>
177                 </div>
178                 <ProgressBar value={pct} color="blue" size="lg" animate />
179                 <div className="mt-2 text-right text-xs text-gray-400">
180                   {pct}% complete
181                 </div>
182               </div>
```
**[REMOVED]**
```
(from line ~184)
          <div className="mt-4 rounded-lg bg-gray-50 p-3">
            <p className="text-xs text-gray-400">
              Exam ID: <code className="text-gray-600">{examId}</code>
            </p>
          </div>

```
**[ADDED]**
```
184               {/* Stats row */}
185               <div className="mt-6 grid grid-cols-3 gap-4">
186                 <div className="rounded-lg bg-gray-50 p-3 text-center">
187                   <p className="text-xs text-gray-500">Elapsed</p>
188                   <p className="mt-1 text-sm font-semibold text-gray-900">
189                     {formatTime(elapsedSeconds)}
190                   </p>
191                 </div>
192                 <div className="rounded-lg bg-gray-50 p-3 text-center">
193                   <p className="text-xs text-gray-500">Est. Remaining</p>
194                   <p className="mt-1 text-sm font-semibold text-gray-900">
195                     {progress.completed > 0
196                       ? `~${formatTime(remaining)}`
197                       : "Calculating..."}
198                   </p>
199                 </div>
200                 <div className="rounded-lg bg-gray-50 p-3 text-center">
201                   <p className="text-xs text-gray-500">Batch</p>
202                   <p className="mt-1 text-sm font-semibold text-gray-900">
203                     {progress.batch || "—"}
204                   </p>
205                 </div>
206               </div>
```
**[REMOVED]**
```
(from line ~208)
          <div className="mt-8 flex justify-center gap-3">
            <Link
              to="/dashboard"
              className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              ← Back to Dashboard
            </Link>

```
**[ADDED]**
```
208               {/* Failed questions warning */}
209               {progress.failed > 0 && (
210                 <div className="mt-4 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">
211                   <span className="font-medium">Note:</span>{" "}
212                   {progress.failed} question(s) failed validation and will be
213                   retried or skipped. This is normal.
214                 </div>
215               )}
216   
217               {/* Live steps */}
218               <div className="mt-6 space-y-2">
219                 <Step
220                   done={progress.completed > 0}
221                   active={progress.completed === 0}
222                   label="Initializing question generation pipeline"
223                 />
224                 <Step
225                   done={progress.completed >= 10}
226                   active={progress.completed > 0 && progress.completed < 10}
227                   label="Generating General Aptitude questions (10)"
228                 />
229                 <Step
230                   done={progress.completed >= progress.total}
231                   active={progress.completed >= 10 && progress.completed < progress.total}
232                   label={`Generating Subject questions (${Math.max(0, progress.completed - 10)}/55)`}
233                 />
234                 <Step
235                   done={false}
236                   active={false}
237                   label="Assembling final exam paper"
238                 />
239               </div>
240   
241               {/* Exam ID */}
242               <div className="mt-6 rounded-lg bg-gray-50 p-3 text-center">
243                 <p className="text-xs text-gray-400">
244                   Exam ID:{" "}
245                   <code className="rounded bg-gray-200 px-1.5 py-0.5 text-gray-600">
246                     {examId}
247                   </code>
248                 </p>
249               </div>
```
**[REMOVED]**
```
(from line ~251)
        </div>
      </main>
    </div>
  );
}
```
**[ADDED]**
```
251           )}
252   
253           {/* ── COMPLETED: Generation successful ── */}
254           {phase === "completed" && (
255             <div className="rounded-xl border border-green-200 bg-white p-8 shadow-sm">
256               <div className="text-center">
257                 <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-50">
258                   <svg
259                     className="h-10 w-10 text-green-500"
260                     fill="none"
261                     stroke="currentColor"
262                     viewBox="0 0 24 24"
263                   >
264                     <path
265                       strokeLinecap="round"
266                       strokeLinejoin="round"
267                       strokeWidth={2}
268                       d="M5 13l4 4L19 7"
269                     />
270                   </svg>
271                 </div>
272                 <h1 className="mt-6 text-2xl font-bold text-gray-900">
273                   Exam Ready! 🎉
274                 </h1>
275                 <p className="mt-2 text-gray-500">
276                   Your GATE mock test has been generated successfully.
277                 </p>
278               </div>
279   
280               {/* Summary */}
281               <div className="mt-6">
282                 <ProgressBar value={100} color="green" size="lg" animate={false} />
283               </div>
284   
285               <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
286                 <SummaryCard label="Questions" value={String(progress.completed)} />
287                 <SummaryCard label="Total Marks" value="100" />
288                 <SummaryCard label="Duration" value="3 hours" />
289                 <SummaryCard
290                   label="Generated In"
291                   value={formatTime(elapsedSeconds)}
292                 />
293               </div>
294   
295               {progress.failed > 0 && (
296                 <div className="mt-4 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">
297                   <span className="font-medium">Note:</span>{" "}
298                   {progress.failed} question(s) failed validation and were
299                   skipped. Your exam may have slightly fewer questions.
300                 </div>
301               )}
302   
303               {/* Actions */}
304               <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
305                 <button
306                   onClick={handleStartExam}
307                   className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-8 py-3.5 text-base font-semibold text-white shadow-sm hover:bg-blue-700 sm:w-auto"
308                 
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\frontend\src\components\common\ProgressBar.tsx
*Saved at: 3/23/2026, 1:51:46 PM*

**[ADDED]**
```
1     interface Props {
2       value: number; // 0–100
3       color?: "blue" | "green" | "red" | "yellow";
4       size?: "sm" | "md" | "lg";
5       animate?: boolean;
6     }
7     
8     const colorMap = {
9       blue: "bg-blue-600",
10      green: "bg-green-500",
11      red: "bg-red-500",
12      yellow: "bg-yellow-500",
13    };
14    
15    const trackMap = {
16      blue: "bg-blue-100",
17      green: "bg-green-100",
18      red: "bg-red-100",
19      yellow: "bg-yellow-100",
20    };
21    
22    const sizeMap = {
23      sm: "h-2",
24      md: "h-3",
25      lg: "h-4",
26    };
27    
28    export default function ProgressBar({
29      value,
30      color = "blue",
31      size = "md",
32      animate = true,
33    }: Props) {
34      const clamped = Math.max(0, Math.min(100, value));
35    
36      return (
37        <div className={`w-full overflow-hidden rounded-full ${trackMap[color]} ${sizeMap[size]}`}>
38          <div
39            className={`${sizeMap[size]} rounded-full ${colorMap[color]} transition-all duration-500 ease-out ${
40              animate && clamped < 100 ? "animate-pulse" : ""
41            }`}
42            style={{ width: `${clamped}%` }}
43          />
44        </div>
45      );
46    }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\api\exams.py
*Saved at: 3/23/2026, 1:44:40 PM*

**[ADDED]**
```
1     import asyncio
```
**[REMOVED]**
```
(from line ~4)
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

```
**[ADDED]**
```
4     from fastapi import APIRouter, Depends, HTTPException, status
```
**[REMOVED]**
```
(from line ~14)
from app.services.llm_queue import enqueue, GenerationJob

```
**[ADDED]**
```
14    from app.services.question_generator import run_generation
```
**[REMOVED]**
```
(from line ~27)
    background_tasks: BackgroundTasks,

```
**[REMOVED]**
```
(from line ~32)
    status 'generating', and enqueues the generation job for
    background processing by the LLM queue worker.

```
**[ADDED]**
```
32        status 'generating', kicks off background generation, and returns exam_id.
```
**[REMOVED]**
```
(from line ~46)
    # ── 2. Validate GA syllabus exists (needed for every exam) ──

```
**[ADDED]**
```
46        # ── 2. Validate GA syllabus exists ──
```
**[REMOVED]**
```
(from line ~65)
        # Fetch all valid topics for this paper from the database

```
**[REMOVED]**
```
(from line ~95)
        use_pyq_reference=False,  # Disabled — no RAG in v1

```
**[ADDED]**
```
95            use_pyq_reference=False,
```
**[REMOVED]**
```
(from line ~104)
        question_ids=[],       # Will be populated by generation worker
        question_order=[],     # Will be populated by generation worker

```
**[ADDED]**
```
104           question_ids=[],
105           question_order=[],
```
**[REMOVED]**
```
(from line ~112)
    await db.refresh(exam)

```
**[REMOVED]**
```
(from line ~113)
    # ── Enqueue generation job ──
    job = GenerationJob(
        exam_id=exam.id,
        paper=body.paper,
        scope=body.scope,
        selected_topics=body.selected_topics if body.scope == "topic" else None,
        difficulty=body.difficulty,
        types_ratio={
            "MCQ": body.types_ratio.MCQ,
            "MSQ": body.types_ratio.MSQ,
            "NAT": body.types_ratio.NAT,
        },
    )
    background_tasks.add_task(enqueue, job)

```
**[ADDED]**
```
113       # ── 6. Kick off background generation ──
114       asyncio.create_task(run_generation(exam_id))
```
**[REMOVED]**
```
(from line ~119)
        message="Exam configuration saved. Generation will begin shortly.",

```
**[ADDED]**
```
119           message="Exam generation started. Poll GET /exams/{id}/status for progress.",
```
**[REMOVED]**
```
(from line ~159)
    summary="Get exam generation status",

```
**[ADDED]**
```
159       summary="Poll exam generation progress",
```
**[REMOVED]**
```
(from line ~166)
    """Poll this endpoint to check generation progress."""

```
**[ADDED]**
```
166       """
167       Returns current generation status and progress.
168       Frontend polls this every 3 seconds during generation.
169       """
```
**[ADDED]**
```
181       progress = exam.generation_progress or {}
182   
```
**[REMOVED]**
```
(from line ~184)
        "exam_id": exam.id,

```
**[ADDED]**
```
184           "exam_id": str(exam.id),
```
**[REMOVED]**
```
(from line ~186)
        "progress": exam.generation_progress,
    }
```
**[ADDED]**
```
186           "progress": {
187               "total": progress.get("total", 65),
188               "completed": progress.get("completed", 0),
189               "failed": progress.get("failed", 0),
190               "batch": progress.get("batch"),
191               "error": progress.get("error"),
192           },
193       }
194   
195   
196   @router.delete(
197       "/{exam_id}",
198       status_code=status.HTTP_204_NO_CONTENT,
199       summary="Delete an exam",
200   )
201   async def delete_exam(
202       exam_id: uuid.UUID,
203       user: User = Depends(get_current_user),
204       db: AsyncSession = Depends(get_db),
205   ):
206       """Delete an exam and its associated data."""
207       result = await db.execute(
208           select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
209       )
210       exam = result.scalar_one_or_none()
211   
212       if exam is None:
213           raise HTTPException(
214               status_code=status.HTTP_404_NOT_FOUND,
215               detail="Exam not found.",
216           )
217   
218       await db.delete(exam)
219       await db.commit()
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\question_generator.py
*Saved at: 3/23/2026, 1:43:13 PM*

**[REMOVED]**
```
(from line ~2)
Question generator orchestrator.

```
**[ADDED]**
```
2     Main orchestrator for exam question generation.
```
**[REMOVED]**
```
(from line ~4)
Drives the full generation pipeline:
  1. Retrieve syllabus context from DB
  2. Generate GA questions (2 batches × 5 = 10)
  3. Generate subject questions (11 batches × 5 = 55)
  4. Validate each question with retry logic
  5. Update progress after every batch

```
**[ADDED]**
```
4     Flow:
5       1. Load exam config from DB
6       2. Load syllabus topics
7       3. Calculate question distribution → list of batch specs
8       4. For each batch: call LLM → parse → validate → collect
9       5. Store valid questions in question_bank
10      6. Assemble 65-question exam
11      7. Update exam row with question_ids, question_order, status
```
**[ADDED]**
```
14    import asyncio
```
**[REMOVED]**
```
(from line ~16)
import random

```
**[ADDED]**
```
16    import logging
17    import math
18    import uuid
```
**[REMOVED]**
```
(from line ~20)
from typing import Any

```
**[ADDED]**
```
24    from app.core.database import AsyncSessionLocal
25    from app.core.config import settings
26    from app.core.llm_config import (
27        GA_1MARK,
28        GA_2MARK,
29        SUBJECT_1MARK,
30        SUBJECT_2MARK,
31        GATE_TOTAL_QUESTIONS,
32    )
33    from app.models.exam import Exam
```
**[REMOVED]**
```
(from line ~35)
from app.services.llm_service import llm_service
from app.services.question_validator import validate_question_with_retry
from app.services.exam_assembler import update_exam_progress

```
**[ADDED]**
```
35    from app.models.question_bank import QuestionBank
36    from app.services.llm_service import call_llm, extract_json_array
37    from app.services.question_validator import validate_batch
38    from app.services.exam_assembler import assemble_exam, compute_marks_summary
```
**[REMOVED]**
```
(from line ~40)
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

```
**[ADDED]**
```
40    logger = logging.getLogger(__name__)
```
**[ADDED]**
```
42    # ── Load prompt templates ──
43    PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
```
**[REMOVED]**
```
(from line ~45)
# ─── Template loader ─────────────────────────────────────────────────────────


def load_template(name: str) -> dict[str, Any]:
    """Load a JSON prompt template from the prompts directory."""
    with open(PROMPTS_DIR / f"{name}.json", encoding="utf-8") as f:

```
**[ADDED]**
```
45    def _load_prompt(filename: str) -> dict:
46        filepath = PROMPTS_DIR / filename
47        with open(filepath, "r", encoding="utf-8") as f:
```
**[ADDED]**
```
50    _BATCH_PROMPT = _load_prompt("generate_batch.json")
51    _GA_PROMPT = _load_prompt("generate_ga.json")
```
**[REMOVED]**
```
(from line ~53)
# ─── Syllabus context builder ───────────────────────────────────────────────

```
**[ADDED]**
```
53    PAPER_NAMES = {
54        "CS": "Computer Science and Information Technology",
55        "DA": "Data Science and Artificial Intelligence",
56    }
```
**[REMOVED]**
```
(from line ~59)
def build_syllabus_context(
    paper: str,
    topics: list[str] | None,
    db: AsyncSession,
) -> str:

```
**[ADDED]**
```
59    # ──────────────────────────────────────────────────────────
60    # Public entry point
61    # ──────────────────────────────────────────────────────────
62    
63    async def run_generation(exam_id: uuid.UUID) -> None:
```
**[REMOVED]**
```
(from line ~65)
    Query the syllabus table for the given paper (and optional topic filter),
    group by section_name, and return a formatted string for the LLM prompt.

```
**[ADDED]**
```
65        Background task: generates all questions for an exam.
66        Uses its own DB session (not the request session).
```
**[REMOVED]**
```
(from line ~68)
    query = select(Syllabus).where(Syllabus.paper == paper)
    if topics:
        query = query.where(Syllabus.topic.in_(topics))
    result = db.execute(query)
    rows = result.scalars().all()

```
**[ADDED]**
```
68        async with AsyncSessionLocal() as db:
69            try:
70                await _do_generation(db, exam_id)
71            except Exception as exc:
72                logger.exception(f"Exam generation failed for {exam_id}: {exc}")
73                await _set_error(db, exam_id, str(exc))
```
**[REMOVED]**
```
(from line ~75)
    sections: dict[str, list[str]] = {}
    for row in rows:
        sections.setdefault(row.section_name, []).append(row.topic)

```
**[REMOVED]**
```
(from line ~76)
    lines: list[str] = []
    for section, topic_list in sections.items():
        lines.append(f"## {section}")
        for t in topic_list:
            lines.append(f"  - {t}")
        lines.append("")

```
**[ADDED]**
```
76    async def _do_generation(db: AsyncSession, exam_id: uuid.UUID) -> None:
77        # ── 1. Load exam config ──
78        exam = await db.get(Exam, exam_id)
79        if exam is None:
80            raise ValueError(f"Exam {exam_id} not found")
```
**[REMOVED]**
```
(from line ~82)
    return "\n".join(lines) if lines else "No specific topics defined."

```
**[ADDED]**
```
82        logger.info(f"Starting generation for exam {exam_id} (paper={exam.paper})")
```
**[ADDED]**
```
84        # ── 2. Load syllabus topics ──
85        subject_sections = await _load_syllabus_grouped(db, exam.paper)
86        ga_sections = await _load_syllabus_grouped(db, "GA")
```
**[REMOVED]**
```
(from line ~88)
# ─── Batch type determination ────────────────────────────────────────────────

```
**[ADDED]**
```
88        if not subject_sections:
89            raise ValueError(f"No syllabus data for paper {exam.paper}")
90        if not ga_sections:
91            raise ValueError("No syllabus data for GA")
```
**[ADDED]**
```
93        # Filter subject sections if scope is 'topic'
94        if exam.scope == "topic" and exam.selected_topics:
95            selected = set(exam.selected_topics)
96            filtered = {}
97            for sec_name, topics in subject_sections.items():
98                matching = [t for t in topics if t in selected]
99                if matching:
100                   filtered[sec_name] = matching
101           if not filtered:
102               raise ValueError("No matching sections for selected topics")
103           subject_sections = filtered
```
**[REMOVED]**
```
(from line ~105)
def determine_batch_types(
    types_ratio: dict[str, float],
    batch_size: int = 5,
) -> list[dict[str, Any]]:
    """
    For a batch of 5 questions, determine types and marks following GATE style.
    Pattern: 2×MCQ-1mark + 2×MCQ-2mark + 1×(MSQ or NAT)-2mark
    The MSQ/NAT choice is weighted randomly by the configured ratios.
    """
    batch = [
        {"question_type": "MCQ", "marks": 1},
        {"question_type": "MCQ", "marks": 1},
        {"question_type": "MCQ", "marks": 2},
        {"question_type": "MCQ", "marks": 2},
    ]

```
**[ADDED]**
```
105       # ── 3. Build batch plan ──
106       types_ratio = exam.types_ratio or {"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
107       difficulty = exam.difficulty
```
**[REMOVED]**
```
(from line ~109)
    msq_ratio = types_ratio.get("MSQ", 0.2)
    nat_ratio = types_ratio.get("NAT", 0.2)
    total = msq_ratio + nat_ratio + 0.0001  # avoid div-by-zero

```
**[ADDED]**
```
109       batches = _build_batch_plan(
110           subject_sections=subject_sections,
111           ga_sections=ga_sections,
112           types_ratio=types_ratio,
113           difficulty=difficulty,
114           paper=exam.paper,
115       )
```
**[REMOVED]**
```
(from line ~117)
    r = random.random()
    if r < msq_ratio / total:
        batch.append({"question_type": "MSQ", "marks": 2})
    else:
        batch.append({"question_type": "NAT", "marks": 2})

```
**[ADDED]**
```
117       total_expected = sum(b["count"] for b in batches)
118       logger.info(f"Batch plan: {len(batches)} batches, {total_expected} questions expected")
```
**[REMOVED]**
```
(from line ~120)
    return batch

```
**[ADDED]**
```
120       # ── 4. Generate questions batch by batch ──
121       all_questions: list[dict] = []
122       completed = 0
123       failed = 0
```
**[ADDED]**
```
125       for batch_idx, batch_spec in enumerate(batches):
126           try:
127               raw = await _generate_one_batch(batch_spec)
128               valid = validate_batch(raw, expected_section=batch_spec["section_name"])
```
**[REMOVED]**
```
(from line ~130)
# ─── GA batch generation ─────────────────────────────────────────────────────

```
**[ADDED]**
```
130               # Tag each question with paper
131               for q in valid:
132                   q["_paper"] = exam.paper if batch_spec["is_ga"] is False else "GA"
```
**[ADDED]**
```
134               all_questions.extend(valid)
135               completed += len(valid)
136               failed += batch_spec["count"] - len(valid)
```
**[REMOVED]**
```
(from line ~138)
async def generate_ga_batch(
    db: AsyncSession,
    difficulty: str,
    batch_index: int,
) -> list[dict[str, Any]]:
    """
    Generate one batch of 5 General Aptitude questions.
    - Batch 0: all 1-mark MCQ
    - Batch 1: 4×MCQ-2mark + 1×(MSQ or NAT)-2mark
    """
    template = load_template("generate_ga")
    syllabus_context = build_syllabus_context("GA", None, db)

```
**[ADDED]**
```
138               logger.info(
139                   f"Batch {batch_idx + 1}/{len(batches)}: "
140                   f"{len(valid)}/{batch_spec['count']} valid"
141               )
```
**[REMOVED]**
```
(from line ~143)
    if batch_index == 0:
        marks_dist = "MCQ-1mark, MCQ-1mark, MCQ-1mark, MCQ-1mark, MCQ-1mark"
        types_str = "MCQ, MCQ, MCQ, MCQ, MCQ"
    else:
        # Batch 1: 2mark questions with MSQ/NAT mix
        marks_dist = "MCQ-2mark, MCQ-2mark, MCQ-2mark, MCQ-2mark, MSQ-2mark"
        types_str = "MCQ, MCQ, MCQ, MCQ, MSQ"

```
**[ADDED]**
```
143           except Exception as exc:
144               logger.error(f"Batch {batch_idx + 1} failed entirely: {exc}")
145               failed += batch_spec["count"]
```
**[REMOVED]**
```
(from line ~147)
    user_content = json.dumps({
        "syllabus_context": syllabus_context,
        "difficulty": difficulty,
        "question_types": types_str,
        "marks_distribution": marks_dist,
    })

```
**[ADDED]**
```
147           # Update progress
148           exam.generation_progress = {
149               "total": GATE_TOTAL_QUESTIONS,
150               "completed": min(completed, GATE_TOTAL_QUESTIONS),
151               "failed": failed,
152               "batch": f"{batch_idx + 1}/{len(batches)}",
153           }
154           await db.commit()
```
**[REMOVED]**
```
(from line ~156)
    messages = [
        {"role": "system", "content": template["system_prompt"]},
        {"role": "user", "content": user_content},
    ]

```
**[ADDED]**
```
156       logger.info(
157           f"Generation done: {len(all_questions)} valid questions "
158           f"({completed} completed, {failed} failed)"
159       )
```
**[REMOVED]**
```
(from line ~161)
    try:
        raw = await llm_service.chat_completion(messages)
        questions: list[dict[str, Any]] = raw if isinstance(raw, list) else []
    except Exception as exc:
        print(f"[question_generator] GA batch {batch_index} LLM call failed: {exc}")
        questions = []

```
**[ADDED]**
```
161       if len(all_questions) < 20:
162           raise ValueError(
163               f"Only generated {len(all_questions)} valid questions — "
164               "not enough to assemble an exam. Check LLM configuration."
165           )
```
**[REMOVED]**
```
(from line ~167)
    # Add paper tag to each question
    validated: list[dict[str, Any]] = []
    for q in questions:
        q["paper"] = "GA"
        result = await validate_question_with_retry(q)
        if result.valid:
            validated.append(q)

```
**[ADDED]**
```
167       # ── 5. Store questions in question_bank ──
168       stored_ids = await _store_questions(db, all_questions, exam)
```
**[REMOVED]**
```
(from line ~170)
    return validated

```
**[ADDED]**
```
170       # ── 6. Assemble exam ──
171       question_order, selected = assemble_exam(all_questions, exam.paper)
```
**[ADDED]**
```
173       # Map question_order IDs to stored UUIDs
174       for i, entry in enumerate(question_order):
175           if i < len(stored_ids):
176               entry["question_id"] = str(stored_ids[i])
```
**[REMOVED]**
```
(from line ~178)
# ─── Subject batch generation ────────────────────────────────────────────────

```
**[ADDED]**
```
178       summary = compute_marks_summary(question_order)
179       logger.info(f"Exam assembled: {summary}")
```
**[ADDED]**
```
181       # ── 7. Update exam row ──
182       exam.question_ids = [str(qid) for qid in stored_ids[: len(selected)]]
183       exam.question_order = question_order
184       exam.status = "generated"
185       exam.generation_progress = {
186           "total": GATE_TOTAL_QUESTIONS,
187           "completed": len(question_order),
188           "failed": 0,
189       }
190       await db.commit()
```
**[REMOVED]**
```
(from line ~192)
async def generate_subject_batch(
    db: AsyncSession,
    paper: str,
    difficulty: str,

```
**[ADDED]**
```
192       logger.info(f"Exam {exam_id} generation complete — status: generated")
193   
194   
195   # ──────────────────────────────────────────────────────────
196   # Internal helpers
197   # ──────────────────────────────────────────────────────────
198   
199   async def _load_syllabus_grouped(
200       db: AsyncSession, paper: str
201   ) -> dict[str, list[str]]:
202       """Load syllabus topics grouped by section_name."""
203       result = await db.execute(
204           select(Syllabus.section_name, Syllabus.topic)
205           .where(Syllabus.paper == paper)
206           .order_by(Syllabus.section_name, Syllabus.id)
207       )
208       rows = result.fetchall()
209   
210       grouped: dict[str, list[str]] = {}
211       for section_name, topic in rows:
212           grouped.setdefault(section_name, []).append(topic)
213       return grouped
214   
215   
216   def _build_batch_plan(
217       subject_sections: dict[str, list[str]],
218       ga_sections: dict[str, list[str]],
```
**[REMOVED]**
```
(from line ~220)
    batch_index: int,
    topics: list[str] | None,
) -> list[dict[str, Any]]:

```
**[ADDED]**
```
220       difficulty: str,
221       paper: str,
222   ) -> list[dict]:
```
**[REMOVED]**
```
(from line ~224)
    Generate one batch of 5 subject questions for CS or DA paper.

```
**[ADDED]**
```
224       Create a list of batch specifications.
225       Each batch = one LLM call producing up to 5 questions.
```
**[REMOVED]**
```
(from line ~227)
    template = load_template("generate_batch")
    syllabus_context = build_syllabus_context(paper, topics, db)
    type_spec = determine_batch_types(types_ratio)

```
**[ADDED]**
```
227       batches: list[dict] = []
```
**[REMOVED]**
```
(from line ~229)
    marks_dist = ", ".join(
        f"{t['question_type']}-{t['marks']}mark" for t in type_spec
    )
    types_str = ", ".join(t["question_type"] for t in type_spec)

```
**[ADDED]**
```
229       # ── GA batches ──
230       all_ga_topics = []
231       for topics in ga_sections.values():
232           all_ga_topics.extend(topics)
```
**[REMOVED]**
```
(from line ~234)
    user_content = json.dumps({

```
**[ADDED]**
```
234       batches.append({
235           "section_name": "General Aptitude",
```
**[REMOVED]**
```
(from line ~237)
        "difficulty": difficulty,
        "syllabus_context": syllabus_context,
        "question_types": types_str,
        "marks_distribution": marks_dist,

```
**[ADDED]**
```
237           "is_ga": True,
238           "topics": all_ga_topics,
239           "marks": 1,
240           "count": GA_1MARK,
241           "types": {"MCQ": GA_1MARK},
242           "difficulty": difficulty if difficulty != "auto" else "easy",
```
**[ADDED]**
```
244       batches.append({
245           "section_name": "General Aptitude",
246           "paper": paper,
247           "is_ga": True,
248           "topics": all_ga_topics,
249           "marks": 2,
250           "count": GA_2MARK,
251           "types": {"MCQ": GA_2MARK},
252           "difficulty": difficulty if difficulty != "auto" else "medium",
253       })
```
**[REMOVED]**
```
(from line ~255)
    messages = [
        {"role": "system", "content": template["system_prompt"]},
        {"role": "user", "content": user_content},
    ]

```
**[ADDED]**
```
255       # ── Subject batches ──
256       num_sections = len(subject_sections)
257       if num_sections == 0:
258           return batches
```
**[REMOVED]**
```
(from line ~260)
    try:
        raw = await llm_service.chat_completion(messages)
        questions: list[dict[str, Any]] = raw if isinstance(raw, list) else []
    except Exception as exc:
        print(f"[question_generator] Subject batch {batch_index} LLM call failed: {exc}")
        questions = []

```
**[ADDED]**
```
260       # Distribute 55 questions across sections
261       base = SUBJECT_1MARK + SUBJECT_2MARK  # 55
262       per_section = base // num_sections
263       remainder = base % num_sections
```
**[REMOVED]**
```
(from line ~265)
    validated: list[dict[str, Any]] = []
    for q in questions:
        q["paper"] = paper
        result = await validate_question_with_retry(q)
        if result.valid:
            validated.append(q)

```
**[ADDED]**
```
265       section_list = list(subject_sections.items())
```
**[REMOVED]**
```
(from line ~267)
    return validated

```
**[ADDED]**
```
267       # Distribute 1-mark and 2-mark across sections
268       remaining_1m = SUBJECT_1MARK  # 25
269       remaining_2m = SUBJECT_2MARK  # 30
```
**[ADDED]**
```
271       for i, (sec_name, topics) in enumerate(section_list):
272           total_for_section = per_section + (1 if i < remainder else 0)
```
**[REMOVED]**
```
(from line ~274)
# ─── Full exam generation orchestrator ──────────────────────────────────────

```
**[ADDED]**
```
274           # Split into 1-mark and 2-mark proportionally
275           sec_1m = round(total_for_section * SUBJECT_1MARK / base)
276           sec_2m = total_for_section - sec_1m
```
**[ADDED]**
```
278           # Clamp to remaining
279           sec_1m = min(sec_1m, remaining_1m)
280           sec_2m = min(sec_2m, remaining_2m)
```
**[REMOVED]**
```
(from line ~282)
async def generate_exam_questions(
    db: AsyncSession,
    exam_id: str,
    paper: str,
    scope: str,
    selected_topics: list[str] | None,
    difficulty: str,
    types_ratio: dict[str, float],
) -> tuple[list[dict[str, Any]], int]:
    """
    Orchestrates full exam generation for one exam.

```
**[ADDED]**
```
282           # If we under-allocated, adjust
283           if sec_1m + sec_2m < total_for_section:
284               diff = total_for_section - sec_1m - sec_2m
285               if remaining_1m - sec_1m >= diff:
286                   sec_1m += diff
287               else:
288                   sec_2m += diff
```
**[REMOVED]**
```
(from line ~290)
    Returns (all_validated_questions, failed_count).

```
**[ADDED]**
```
290           remaining_1m -= sec_1m
291           remaining_2m -= sec_2m
```
**[REMOVED]**
```
(from line ~293)
    Generation order:
      - 2 GA batches × 5 = 10 questions
      - 11 subject batches × 5 = 55 questions
      Total: 65 questions
    """
    all_questions: list[dict[str, Any]] = []
    failed_count = 0

```
**[ADDED]**
```
293           # Determine types for this section's questions
294           for marks_val, count in [(1, sec_1m), (2, sec_2m)]:
295               if count == 0:
296                   continue
```
**[REMOVED]**
```
(from line ~298)
    topics_filter = selected_topics if scope == "topic" else None

```
**[ADDED]**
```
298               types_dist = _distribute_types(count, types_ratio)
299               diff_level = _pick_difficulty(difficulty, marks_val)
```
**[REMOVED]**
```
(from line ~301)
    # ── GA questions (2 batches) ──
    for batch_i in range(2):
        batch = await generate_ga_batch(db, difficulty, batch_i)
        all_questions.extend(batch)
        failed_in_batch = 5 - len(batch)
        failed_count += failed_in_batch
        await update_exam_progress(
            db, exam_id, completed=len(all_questions), failed=failed_count
        )

```
**[ADDED]**
```
301               # Split into batches of max 5
302               specs_for_batch = _build_question_specs(types_dist, marks_val)
```
**[REMOVED]**
```
(from line ~304)
    # ── Subject questions (11 batches) ──
    for batch_i in range(11):
        batch = await generate_subject_batch(
            db, paper, difficulty, types_ratio, batch_i, topics_filter

```
**[ADDED]**
```
304               for chunk_start in range(0, len(specs_for_batch), 5):
305                   chunk = specs_for_batch[chunk_start : chunk_start + 5]
306                   type_counts: dict[str, int] = {}
307                   for s in chunk:
308                       type_counts[s] = type_counts.get(s, 0) + 1
309   
310                   batches.append({
311                       "section_name": sec_name,
312                       "paper": paper,
313                       "is_ga": False,
314                       "topics": topics,
315                       "marks": marks_val,
316                       "count": len(chunk),
317                       "types": type_counts,
318                       "difficulty": diff_level,
319                   })
320   
321       return batches
322   
323   
324   def _distribute_types(count: int, ratio: dict[str, float]) -> dict[str, int]:
325       """Distribute `count` questions across MCQ/MSQ/NAT based on ratio."""
326       mcq = round(count * ratio.get("MCQ", 0.6))
327       msq = round(count * ratio.get("MSQ", 0.2))
328       nat = count - mcq - msq  # remainder goes to NAT
329   
330       # Ensure no negatives
331       if nat < 0:
332           nat = 0
333           msq = count - mcq
334   
335       return {"MCQ": mcq, "MSQ": msq, "NAT": nat}
336   
337   
338   def _build_question_specs(types_dist: dict[str, int], marks: int) -> list[str]:
339       """Build a flat list of type strings, e.g., ['MCQ', 'MCQ', 'MSQ', 'NAT']."""
340       specs: list[str] = []
341       for qtype, count in types_dist.items():
342           specs.extend([qtype] * count)
343       return specs
344   
345   
346   def _pick_difficulty(difficulty: str, marks: int) -> str:
347       """Pick difficulty for a batch."""
348       if difficulty != "auto":
349           return difficulty
350       # Auto: 1-mark tends easier, 2-mark tends harder
351       return "medium" if marks == 1 else "hard"
352   
353   
354   async def _generate_one_batch(batch_spec: dict) -> list[dict]:
355       """Generate one batch of questions via LLM."""
356       is_ga = batch_spec["is_ga"]
357       prompt_template = _GA_PROMPT if is_ga else _BATCH_PROMPT
358   
359       # Build the question specs text
360       specs_lines = []
361       idx = 1
362       for qtype, count in batch_spec["types"].items():
363           for _ in range(count):
364               specs_lines.append(f"{idx}. {qtype}, {batch_spec['marks']} mark(s)")
365               idx += 1
366   
367       question_specs = "\n".join(specs_lines)
368   
369       # Build topics list
370       topics_list = "\n".join(f"- {t}" for t in batch_spec["topics"])
371   
372       # Format user prompt
373       if is_ga:
374           user_prompt = prompt_template["user_prompt_template"].format(
375               count=batch_spec["count"],
376               marks=batch_spec["marks"],
377               difficulty=batch_spec["difficulty"],
378               topics_list=topics_list,
```
**[REMOVED]**
```
(from line ~380)
        all_questions.extend(batch)
        failed_in_batch = 5 - len(batch)
        failed_count += failed_in_batch
        await update_exam_progress(
            db, exam_id, completed=len(all_questions), failed=failed_count

```
**[ADDED]**
```
380       else:
381           user_prompt = prompt_template["user_prompt_template"].format(
382               count=batch_spec["count"],
383               paper=batch_spec["paper"],
384               paper_full_name=PAPER_NAMES.get(batch_spec["paper"], batch_spec["paper"]),
385               section_name=batch_spec["section_name"],
386               difficulty=batch_spec["difficulty"],
387               question_specs=question_specs,
388               topics_list=topics_list,
```
**[REMOVED]**
```
(from line ~391)
    return all_questions, failed_count

```
**[ADDED]**
```
391       system_prompt = prompt_template["system_prompt"]
392   
393       # Call LLM
394       raw_response = await call_llm(
395           system_prompt=system_prompt,
396           user_prompt=user_prompt,
397           temperature=settings.LLM_TEMPERATURE,
398       )
399   
400       # Parse JSON
401       questions = extract_json_array(raw_response)
402   
403       # Ensure section_name is set correctly
404       for q in questions:
405           if is_ga:
406               q["section_name"] = "General Aptitude"
407           elif not q.get("section_name"):
408               q["section_name"] = batch_spec["section_name"]
409   
410       return questions
411   
412   
413   async def _store_questions(
414       db: AsyncSession,
415       questions: list[dict],
416       exam: Exam,
417   ) -> list[uuid.UUID]:
418       """Store generated questions in the question_bank table."""
419       stored_ids: list[uuid.UUID] = []
420   
421       for q in questions:
422           qb = QuestionBank(
423               id=uuid.uuid4(),
424               paper=exam.paper if q.get("section_name") != "General Aptitude" else "GA",
425               question_type=q["question_type"],
426               marks=q["marks"],
427               difficulty=q.get("difficulty", "medium"),
428               difficulty_score=q.get("difficulty_score", 0.5),
429               section_name=q["section_name"],
430               topic=q.get("topic", "General"),
431               stem_tex=q["stem_tex"],
432               code_snippet=q.get("code_snippet"),
433               code_language=q.get("code_language"),
434               choices=q.get("choices"),
435               answer=q["answer"],
436               solution_tex=q["solution_tex"],
437               estimated_time_seconds=q.get("estimated_time_seconds"),
438               llm_model=settings.NEBIUS_MODEL,
439               llm_prompt_version="1.0",
440               validated=True,
441           )
442           db.add(qb)
443           stored_ids.append(qb.id)
444   
445       await db.flush()
446       return stored_ids
447   
448   
449   async def _set_error(db: AsyncSession, exam_id: uuid.UUID, error_msg: str) -> None:
450       """Mark an exam generation as failed via generation_progress."""
451       exam = await db.get(Exam, exam_id)
452       if exam:
453           exam.generation_progress = {
454               **(exam.generation_progress or {}),
455               "error": error_msg,
456           }
457           await db.commit()
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\exam_assembler.py
*Saved at: 3/23/2026, 1:43:01 PM*

**[REMOVED]**
```
(from line ~2)
Exam assembler: selects exactly 65 questions following GATE 2026 distribution,
stores them in question_bank, and updates the exam record.

```
**[ADDED]**
```
2     Assembles a final 65-question exam from the pool of generated questions,
3     following the official GATE 2026 distribution rules.
```
**[REMOVED]**
```
(from line ~6)
import uuid

```
**[ADDED]**
```
6     import logging
7     import random
```
**[REMOVED]**
```
(from line ~10)
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

```
**[ADDED]**
```
10    from app.core.llm_config import (
11        GA_1MARK,
12        GA_2MARK,
13        GA_QUESTIONS,
14        SUBJECT_1MARK,
15        SUBJECT_2MARK,
16        SUBJECT_QUESTIONS,
17        GATE_TOTAL_QUESTIONS,
18    )
```
**[REMOVED]**
```
(from line ~20)
from app.models.exam import Exam
from app.models.question_bank import QuestionBank

```
**[ADDED]**
```
20    logger = logging.getLogger(__name__)
```
**[REMOVED]**
```
(from line ~23)
# ─── GATE 2026 distribution constants ───────────────────────────────────────

```
**[ADDED]**
```
23    def assemble_exam(
24        generated_questions: list[dict],
25        paper: str,
26    ) -> tuple[list[dict], list[dict]]:
27        """
28        Select and order exactly 65 questions from the generated pool.
```
**[REMOVED]**
```
(from line ~30)
GA_1MARK_COUNT = 5
GA_2MARK_COUNT = 5
SUBJECT_1MARK_COUNT = 25
SUBJECT_2MARK_COUNT = 30

```
**[ADDED]**
```
30        Returns:
31            (question_order, selected_questions)
```
**[ADDED]**
```
33            question_order: list of dicts with keys:
34                qno, question_id, marks, type, section
```
**[REMOVED]**
```
(from line ~36)
# ─── Difficulty score mapping ────────────────────────────────────────────────


def _difficulty_to_score(difficulty: str) -> float:
    mapping = {"easy": 0.3, "medium": 0.6, "hard": 0.9}
    return mapping.get(difficulty, 0.5)


# ─── Progress updater ─────────────────────────────────────────────────────────


async def update_exam_progress(
    db: AsyncSession,
    exam_id: str,
    completed: int,
    failed: int,
) -> None:
    """Update the generation_progress JSON on the exam row."""
    total = completed + failed
    await db.execute(
        update(Exam)
        .where(Exam.id == exam_id)
        .values(
            generation_progress={
                "total": 65,
                "completed": completed,
                "failed": failed,
            }
        )
    )
    await db.commit()


# ─── Question selection ───────────────────────────────────────────────────────


def select_65_questions(
    all_questions: list[dict[str, Any]],
    types_ratio: dict[str, float],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:

```
**[ADDED]**
```
36            selected_questions: the actual question dicts (to store IDs)
```
**[REMOVED]**
```
(from line ~38)
    From all generated questions, select exactly 65 following GATE distribution.

```
**[ADDED]**
```
38        # ── Separate GA and Subject questions ──
39        ga_pool = [q for q in generated_questions if q.get("section_name") == "General Aptitude"]
40        subj_pool = [q for q in generated_questions if q.get("section_name") != "General Aptitude"]
```
**[REMOVED]**
```
(from line ~42)
    Returns (ga_questions, subject_questions).

```
**[ADDED]**
```
42        logger.info(f"Assembly pool: {len(ga_pool)} GA, {len(subj_pool)} Subject")
```
**[REMOVED]**
```
(from line ~44)
    GA: 5×1mark + 5×2mark = 10 questions
    Subject: 25×1mark + 30×2mark = 55 questions
    """
    ga_qs = [q for q in all_questions if q.get("paper") == "GA"]
    subject_qs = [q for q in all_questions if q.get("paper") != "GA"]

```
**[ADDED]**
```
44        # ── Select GA questions ──
45        ga_1m = _select_n(ga_pool, n=GA_1MARK, marks=1)
46        ga_2m = _select_n(ga_pool, n=GA_2MARK, marks=2)
47        ga_selected = ga_1m + ga_2m
```
**[REMOVED]**
```
(from line ~49)
    # Trim/pad GA to exactly 10
    ga_1mark = [q for q in ga_qs if q.get("marks") == 1][:GA_1MARK_COUNT]
    ga_2mark = [q for q in ga_qs if q.get("marks") == 2][:GA_2MARK_COUNT]
    ga_qs = ga_1mark + ga_2mark

```
**[ADDED]**
```
49        # ── Select Subject questions ──
50        subj_1m = _select_n(subj_pool, n=SUBJECT_1MARK, marks=1)
51        subj_2m = _select_n(subj_pool, n=SUBJECT_2MARK, marks=2)
52        subj_selected = subj_1m + subj_2m
```
**[REMOVED]**
```
(from line ~54)
    # Trim subject to at most 60 (we'll select exactly 55)
    subject_1mark = [q for q in subject_qs if q.get("marks") == 1]
    subject_2mark = [q for q in subject_qs if q.get("marks") == 2]

```
**[ADDED]**
```
54        # ── Combine ──
55        all_selected = ga_selected + subj_selected
```
**[REMOVED]**
```
(from line ~57)
    # Apply type ratio within 2-mark subject questions
    mcq_1mark = [q for q in subject_1mark if q.get("question_type") == "MCQ"]
    mcq_2mark = [q for q in subject_2mark if q.get("question_type") == "MCQ"]
    msq_2mark = [q for q in subject_2mark if q.get("question_type") == "MSQ"]
    nat_2mark = [q for q in subject_2mark if q.get("question_type") == "NAT"]

    target_mcq_1mark = int(SUBJECT_1MARK_COUNT * types_ratio.get("MCQ", 0.6))
    target_mcq_2mark = int(SUBJECT_2MARK_COUNT * types_ratio.get("MCQ", 0.6))
    target_msq = int(SUBJECT_2MARK_COUNT * types_ratio.get("MSQ", 0.2))
    target_nat = int(SUBJECT_2MARK_COUNT * types_ratio.get("NAT", 0.2))

    selected_subject = (
        mcq_1mark[:target_mcq_1mark]
        + mcq_2mark[:target_mcq_2mark]
        + msq_2mark[:target_msq]
        + nat_2mark[:target_nat]

```
**[ADDED]**
```
57        logger.info(
58            f"Assembled: {len(ga_selected)} GA + {len(subj_selected)} Subject "
59            f"= {len(all_selected)} total"
```
**[REMOVED]**
```
(from line ~62)
    # Ensure we have exactly 55 subject questions — pad with whatever is available
    while len(selected_subject) < 55:
        for pool in [mcq_2mark, msq_2mark, nat_2mark]:
            for q in pool:
                if q not in selected_subject and len(selected_subject) < 55:
                    selected_subject.append(q)

```
**[ADDED]**
```
62        # ── Verify counts ──
63        if len(all_selected) < GATE_TOTAL_QUESTIONS:
64            logger.warning(
65                f"Only assembled {len(all_selected)}/{GATE_TOTAL_QUESTIONS} questions. "
66                f"Exam will be shorter than standard."
67            )
```
**[REMOVED]**
```
(from line ~69)
    return ga_qs, selected_subject[:55]

```
**[ADDED]**
```
69        # ── Build question_order ──
70        question_order = []
71        for i, q in enumerate(all_selected):
72            question_order.append({
73                "qno": i + 1,
74                "question_id": q.get("_id", ""),  # Will be replaced with actual UUID after storage
75                "marks": q["marks"],
76                "type": q["question_type"],
77                "section": "GA" if q.get("section_name") == "General Aptitude" else "Subject",
78                "section_name": q["section_name"],
79                "topic": q["topic"],
80            })
```
**[ADDED]**
```
82        return question_order, all_selected
```
**[REMOVED]**
```
(from line ~84)
# ─── Question ordering ────────────────────────────────────────────────────────

```
**[REMOVED]**
```
(from line ~85)

def build_question_order(
    ga_qs: list[dict[str, Any]],
    subject_qs: list[dict[str, Any]],
) -> list[str]:

```
**[ADDED]**
```
85    def _select_n(
86        pool: list[dict],
87        n: int,
88        marks: int,
89    ) -> list[dict]:
```
**[REMOVED]**
```
(from line ~91)
    Build final question ordering:
      - GA questions first (Q1–Q10)
      - Subject questions next (Q11–Q65)
      - Within each group, interleave by marks: 1mark, 1mark, 2mark, 2mark, ...

    Returns list of question IDs (UUID strings).

```
**[ADDED]**
```
91        Select n questions with the given marks value from pool.
92        Tries to maximise topic diversity.
```
**[ADDED]**
```
94        # Filter by marks
95        candidates = [q for q in pool if q.get("marks") == marks]
```
**[REMOVED]**
```
(from line ~97)
    def interleaved(qs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        one = [q for q in qs if q.get("marks") == 1]
        two = [q for q in qs if q.get("marks") == 2]
        result: list[dict[str, Any]] = []
        for o, t in zip(one, two):
            result.extend([o, t])
        if len(one) > len(two):
            result.extend(one[len(two) :])
        elif len(two) > len(one):
            result.extend(two[len(one) :])
        return result

```
**[ADDED]**
```
97        if len(candidates) <= n:
98            return candidates
```
**[REMOVED]**
```
(from line ~100)
    ordered = interleaved(ga_qs) + interleaved(subject_qs)
    return [q.get("id") or str(uuid.uuid4()) for q in ordered]

```
**[ADDED]**
```
100       # ── Diversify by topic ──
101       selected: list[dict] = []
102       used_topics: set[str] = set()
```
**[ADDED]**
```
104       # First pass: one per topic
105       shuffled = candidates[:]
106       random.shuffle(shuffled)
```
**[REMOVED]**
```
(from line ~108)
# ─── Question insertion ───────────────────────────────────────────────────────

```
**[ADDED]**
```
108       for q in shuffled:
109           topic = q.get("topic", "")
110           if topic not in used_topics and len(selected) < n:
111               selected.append(q)
112               used_topics.add(topic)
```
**[ADDED]**
```
114       # Second pass: fill remaining from unused candidates
115       if len(selected) < n:
116           remaining = [q for q in shuffled if q not in selected]
117           for q in remaining:
118               if len(selected) >= n:
119                   break
120               selected.append(q)
```
**[REMOVED]**
```
(from line ~122)
async def insert_questions(
    db: AsyncSession,
    questions: list[dict[str, Any]],
    exam_id: str,
) -> list[str]:
    """
    Insert validated question dicts into the question_bank table.
    Returns list of inserted question ID strings.
    """
    inserted_ids: list[str] = []

```
**[ADDED]**
```
122       return selected[:n]
```
**[REMOVED]**
```
(from line ~124)
    for q in questions:
        q_id = uuid.uuid4()
        row = QuestionBank(
            id=q_id,
            paper=q.get("paper", "CS"),
            question_type=q["question_type"],
            marks=q["marks"],
            difficulty=q["difficulty"],
            difficulty_score=_difficulty_to_score(q["difficulty"]),
            section_name=q["section_name"],
            topic=q["topic"],
            stem_tex=q["stem_tex"],
            code_snippet=q.get("code_snippet"),
            code_language=q.get("code_language"),
            choices=q.get("choices"),
            answer=q["answer"],
            solution_tex=q["solution_tex"],
            estimated_time_seconds=q.get("estimated_time_seconds", 180),
            provenance=[{"exam_id": exam_id}],
            llm_model="deepseek-ai/DeepSeek-V3.2",
            llm_prompt_version="1.0",
            validated=True,
            validation_notes="Auto-validated by question_validator",
        )
        db.add(row)
        inserted_ids.append(str(q_id))

```
**[REMOVED]**
```
(from line ~125)
    await db.flush()
    return inserted_ids

```
**[ADDED]**
```
125   def compute_marks_summary(question_order: list[dict]) -> dict:
126       """Compute marks breakdown for verification."""
127       ga_marks = sum(q["marks"] for q in question_order if q["section"] == "GA")
128       subj_marks = sum(q["marks"] for q in question_order if q["section"] == "Subject")
129       total_marks = ga_marks + subj_marks
```
**[ADDED]**
```
131       type_counts = {}
132       for q in question_order:
133           t = q["type"]
134           type_counts[t] = type_counts.get(t, 0) + 1
```
**[REMOVED]**
```
(from line ~136)
# ─── Final assembly ───────────────────────────────────────────────────────────


async def assemble_exam(
    db: AsyncSession,
    exam_id: str,
    all_questions: list[dict[str, Any]],
    types_ratio: dict[str, float],
) -> None:
    """
    Final assembly step:
      1. Select exactly 65 questions following GATE distribution
      2. Build ordering (GA first, then Subject)
      3. Insert into question_bank
      4. Update exam with question_ids, question_order, status="generated"
    """
    ga_qs, subject_qs = select_65_questions(all_questions, types_ratio)
    ordered_ids = build_question_order(ga_qs, subject_qs)
    all_selected = ga_qs + subject_qs

    inserted_ids = await insert_questions(db, all_selected, exam_id)

    await db.execute(
        update(Exam)
        .where(Exam.id == exam_id)
        .values(
            question_ids=inserted_ids,
            question_order=ordered_ids,
            status="generated",
            generation_progress={
                "total": 65,
                "completed": len(inserted_ids),
                "failed": 0,
            },
        )
    )
    await db.commit()

```
**[ADDED]**
```
136       return {
137           "total_questions": len(question_order),
138           "total_marks": total_marks,
139           "ga_questions": sum(1 for q in question_order if q["section"] == "GA"),
140           "ga_marks": ga_marks,
141           "subject_questions": sum(1 for q in question_order if q["section"] == "Subject"),
142           "subject_marks": subj_marks,
143           "type_counts": type_counts,
144       }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\question_validator.py
*Saved at: 3/23/2026, 1:42:47 PM*

**[REMOVED]**
```
(from line ~2)
Question validation with retry logic.

```
**[ADDED]**
```
2     Validates LLM-generated questions for structural correctness.
```
**[REMOVED]**
```
(from line ~4)
Validates each generated question against:
  1. JSON schema (required fields, correct types, marks, options)
  2. LaTeX syntax (balanced delimiters)
  3. SymPy numeric verification for NAT answers (with LLM fallback)

```
**[ADDED]**
```
4     Checks:
5       1. Required keys present
6       2. Types correct
7       3. Answer format matches question_type
8       4. Marks valid (1 or 2)
9       5. Basic NAT answer sanity via SymPy (if computable)
```
**[REMOVED]**
```
(from line ~12)
import re
import sympy
from sympy import N as sympy_n

```
**[ADDED]**
```
12    import logging
13    import math
```
**[REMOVED]**
```
(from line ~16)
from app.services.llm_service import llm_service

```
**[ADDED]**
```
16    logger = logging.getLogger(__name__)
```
**[ADDED]**
```
18    REQUIRED_KEYS = {
19        "stem_tex",
20        "code_snippet",
21        "code_language",
22        "choices",
23        "answer",
24        "question_type",
25        "marks",
26        "difficulty",
27        "difficulty_score",
28        "section_name",
29        "topic",
30        "estimated_time_seconds",
31        "solution_tex",
32    }
```
**[REMOVED]**
```
(from line ~34)
MAX_RETRIES = 3

```
**[ADDED]**
```
34    VALID_TYPES = {"MCQ", "MSQ", "NAT"}
35    VALID_DIFFICULTIES = {"easy", "medium", "hard"}
```
**[REMOVED]**
```
(from line ~38)
# ─── Result dataclass ────────────────────────────────────────────────────────


class ValidationResult:
    """Container for validation outcome."""

    def __init__(
        self,
        valid: bool,
        errors: list[str],
        retry_count: int = 0,
    ) -> None:
        self.valid = valid
        self.errors = errors
        self.retry_count = retry_count

    def __repr__(self) -> str:
        return f"ValidationResult(valid={self.valid}, errors={self.errors}, retries={self.retry_count})"


# ─── LaTeX syntax checks ─────────────────────────────────────────────────────


def check_latex_balance(text: str) -> list[str]:

```
**[ADDED]**
```
38    def validate_question(q: dict, expected_section: str | None = None) -> tuple[bool, str]:
```
**[REMOVED]**
```
(from line ~40)
    Basic LaTeX structural checks.
    Returns a list of error messages (empty = valid).

```
**[ADDED]**
```
40        Validate a single generated question dict.
41        Returns (is_valid, error_message).
```
**[REMOVED]**
```
(from line ~43)
    errors: list[str] = []

```
**[ADDED]**
```
43        # ── 1. Check required keys ──
44        missing = REQUIRED_KEYS - set(q.keys())
45        if missing:
46            return False, f"Missing keys: {missing}"
```
**[REMOVED]**
```
(from line ~48)
    # Balanced parentheses
    if text.count("(") != text.count(")"):
        errors.append(
            f"Unbalanced parentheses: {text.count('(')} '(' vs {text.count(')')} ')'"
        )

```
**[ADDED]**
```
48        # ── 2. stem_tex must be non-empty string ──
49        if not isinstance(q["stem_tex"], str) or len(q["stem_tex"].strip()) < 10:
50            return False, "stem_tex is empty or too short"
```
**[REMOVED]**
```
(from line ~52)
    # Balanced square brackets
    if text.count("[") != text.count("]"):
        errors.append(
            f"Unbalanced brackets: {text.count('[')} '[' vs {text.count(']')} ']'"
        )

```
**[ADDED]**
```
52        # ── 3. solution_tex must be non-empty ──
53        if not isinstance(q["solution_tex"], str) or len(q["solution_tex"].strip()) < 10:
54            return False, "solution_tex is empty or too short"
```
**[REMOVED]**
```
(from line ~56)
    # Balanced braces
    open_b = text.count("{")
    close_b = text.count("}")
    if open_b != close_b:
        errors.append(
            f"Unbalanced braces: {open_b} '{{' vs {close_b} '}}'"
        )

```
**[ADDED]**
```
56        # ── 4. question_type ──
57        qtype = q.get("question_type")
58        if qtype not in VALID_TYPES:
59            return False, f"Invalid question_type: {qtype}"
```
**[REMOVED]**
```
(from line ~61)
    # \left / \right balance
    left_count = len(re.findall(r"\\left\s*[([{\[]", text))
    right_count = len(re.findall(r"\\right\s*[)}\]]", text))
    if left_count != right_count:
        errors.append(
            f"Mismatched \\left/\\right: {left_count} \\left vs {right_count} \\right"
        )

```
**[ADDED]**
```
61        # ── 5. marks ──
62        marks = q.get("marks")
63        if marks not in (1, 2):
64            return False, f"Invalid marks: {marks}"
```
**[REMOVED]**
```
(from line ~66)
    # \begin / \end balance
    begin_count = len(re.findall(r"\\begin\{", text))
    end_count = len(re.findall(r"\\end\{", text))
    if begin_count != end_count:
        errors.append(
            f"Mismatched \\begin/\\end: {begin_count} vs {end_count}"
        )

```
**[ADDED]**
```
66        # ── 6. difficulty ──
67        diff = q.get("difficulty")
68        if diff not in VALID_DIFFICULTIES:
69            return False, f"Invalid difficulty: {diff}"
```
**[REMOVED]**
```
(from line ~71)
    return errors

```
**[ADDED]**
```
71        # ── 7. difficulty_score ──
72        dscore = q.get("difficulty_score")
73        if dscore is not None:
74            try:
75                dscore = float(dscore)
76                if not (0.0 <= dscore <= 1.0):
77                    return False, f"difficulty_score out of range: {dscore}"
78            except (TypeError, ValueError):
79                q["difficulty_score"] = 0.5  # fallback
```
**[ADDED]**
```
81        # ── 8. Validate answer format per type ──
82        answer = q.get("answer")
83        if not isinstance(answer, dict):
84            return False, f"answer must be a dict, got {type(answer).__name__}"
```
**[REMOVED]**
```
(from line ~86)
# ─── JSON schema validation ──────────────────────────────────────────────────

```
**[ADDED]**
```
86        if qtype == "MCQ":
87            valid, msg = _validate_mcq(q)
88        elif qtype == "MSQ":
89            valid, msg = _validate_msq(q)
90        elif qtype == "NAT":
91            valid, msg = _validate_nat(q)
92        else:
93            valid, msg = False, f"Unknown type: {qtype}"
```
**[ADDED]**
```
95        if not valid:
96            return False, msg
```
**[REMOVED]**
```
(from line ~98)
def validate_json_schema(question: dict[str, Any]) -> list[str]:
    """
    Check required fields and type constraints for a question dict.
    Returns a list of error messages.
    """
    errors: list[str] = []

```
**[ADDED]**
```
98        # ── 9. section_name and topic must be strings ──
99        if not isinstance(q.get("section_name"), str) or not q["section_name"].strip():
100           return False, "section_name is missing or empty"
101       if not isinstance(q.get("topic"), str) or not q["topic"].strip():
102           return False, "topic is missing or empty"
```
**[REMOVED]**
```
(from line ~104)
    required_fields = [
        "question_type", "marks", "difficulty", "section_name",
        "topic", "stem_tex", "answer", "solution_tex", "estimated_time_seconds",
    ]
    for field in required_fields:
        if field not in question:
            errors.append(f"Missing required field: {field}")

```
**[ADDED]**
```
104       # ── 10. estimated_time_seconds ──
105       ets = q.get("estimated_time_seconds")
106       if ets is not None:
107           try:
108               q["estimated_time_seconds"] = int(ets)
109           except (TypeError, ValueError):
110               q["estimated_time_seconds"] = 120  # default
```
**[REMOVED]**
```
(from line ~112)
    qtype = question.get("question_type")
    if qtype not in ("MCQ", "MSQ", "NAT"):
        errors.append(f"Invalid question_type: {qtype!r}")

```
**[ADDED]**
```
112       return True, "OK"
```
**[REMOVED]**
```
(from line ~114)
    marks = question.get("marks")
    if marks not in (1, 2):
        errors.append(f"Invalid marks (must be 1 or 2): {marks}")

```
**[REMOVED]**
```
(from line ~115)
    difficulty = question.get("difficulty")
    if difficulty not in ("easy", "medium", "hard"):
        errors.append(f"Invalid difficulty: {difficulty!r}")

```
**[ADDED]**
```
115   def _validate_mcq(q: dict) -> tuple[bool, str]:
116       """MCQ: 4 choices, answer.index is int 0-3."""
117       choices = q.get("choices")
118       if not isinstance(choices, list) or len(choices) != 4:
119           return False, f"MCQ must have exactly 4 choices, got {type(choices)}"
```
**[REMOVED]**
```
(from line ~121)
    # Choices validation
    choices = question.get("choices")
    if qtype in ("MCQ", "MSQ"):
        if not isinstance(choices, list) or len(choices) != 4:
            errors.append(
                f"{qtype} must have exactly 4 choices, got {choices!r}"
            )

```
**[ADDED]**
```
121       answer = q["answer"]
122       idx = answer.get("index")
123       if idx is None:
124           # Try to extract from other formats
125           if "indices" in answer and len(answer["indices"]) == 1:
126               q["answer"] = {"index": answer["indices"][0]}
127               idx = answer["indices"][0]
```
**[REMOVED]**
```
(from line ~129)
            labels = {c.get("label") for c in choices if c}
            if labels != {"A", "B", "C", "D"}:
                errors.append(f"Choices must have labels A,B,C,D, got {labels}")
    elif qtype == "NAT":
        if choices is not None:
            errors.append(f"NAT questions must have null choices, got {choices!r}")

```
**[ADDED]**
```
129               return False, "MCQ answer must have 'index' key"
```
**[REMOVED]**
```
(from line ~131)
    # Answer structure
    answer = question.get("answer", {})
    if qtype == "MCQ":
        correct = answer.get("correct")
        if correct not in ("A", "B", "C", "D"):
            errors.append(f"MCQ correct answer must be A/B/C/D, got {correct!r}")
    elif qtype == "MSQ":
        correct = answer.get("correct", [])
        if not isinstance(correct, list) or len(correct) == 0:
            errors.append(f"MSQ correct answer must be non-empty list, got {correct!r}")
    elif qtype == "NAT":
        correct_val = answer.get("correct")
        if not isinstance(correct_val, (int, float)):
            errors.append(f"NAT correct answer must be numeric, got {correct_val!r}")

```
**[ADDED]**
```
131       try:
132           idx = int(idx)
133       except (TypeError, ValueError):
134           return False, f"MCQ answer.index must be int, got {idx}"
```
**[REMOVED]**
```
(from line ~136)
    return errors

```
**[ADDED]**
```
136       if idx < 0 or idx > 3:
137           return False, f"MCQ answer.index must be 0-3, got {idx}"
```
**[ADDED]**
```
139       q["answer"] = {"index": idx}
140       return True, "OK"
```
**[REMOVED]**
```
(from line ~142)
# ─── NAT answer verification ─────────────────────────────────────────────────

```
**[ADDED]**
```
143   def _validate_msq(q: dict) -> tuple[bool, str]:
144       """MSQ: 4 choices, answer.indices is list of ints, 1-3 correct."""
145       choices = q.get("choices")
146       if not isinstance(choices, list) or len(choices) != 4:
147           return False, f"MSQ must have exactly 4 choices, got {type(choices)}"
```
**[REMOVED]**
```
(from line ~149)
def _extract_expr_from_stem(stem_tex: str) -> str | None:
    """Extract a mathematical expression from a LaTeX stem for SymPy evaluation."""
    patterns = [
        r"\$([^$]+)\$",          # $...$
        r"\\\(([^\\)]+)\\\)",  # \(...\)

```
**[ADDED]**
```
149       answer = q["answer"]
150       indices = answer.get("indices")
```
**[ADDED]**
```
152       if indices is None:
153           # Maybe LLM used "index" instead
154           if "index" in answer:
155               indices = [answer["index"]]
156           else:
157               return False, "MSQ answer must have 'indices' key"
```
**[REMOVED]**
```
(from line ~159)
        r"=\s*([\d\.\+\-\*\/\(\)\s\^]+?)(?:\s*[,\.]|$)",  # = expression
    ]
    for pattern in patterns:
        m = re.search(pattern, stem_tex)
        if m:
            return m.group(1).strip()
    return None

```
**[ADDED]**
```
159       if not isinstance(indices, list):
160           return False, f"MSQ answer.indices must be a list, got {type(indices)}"
```
**[ADDED]**
```
162       if len(indices) < 1 or len(indices) > 3:
163           return False, f"MSQ must have 1-3 correct indices, got {len(indices)}"
```
**[REMOVED]**
```
(from line ~165)
async def verify_nat_answer(question: dict[str, Any]) -> tuple[bool, str]:
    """
    Verify a NAT answer using SymPy numerically.
    Falls back to LLM verification if SymPy cannot parse the expression.
    Returns (is_correct, notes).
    """
    answer_data = question.get("answer", {})
    correct_val = answer_data.get("correct")
    tolerance = answer_data.get("tolerance", 0.01)
    stem_tex = question.get("stem_tex", "")

```
**[ADDED]**
```
165       try:
166           indices = [int(i) for i in indices]
167       except (TypeError, ValueError):
168           return False, "MSQ answer.indices must be integers"
```
**[REMOVED]**
```
(from line ~170)
    # Try SymPy first
    expr_str = _extract_expr_from_stem(stem_tex)
    if expr_str:
        try:
            expr = sympy.parse_expr(expr_str)
            computed = float(sympy_n(expr))
            error = abs(computed - correct_val)
            within_tol = error <= tolerance
            return within_tol, f"sympy computed={computed:.6f}, error={error:.6f}"
        except Exception:
            # SymPy failed — fall through to LLM fallback
            pass

```
**[ADDED]**
```
170       if any(i < 0 or i > 3 for i in indices):
171           return False, f"MSQ indices must be 0-3, got {indices}"
```
**[REMOVED]**
```
(from line ~173)
    # LLM fallback
    prompt_text = (
        f"Question stem: {stem_tex}\n"
        f"Correct numerical answer: {correct_val}\n"
        f"Tolerance: {tolerance}\n\n"
        "Verify if this answer is mathematically correct for the given question. "
        "Return JSON with fields: verified (bool), computed_value (number), "
        "submitted_value (number), absolute_error (number), "
        "within_tolerance (bool), notes (string)."
    )
    messages = [{"role": "user", "content": prompt_text}]

```
**[ADDED]**
```
173       q["answer"] = {"indices": sorted(set(indices))}
174       return True, "OK"
```
**[REMOVED]**
```
(from line ~176)
    try:
        result = await llm_service.chat_completion(messages)
        within_tol = result.get("within_tolerance", False)
        notes = result.get("notes", "")
        return within_tol, f"llm: {notes}"
    except Exception as exc:
        return True, f"llm verification skipped: {exc}"

```
**[ADDED]**
```
177   def _validate_nat(q: dict) -> tuple[bool, str]:
178       """NAT: choices must be null, answer has value + tolerance."""
179       if q.get("choices") is not None:
180           q["choices"] = None  # auto-fix
```
**[REMOVED]**
```
(from line ~182)
# ─── Full validation pipeline ────────────────────────────────────────────────

```
**[ADDED]**
```
182       answer = q["answer"]
183       value = answer.get("value")
```
**[ADDED]**
```
185       if value is None:
186           return False, "NAT answer must have 'value' key"
```
**[REMOVED]**
```
(from line ~188)
async def validate_question(
    question: dict[str, Any],
    retry_count: int = 0,
) -> ValidationResult:
    """
    Run the full validation pipeline on a single question dict.
    """
    errors: list[str] = []

```
**[ADDED]**
```
188       try:
189           value = float(value)
190       except (TypeError, ValueError):
191           return False, f"NAT answer.value must be numeric, got {value}"
```
**[REMOVED]**
```
(from line ~193)
    # 1. JSON schema check
    errors.extend(validate_json_schema(question))

```
**[ADDED]**
```
193       if math.isnan(value) or math.isinf(value):
194           return False, "NAT answer.value is NaN or Inf"
```
**[REMOVED]**
```
(from line ~196)
    # 2. LaTeX syntax check on stem and solution
    for field in ("stem_tex", "solution_tex"):
        if field in question and question[field]:
            latex_errors = check_latex_balance(question[field])
            errors.extend(f"{field}: {e}" for e in latex_errors)

```
**[ADDED]**
```
196       tolerance = answer.get("tolerance", 0.01)
197       try:
198           tolerance = float(tolerance)
199       except (TypeError, ValueError):
200           tolerance = 0.01
```
**[REMOVED]**
```
(from line ~202)
    # 3. NAT answer verification via SymPy (skip if already errors)
    if question.get("question_type") == "NAT" and not errors:
        is_correct, notes = await verify_nat_answer(question)
        if not is_correct:
            errors.append(f"NAT answer verification failed: {notes}")

```
**[ADDED]**
```
202       if tolerance < 0:
203           tolerance = abs(tolerance)
```
**[REMOVED]**
```
(from line ~205)
    if errors:
        return ValidationResult(
            valid=False,
            errors=errors,
            retry_count=retry_count,
        )

```
**[ADDED]**
```
205       q["answer"] = {"value": value, "tolerance": tolerance}
206       return True, "OK"
```
**[REMOVED]**
```
(from line ~208)
    return ValidationResult(valid=True, errors=[], retry_count=retry_count)

```
**[REMOVED]**
```
(from line ~209)

async def validate_question_with_retry(question: dict[str, Any]) -> ValidationResult:

```
**[ADDED]**
```
209   def validate_batch(
210       questions: list[dict],
211       expected_section: str | None = None,
212   ) -> list[dict]:
```
**[REMOVED]**
```
(from line ~214)
    Validate with up to MAX_RETRIES on failure.
    Returns the result of the last attempt.

```
**[ADDED]**
```
214       Validate a batch of questions. Returns only the valid ones.
```
**[REMOVED]**
```
(from line ~216)
    result = await validate_question(question, retry_count=0)
    for attempt in range(1, MAX_RETRIES + 1):
        if result.valid:
            break
        result = await validate_question(question, retry_count=attempt)
    return result

```
**[ADDED]**
```
216       valid = []
217       for i, q in enumerate(questions):
218           is_valid, msg = validate_question(q, expected_section)
219           if is_valid:
220               valid.append(q)
221           else:
222               logger.warning(f"Question {i + 1} in batch failed validation: {msg}")
223       return valid
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\llm_queue.py
*Saved at: 3/23/2026, 1:42:28 PM*

**[REMOVED]**
```
(from line ~2)
asyncio.Queue singleton for sequential LLM processing.

One generation job processes at a time — others wait in the queue.
The worker is started/stopped via the FastAPI lifespan in main.py.

```
**[ADDED]**
```
2     Simple async queue that serialises exam-generation jobs.
3     Ensures only one exam is being generated at a time.
4     Individual LLM calls within a job use the semaphore in llm_service.
```
**[ADDED]**
```
8     import logging
```
**[REMOVED]**
```
(from line ~10)
from dataclasses import dataclass
from typing import Callable, Awaitable

```
**[ADDED]**
```
10    from typing import Callable, Coroutine, Any
```
**[REMOVED]**
```
(from line ~12)
# Module-level singleton queue
_queue: asyncio.Queue["GenerationJob | None"] = asyncio.Queue()

```
**[ADDED]**
```
12    logger = logging.getLogger(__name__)
```
**[REMOVED]**
```
(from line ~15)
@dataclass
class GenerationJob:
    """A single exam generation job placed in the queue."""
    exam_id: uuid.UUID
    paper: str
    scope: str
    selected_topics: list[str] | None
    difficulty: str
    types_ratio: dict[str, float]

```
**[ADDED]**
```
15    class LLMQueue:
16        """In-process async queue for exam generation jobs."""
```
**[ADDED]**
```
18        def __init__(self) -> None:
19            self._queue: asyncio.Queue[
20                tuple[Callable[..., Coroutine], tuple, asyncio.Future]
21            ] = asyncio.Queue()
22            self._processing = False
```
**[REMOVED]**
```
(from line ~24)
def get_queue() -> asyncio.Queue["GenerationJob | None"]:
    """Returns the singleton queue instance."""
    return _queue

```
**[ADDED]**
```
24        async def enqueue(
25            self, task_fn: Callable[..., Coroutine], *args: Any
26        ) -> Any:
27            """
28            Add a generation job to the queue.
29            Returns the result when the job completes.
30            """
31            future: asyncio.Future = asyncio.get_event_loop().create_future()
32            await self._queue.put((task_fn, args, future))
```
**[ADDED]**
```
34            if not self._processing:
35                asyncio.create_task(self._process())
```
**[REMOVED]**
```
(from line ~37)
async def enqueue(job: GenerationJob) -> None:
    """Add a generation job to the queue."""
    await _queue.put(job)

```
**[ADDED]**
```
37            return await future
```
**[ADDED]**
```
39        def enqueue_fire_and_forget(
40            self, task_fn: Callable[..., Coroutine], *args: Any
41        ) -> None:
42            """Add a generation job without waiting for the result."""
43            future: asyncio.Future = asyncio.get_event_loop().create_future()
44            asyncio.ensure_future(self._queue.put((task_fn, args, future)))
```
**[REMOVED]**
```
(from line ~46)
async def shutdown_queue() -> None:
    """Signal the worker to stop by sending the None sentinel."""
    await _queue.put(None)

```
**[ADDED]**
```
46            if not self._processing:
47                asyncio.ensure_future(self._process())
```
**[ADDED]**
```
49        async def _process(self) -> None:
50            self._processing = True
51            logger.info("LLM queue worker started")
```
**[REMOVED]**
```
(from line ~53)
async def run_worker(
    process_fn: Callable[[GenerationJob], Awaitable[None]],
) -> None:
    """
    Long-running worker coroutine. Runs inside an asyncio.Task managed
    by the FastAPI lifespan. Processes one job at a time sequentially.
    """
    while True:
        job = await _queue.get()
        if job is None:
            # Shutdown sentinel received
            break
        try:
            await process_fn(job)
        except Exception as exc:
            print(f"[llm_queue] Job {job.exam_id} failed: {exc}")
        finally:
            _queue.task_done()

```
**[ADDED]**
```
53            while not self._queue.empty():
54                task_fn, args, future = await self._queue.get()
55                job_id = str(uuid.uuid4())[:8]
56    
57                try:
58                    logger.info(f"[Job {job_id}] Starting")
59                    result = await task_fn(*args)
60                    if not future.done():
61                        future.set_result(result)
62                    logger.info(f"[Job {job_id}] Completed")
63                except Exception as exc:
64                    logger.error(f"[Job {job_id}] Failed: {exc}")
65                    if not future.done():
66                        future.set_exception(exc)
67                finally:
68                    self._queue.task_done()
69    
70            self._processing = False
71            logger.info("LLM queue worker idle")
72    
73    
74    # Global singleton
75    generation_queue = LLMQueue()
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\llm_service.py
*Saved at: 3/23/2026, 1:41:41 PM*

**[REMOVED]**
```
(from line ~2)
Nebius API client using the OpenAI Python SDK.

Base URL : https://api.tokenfactory.us-central1.nebius.com/v1/
Model    : deepseek-ai/DeepSeek-V3.2

```
**[ADDED]**
```
2     Wrapper around the Nebius API (OpenAI-compatible) for LLM calls.
```
**[ADDED]**
```
5     import asyncio
```
**[REMOVED]**
```
(from line ~7)
import os
from typing import Any

```
**[ADDED]**
```
7     import logging
8     import re
```
**[REMOVED]**
```
(from line ~12)
NEBIUS_BASE_URL = "https://api.tokenfactory.us-central1.nebius.com/v1/"
MODEL_NAME = "deepseek-ai/DeepSeek-V3.2"

```
**[ADDED]**
```
12    from app.core.config import settings
```
**[ADDED]**
```
14    logger = logging.getLogger(__name__)
```
**[REMOVED]**
```
(from line ~16)
class LLMService:
    """Thin wrapper around the Nebius OpenAI-compatible API."""

```
**[ADDED]**
```
16    # ── Async semaphore to limit concurrent LLM calls ──
17    _llm_semaphore = asyncio.Semaphore(2)
```
**[REMOVED]**
```
(from line ~19)
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None

```
**[ADDED]**
```
19    # ── Lazy-initialised client ──
20    _client: AsyncOpenAI | None = None
```
**[REMOVED]**
```
(from line ~22)
    def _get_client(self) -> AsyncOpenAI:
        api_key = os.environ.get("NEBIUS_API_KEY")
        if not api_key:
            raise RuntimeError(
                "NEBIUS_API_KEY environment variable is not set. "
                "Set it in your .env file or environment."
            )
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=NEBIUS_BASE_URL,
                api_key=api_key,
            )
        return self._client

```
**[REMOVED]**
```
(from line ~23)
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Send a chat completion request to Nebius DeepSeek-V3.2.
        Returns the parsed JSON from the model's response content.
        Strips markdown code fences automatically.
        """
        client = self._get_client()

```
**[ADDED]**
```
23    def _get_client() -> AsyncOpenAI:
24        global _client
25        if _client is None:
26            _client = AsyncOpenAI(
27                base_url=settings.NEBIUS_BASE_URL,
28                api_key=settings.NEBIUS_API_KEY,
29            )
30        return _client
```
**[REMOVED]**
```
(from line ~32)
        kwargs: dict[str, Any] = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
        }

```
**[REMOVED]**
```
(from line ~33)
        if response_format:
            kwargs["response_format"] = response_format

```
**[ADDED]**
```
33    async def call_llm(
34        system_prompt: str,
35        user_prompt: str,
36        temperature: float | None = None,
37        max_tokens: int | None = None,
38        retries: int = 2,
39    ) -> str:
40        """
41        Call the LLM with rate-limiting (semaphore) and retry logic.
42        Returns the raw text content from the LLM response.
43        """
44        client = _get_client()
45        temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
46        tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS
```
**[REMOVED]**
```
(from line ~48)
        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

```
**[ADDED]**
```
48        last_error: Exception | None = None
```
**[REMOVED]**
```
(from line ~50)
        # Strip markdown code fences
        text = content.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

```
**[ADDED]**
```
50        for attempt in range(1, retries + 2):  # retries + 1 total attempts
51            try:
52                async with _llm_semaphore:
53                    logger.info(f"LLM call attempt {attempt} (temp={temp})")
```
**[REMOVED]**
```
(from line ~55)
        return json.loads(text)

```
**[ADDED]**
```
55                    response = await client.chat.completions.create(
56                        model=settings.NEBIUS_MODEL,
57                        messages=[
58                            {"role": "system", "content": system_prompt},
59                            {"role": "user", "content": user_prompt},
60                        ],
61                        temperature=temp,
62                        max_tokens=tokens,
63                    )
```
**[ADDED]**
```
65                    content = response.choices[0].message.content
66                    if not content:
67                        raise ValueError("LLM returned empty content")
```
**[REMOVED]**
```
(from line ~69)
# Module-level singleton
llm_service = LLMService()

```
**[ADDED]**
```
69                    logger.info(
70                        f"LLM call successful (tokens: "
71                        f"in={response.usage.prompt_tokens}, "
72                        f"out={response.usage.completion_tokens})"
73                    )
74                    return content
75    
76            except Exception as exc:
77                last_error = exc
78                logger.warning(f"LLM call attempt {attempt} failed: {exc}")
79                if attempt <= retries:
80                    wait = 2 ** attempt  # exponential backoff: 2, 4 seconds
81                    logger.info(f"Retrying in {wait}s...")
82                    await asyncio.sleep(wait)
83    
84        raise RuntimeError(
85            f"LLM call failed after {retries + 1} attempts: {last_error}"
86        )
87    
88    
89    def extract_json_array(text: str) -> list[dict]:
90        """
91        Extract a JSON array from LLM response text.
92        Handles markdown code fences and extra surrounding text.
93        """
94        cleaned = text.strip()
95    
96        # 1. Try markdown code fence: ```json ... ``` or ``` ... ```
97        fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
98        match = re.search(fence_pattern, cleaned, re.DOTALL)
99        if match:
100           cleaned = match.group(1).strip()
101   
102       # 2. Find the outermost [ ... ]
103       start = cleaned.find("[")
104       end = cleaned.rfind("]")
105       if start != -1 and end != -1 and end > start:
106           cleaned = cleaned[start : end + 1]
107   
108       # 3. Parse JSON
109       try:
110           parsed = json.loads(cleaned)
111       except json.JSONDecodeError as exc:
112           logger.error(f"JSON parse error: {exc}\nRaw text:\n{text[:500]}")
113           raise ValueError(f"Failed to parse LLM response as JSON: {exc}")
114   
115       if not isinstance(parsed, list):
116           raise ValueError(f"Expected JSON array, got {type(parsed).__name__}")
117   
118       return parsed
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\prompts\verify_answer.json
*Saved at: 3/23/2026, 1:40:46 PM*

**[REMOVED]**
```
(from line ~2)
  "description": "Verify a NAT question answer using symbolic computation",
  "system_prompt": "You are an expert math verifier. Given a question, its numerical answer, and a candidate answer, determine if the candidate is correct within the given tolerance. Return ONLY valid JSON with no markdown or explanation.",
  "response_schema": {
    "type": "object",
    "required": ["verified", "computed_value", "submitted_value", "absolute_error", "within_tolerance", "notes"],
    "properties": {
      "verified": {
        "type": "boolean"
      },
      "computed_value": {
        "type": "number"
      },
      "submitted_value": {
        "type": "number"
      },
      "absolute_error": {
        "type": "number"
      },
      "within_tolerance": {
        "type": "boolean"
      },
      "notes": {
        "type": "string"
      }
    }
  }
}

```
**[ADDED]**
```
2       "version": "1.0",
3       "system_prompt": "You are a precise mathematical and logical verifier. Given a GATE exam question, its proposed answer, and solution, verify whether the answer is correct.\n\nIf the question involves computation, re-compute from scratch.\n\nOutput ONLY a JSON object with these keys:\n- \"is_correct\" (boolean): true if the proposed answer is correct, false otherwise.\n- \"computed_answer\": Your independently computed answer.\n- \"explanation\" (string): Brief reason for your verdict.\n\nReturn ONLY the JSON object. No other text.",
4       "user_prompt_template": "Verify the following GATE question:\n\nQuestion: {stem_tex}\n{code_block}\nType: {question_type}\nMarks: {marks}\nOptions: {choices}\nProposed Answer: {answer}\nProposed Solution: {solution_tex}\n\nRe-solve this independently and verify. Return JSON only."
5     }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\prompts\generate_ga.json
*Saved at: 3/23/2026, 1:40:39 PM*

**[REMOVED]**
```
(from line ~2)
  "description": "Generate 5 GATE General Aptitude questions",
  "system_prompt": "You are an expert GATE exam question writer for General Aptitude. Generate exactly 5 questions strictly following the schema below. Output ONLY valid JSON array with no markdown, no explanation, no text before or after.",
  "response_schema": {
    "type": "array",
    "items": {
      "type": "object",
      "required": [
        "question_type",
        "marks",
        "difficulty",
        "section_name",
        "topic",
        "stem_tex",
        "choices",
        "answer",
        "solution_tex",
        "estimated_time_seconds"
      ],
      "properties": {
        "question_type": {
          "type": "string",
          "enum": ["MCQ", "MSQ", "NAT"]
        },
        "marks": {
          "type": "integer",
          "enum": [1, 2]
        },
        "difficulty": {
          "type": "string",
          "enum": ["easy", "medium", "hard"]
        },
        "section_name": {
          "type": "string"
        },
        "topic": {
          "type": "string"
        },
        "stem_tex": {
          "type": "string"
        },
        "choices": {
          "type": ["array", "null"],
          "items": {
            "type": "object",
            "required": ["label", "tex"],
            "properties": {
              "label": {
                "type": "string",
                "enum": ["A", "B", "C", "D"]
              },
              "tex": {
                "type": "string"
              }
            }
          }
        },
        "answer": {
          "type": "object",
          "required": ["type", "correct"],
          "properties": {
            "type": {
              "type": "string",
              "enum": ["MCQ", "MSQ", "NAT"]
            },
            "correct": {},
            "tolerance": {
              "type": "number"
            }
          }
        },
        "solution_tex": {
          "type": "string"
        },
        "estimated_time_seconds": {
          "type": "integer"
        }
      }
    }
  }
}

```
**[ADDED]**
```
2       "version": "1.0",
3       "system_prompt": "You are an expert GATE General Aptitude question author for GATE 2026.\n\nSTRICT OUTPUT FORMAT:\nReturn ONLY a valid JSON array. No text before or after. No markdown. No explanation.\n\nEach element must be a JSON object with EXACTLY these keys:\n- \"stem_tex\" (string): Question text. Use LaTeX for math where needed.\n- \"code_snippet\": null (GA questions never have code)\n- \"code_language\": null\n- \"choices\" (array): Exactly 4 option strings.\n- \"answer\" (object): {\"index\": N} where N is the 0-based index of the correct choice.\n- \"question_type\": \"MCQ\"\n- \"marks\" (integer): 1 or 2 as specified.\n- \"difficulty\" (string): \"easy\", \"medium\", or \"hard\".\n- \"difficulty_score\" (float): 0.0 to 1.0.\n- \"section_name\": \"General Aptitude\"\n- \"topic\" (string): The specific GA topic (e.g., \"Verbal Aptitude\", \"Data interpretation\").\n- \"estimated_time_seconds\" (integer): 60-120 for 1-mark, 120-180 for 2-mark.\n- \"solution_tex\" (string): Step-by-step solution.\n\nRULES:\n1. GA questions are ALWAYS MCQ with exactly 4 options.\n2. Cover a mix of Verbal, Quantitative, Analytical, and Spatial aptitude.\n3. Verbal questions: grammar, vocabulary, reading comprehension, sentence completion.\n4. Quantitative questions: data interpretation, arithmetic, percentages, ratios.\n5. Analytical questions: logic, deduction, series, puzzles, coding-decoding.\n6. Spatial questions: pattern recognition, figure completion, transformations.\n7. 1-mark questions should be solvable in ~1 minute.\n8. 2-mark questions should require ~2-3 minutes and multi-step reasoning.\n9. Generate ORIGINAL questions. Do NOT copy from any source.\n10. Do NOT include any text outside the JSON array.",
4       "user_prompt_template": "Generate exactly {count} General Aptitude questions for GATE 2026:\n\nMarks per question: {marks}\nDifficulty: {difficulty}\n\nTopics to cover (use different topics for each question):\n{topics_list}\n\nReturn a JSON array of exactly {count} MCQ question objects. Nothing else."
5     }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\prompts\generate_batch.json
*Saved at: 3/23/2026, 1:40:27 PM*

**[REMOVED]**
```
(from line ~2)
  "description": "Generate 5 GATE subject questions (CS or DA paper)",
  "system_prompt": "You are an expert GATE exam question writer for Computer Science and Data Science papers. Generate exactly 5 multiple-choice or numerical-answer questions strictly following the schema below. Output ONLY valid JSON array with no markdown, no explanation, no text before or after.",
  "response_schema": {
    "type": "array",
    "items": {
      "type": "object",
      "required": [
        "question_type",
        "marks",
        "difficulty",
        "section_name",
        "topic",
        "stem_tex",
        "choices",
        "answer",
        "solution_tex",
        "estimated_time_seconds"
      ],
      "properties": {
        "question_type": {
          "type": "string",
          "enum": ["MCQ", "MSQ", "NAT"]
        },
        "marks": {
          "type": "integer",
          "enum": [1, 2]
        },
        "difficulty": {
          "type": "string",
          "enum": ["easy", "medium", "hard"]
        },
        "section_name": {
          "type": "string"
        },
        "topic": {
          "type": "string"
        },
        "stem_tex": {
          "type": "string"
        },
        "code_snippet": {
          "type": ["string", "null"]
        },
        "code_language": {
          "type": ["string", "null"]
        },
        "choices": {
          "type": ["array", "null"],
          "items": {
            "type": "object",
            "required": ["label", "tex"],
            "properties": {
              "label": {
                "type": "string",
                "enum": ["A", "B", "C", "D"]
              },
              "tex": {
                "type": "string"
              }
            }
          }
        },
        "answer": {
          "type": "object",
          "required": ["type", "correct"],
          "properties": {
            "type": {
              "type": "string",
              "enum": ["MCQ", "MSQ", "NAT"]
            },
            "correct": {},
            "tolerance": {
              "type": "number"
            }
          }
        },
        "solution_tex": {
          "type": "string"
        },
        "estimated_time_seconds": {
          "type": "integer"
        }
      }
    }
  }
}

```
**[ADDED]**
```
2       "version": "1.0",
3       "system_prompt": "You are an expert GATE exam question author for the GATE 2026 examination conducted by IIT Guwahati.\n\nSTRICT OUTPUT FORMAT:\nReturn ONLY a valid JSON array. No text before or after. No markdown code fences. No explanation.\n\nEach element in the array must be a JSON object with EXACTLY these keys:\n\n- \"stem_tex\" (string): Question text. Use LaTeX for math: $...$ for inline, $$...$$ for display math.\n- \"code_snippet\" (string or null): Code block if the question involves code, otherwise null.\n- \"code_language\" (string or null): \"c\" or \"python\" if code_snippet is present, otherwise null.\n- \"choices\" (array or null): Exactly 4 option strings for MCQ/MSQ. null for NAT.\n- \"answer\" (object): Format depends on type:\n    MCQ: {\"index\": N} where N is 0-based index of the single correct choice.\n    MSQ: {\"indices\": [N1, N2]} array of ALL correct 0-based indices (1 to 3 correct).\n    NAT: {\"value\": <number>, \"tolerance\": <number>} the numeric answer and acceptable tolerance.\n- \"question_type\" (string): \"MCQ\", \"MSQ\", or \"NAT\" — must match what was requested.\n- \"marks\" (integer): 1 or 2 — must match what was requested.\n- \"difficulty\" (string): \"easy\", \"medium\", or \"hard\".\n- \"difficulty_score\" (float): 0.0 (easiest) to 1.0 (hardest).\n- \"section_name\" (string): The section this question belongs to.\n- \"topic\" (string): The specific syllabus topic this question tests.\n- \"estimated_time_seconds\" (integer): Expected time to solve (60-180 for 1-mark, 120-300 for 2-mark).\n- \"solution_tex\" (string): Complete step-by-step solution. Use LaTeX for all math.\n\nRULES:\n1. Generate ORIGINAL questions — never copy from any source.\n2. Each question must test a DIFFERENT topic or sub-concept.\n3. All answers must be mathematically and logically CORRECT.\n4. Solutions must be detailed, step-by-step, and verifiable.\n5. For MSQ, there must be 1 to 3 correct options (never 0 or 4).\n6. For NAT, tolerance should be small (0.001 to 0.1 depending on the answer magnitude).\n7. Questions should be at authentic GATE difficulty — not textbook-easy.\n8. Do NOT include any text outside the JSON array.",
4       "user_prompt_template": "Generate exactly {count} GATE-style questions with these specifications:\n\nPaper: {paper} ({paper_full_name})\nSection: {section_name}\nOverall Difficulty Target: {difficulty}\n\nQuestions to generate (follow this EXACTLY):\n{question_specs}\n\nSyllabus topics for this section (cover different topics across questions):\n{topics_list}\n\nReturn a JSON array of exactly {count} question objects. Nothing else."
5     }
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\core\llm_config.py
*Saved at: 3/23/2026, 1:39:36 PM*

**[ADDED]**
```
1     """
2     Central LLM configuration constants.
3     """
4     
5     from app.core.config import settings
6     
7     LLM_CONFIG = {
8         "base_url": settings.NEBIUS_BASE_URL,
9         "api_key": settings.NEBIUS_API_KEY,
10        "model": settings.NEBIUS_MODEL,
11        "max_tokens": settings.LLM_MAX_TOKENS,
12        "temperature": settings.LLM_TEMPERATURE,
13        "temperature_verify": settings.LLM_TEMPERATURE_VERIFY,
14        "batch_size": settings.LLM_BATCH_SIZE,
15    }
16    
17    # GATE exam structure constants
18    GATE_TOTAL_QUESTIONS = 65
19    GATE_TOTAL_MARKS = 100
20    GATE_DURATION_MINUTES = 180
21    
22    GA_QUESTIONS = 10
23    GA_MARKS = 15
24    GA_1MARK = 5
25    GA_2MARK = 5
26    
27    SUBJECT_QUESTIONS = 55
28    SUBJECT_MARKS = 85
29    SUBJECT_1MARK = 25
30    SUBJECT_2MARK = 30
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\core\config.py
*Saved at: 3/23/2026, 1:37:39 PM*

**[REMOVED]**
```
(from line ~26)
        NEBIUS_BASE_URL: str = os.getenv(
        "NEBIUS_BASE_URL", "https://api.studio.nebius.com/v1/"

```
**[ADDED]**
```
26        NEBIUS_BASE_URL: str = os.getenv(
27        "NEBIUS_BASE_URL", "https://api.studio.nebius.com/v1/"
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\core\config.py
*Saved at: 3/23/2026, 1:37:32 PM*

**[ADDED]**
```
26            NEBIUS_BASE_URL: str = os.getenv(
27            "NEBIUS_BASE_URL", "https://api.studio.nebius.com/v1/"
28        )
29        NEBIUS_MODEL: str = os.getenv("NEBIUS_MODEL", "google/gemma-3-27b-it")
30    
31        # LLM defaults
32        LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "16000"))
33        LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
34        LLM_TEMPERATURE_VERIFY: float = float(os.getenv("LLM_TEMPERATURE_VERIFY", "0.1"))
35        LLM_BATCH_SIZE: int = int(os.getenv("LLM_BATCH_SIZE", "5"))
36    
37    
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\app\services\question_generator.py
*Saved at: 3/23/2026, 1:26:11 PM*

**[REMOVED]**
```
(from line ~52)
    result = await db.execute(query)

```
**[ADDED]**
```
52        result = db.execute(query)
```

---

### 📄 c:\Users\ELaunch\OneDrive\nitin-p\ai-mock\gate-mock-test\backend\.env
*Saved at: 3/20/2026, 5:39:53 PM*

**[REMOVED]**
```
(from line ~8)
NEBIUS_API_KEY=your_nebius_api_key_here

```
**[ADDED]**
```
8     NEBIUS_API_KEY=v1.CmMKHHN0YXRpY2tleS1lMDBxeXFoOXc2M2tqZmRodnISIXNlcnZpY2VhY2NvdW50LWUwMHF0YTRqbWp0dmVyZjhqeDILCIjy9M0GEIH8qXs6DAiH9YyZBxCAxerMAkACWgNlMDA.AAAAAAAAAAEjoQo26G_SS1UiDx8b2f05M8O9CRW7TYvTc6s4KS574fzGdKRs64CN2a-cVjXkDw6EnwxUccdpOS5JZFRGQF0F
```

---

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

