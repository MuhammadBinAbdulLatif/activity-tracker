# Agent Operating Instructions

> [!IMPORTANT]
> **MANDATORY CONTEXT & COMPLIANCE DIRECTIVE**
> Before undertaking any architectural decisions, planning steps, code modifications, or refactoring in this repository, you **MUST** consult and strictly adhere to the project specification documents stored under the `specs/` directory.

---

## 1. Core Specification Documents

All development within this repository is governed by the foundational specification documents located at the root of `specs/`:

1. **`specs/mission.md`**
   - **Purpose:** Defines the high-level purpose, user persona, problem space, vision, and core philosophy of the application.
   - **Instruction:** Always align feature implementations, architectural design, and scope decisions with the mission outlined here.

2. **`specs/techstack.md`**
   - **Purpose:** Specifies the exact technology stack, libraries, frameworks, database configurations, versions, caching, and third-party dependencies approved for the project.
   - **Instruction:** Do not introduce unapproved external libraries, paradigms, or dependencies without consulting and conforming to this document.

3. **`specs/roadmap.md`**
   - **Purpose:** Provides the phased execution roadmap, category-by-category breakdown, provider strategy, and milestone checklist.
   - **Instruction:** Execute tasks sequentially adhering to the phased deliverables defined in this roadmap.

---

## 2. Feature Specification Workflow (Mandatory Protocol)

Whenever the user indicates starting a new feature, milestone, phase, or any task with resembling sentiment:

> **Do NOT write code immediately.**  
> First, create a dedicated feature folder under `specs/<feature-name>/` containing exactly these **three specification files**:

```
specs/
├── mission.md
├── techstack.md
├── roadmap.md
└── <feature-name>/          # e.g., specs/authentication/
    ├── plan.md              # What we are going to do in this step
    ├── requirements.md      # What we want to achieve & criteria for completion
    └── validation.md        # Verifiable test checklist & conditions to pass
```

### 2.1 File Responsibilities Within Each Feature Specification

1. **`plan.md` (Implementation Strategy):**
   - Step-by-step technical plan for executing the feature.
   - Architecture, modules to create or modify, routing, data models, and UI templates involved.

2. **`requirements.md` (Scope & Acceptance Criteria):**
   - Exact functional and non-functional requirements to achieve.
   - Explicit "Definition of Done" conditions that must be fulfilled before this phase can be considered completed and closed.

3. **`validation.md` (Quality Assurance & Test Gates):**
   - Concrete test cases (unit tests, integration tests, boundary conditions).
   - CLI commands to run (e.g., `python manage.py test <app>`).
   - Explicit checklist of assertions that must pass with zero failures before the feature is marked done.

### 2.2 Feature Completion & Git Protocol (Mandatory Commit & Push)

Once all requirements in `requirements.md` are fulfilled and all test gates in `validation.md` pass with 100% success:
1. **Status Update:** Update the status in all three specification files (`plan.md`, `requirements.md`, `validation.md`) to **Completed / Closed**.
2. **Git Commit & Push:** 
   - Stage all relevant implementation files, tests, static assets, migrations, and updated specifications.
   - Author a clear, semantic commit message capturing the completed specification (e.g., `feat(auth): implement baseline authentication and recovery specifications`).
   - Push the commit to the upstream repository (`git push`).
   - This formally declares that the specification lifecycle for that feature is concluded.

---

## 3. Operational Rules for the Agent

1. **Verify & Author Specs Before Action:**
   - Always inspect `specs/` prior to writing or modifying code.
   - On initiation of any feature, create `specs/<feature-name>/` with `plan.md`, `requirements.md`, and `validation.md` before touching code.
   - If any proposed change conflicts with `specs/mission.md`, `specs/techstack.md`, or `specs/roadmap.md`, pause and reconcile against the specs or request clarification.

2. **Keep Specs as Single Source of Truth:**
   - When answering questions about architecture, stack choices, progress, or verification, cross-reference these files first.

3. **Specification Maintenance:**
   - Keep the feature specification files updated as requirements evolve.
   - Ensure all specs are persisted and respected across all future sessions.
