# Real Data Dashboard Integration — Requirements Specification

> **Target Directory:** `specs/real_dashboard_integration/requirements.md`  
> **Status:** Completed / Closed  
> **Audience:** Development Agent & Engineering Team

---

## 1. Functional Requirements Verification

### 1.1 Real Metrics Calculation
- [x] **FR 1.1:** `active_streak_days` calculates real consecutive days of logged activity ending on today or yesterday.
- [x] **FR 1.2:** `total_items_year` counts items completed or logged by the user during the current calendar year.
- [x] **FR 1.3:** `hours_consumed_month` sums logged engagement time for the current calendar month across movies, series, audiobooks, video games, board games, and exercise sessions.
- [x] **FR 1.4:** `daily_average_min` computes average daily minutes for the month.

### 1.2 52-Week Life Activity Heatmap
- [x] **FR 2.1:** The 52-week calendar grid reflects actual dates and aggregates actual user interactions across all 8 categories.
- [x] **FR 2.2:** Heatmap tooltips display the exact date, total activity count, and readable summary of what was logged on that day.
- [x] **FR 2.3:** Colors correctly scale across 5 tiers (0: dark slate background, 1: dark emerald, 2: mid emerald, 3: bright emerald, 4: peak vibrant emerald).

### 1.3 Currently In-Progress Hub
- [x] **FR 3.1:** Pulls real items with active statuses (`WATCHING`, `READING`, `LISTENING`, `PLAYING`, `IN_PROGRESS`).
- [x] **FR 3.2:** Displays real cover image, title, subtitle, calculated progress percentage, and progress labels.
- [x] **FR 3.3:** Quick links point directly to detail views for each item.

### 1.4 Planned Queue ("Up Next")
- [x] **FR 4.1:** Aggregates real planned items (`PLAN_TO_WATCH`, `PLAN_TO_READ`, `PLAN_TO_LISTEN`, `BACKLOG`, `WANT_TO_PLAY`, `PLANNED`).
- [x] **FR 4.2:** Formatted with covers, notes/tags, and category badges.

### 1.5 Recently Completed Retrospective
- [x] **FR 5.1:** Aggregates real items marked `COMPLETED` ordered by `finish_date` / `watch_date` / `updated_at` descending.
- [x] **FR 5.2:** Displays user rating stars (e.g. ★★★★☆), reviews/notes, and completion date.

### 1.6 User Isolation & Zero-Data Fallback
- [x] **FR 6.1:** All queries strictly filter by `user=request.user`. Users never see data from other users.
- [x] **FR 6.2:** When a user has 0 entries, dashboard displays motivating zero-state placeholders without division-by-zero or template errors.
