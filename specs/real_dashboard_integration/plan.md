# Real Data Dashboard Integration — Plan Specification

> **Target Directory:** `specs/real_dashboard_integration/plan.md`  
> **Status:** Completed / Closed  
> **Audience:** Development Agent & Engineering Team

---

## 1. Feature Overview & Architecture

Replaced prototype mock generator (`dashboard/demo_data.py`) with real ORM queries across all media categories and exercises.
The user requested:
> *"time to start working on the dashboard again... it had dummy data... make sure it uses the real data now"*

### 1.1 Architectural Decisions & Implementation
1. **Unified Dashboard Aggregation Service (`dashboard/services.py`):**
   - Live query aggregation across:
     - `movies` (`MovieEntry`)
     - `series` (`SeriesEntry`, `EpisodeLog`)
     - `books` (`BookEntry`)
     - `audiobooks` (`AudiobookEntry`)
     - `comics` (`ComicMangaEntry`)
     - `games` (`GameEntry`)
     - `boardgames` (`BoardGameEntry`)
     - `exercises` (`UserExerciseTrack`, `ExerciseLog`)
2. **Real Metrics (KPIs):**
   - **Active Streak (Days):** Calculated by continuous daily activity counts up to today/yesterday.
   - **Total Items Logged / Completed This Year:** Count of all user items completed or logged in current year.
   - **Time Engaged (Hours Consumed This Month):** Aggregated movie runtimes, episodes watched, audio minutes listened, video game playtime, boardgame sessions, and exercise minutes.
   - **Daily Average (Min / Day):** Pro-rated across days elapsed this month.
3. **52-Week GitHub-Style Activity Heatmap:**
   - Aggregates daily activity dates across all 8 models into a 365-day grid with calibrated emerald intensities (0–4) and hover tooltips showing what was logged.
4. **Currently In-Progress Hub:**
   - Active entries dynamically queried (`WATCHING`, `READING`, `LISTENING`, `PLAYING`, `IN_PROGRESS`) with real progress bars, percentages, and direct detail links.
5. **Planned Queue & Recently Completed:**
   - Real queued items across all backlogs and wishlists.
   - Real completed highlights with star ratings (★★★★½) and user reviews.
6. **Graceful Zero-State Support:**
   - Empty dashboard handles 0-entry users gracefully with encouraging prompts without dividing by zero or breaking layout.
