# Exercises & Physical Activity Tracking — Plan Specification

> **Target Directory:** `specs/exercises_and_habits/plan.md`  
> **Status:** Completed / Closed  
> **Audience:** Development Agent & Engineering Team

---

## 1. Feature Architecture & Consistency Refactor

### User Feedback Addressed:
1. **Neutral Sidebar Badge:** Removed the green color accent from the sidebar badge for "Exercises & Habits" so that it matches the uniform monochromatic dark badge (`bg-zinc-800/60 text-zinc-400`) used across all other media categories.
2. **Clear Shelf Boundaries (Personal Routine vs Catalog):** Rather than overwhelming the user's primary view with all 63+ exercises, the dashboard is now organized into user shelves matching the standard uTrack UX (Movies, Video Games, Board Games):
   - **Active In Routine (`IN_PROGRESS`)**
   - **Want to Try / Planned (`PLANNED`)**
   - **Mastered / Milestones (`COMPLETED`)**
3. **Modal Picker Dialog:** A top "Add Exercise" button triggers a modal dialog where users search and filter the catalog of 63+ exercises and choose which ones to track in their routine, with a fallback for creating custom exercises.
4. **Context-Aware Form Field Tailoring:**
   - Strength / Dumbbells / Barbells / Machines display **only** relevant resistance metrics (`sets`, `reps`, `weight_kg`). Cardio metrics are omitted.
   - Cardio & Aerobic exercises (Running, Cycling, Rowing, etc.) display **only** endurance metrics (`duration_minutes`, `distance_km`, `calories_burned`).
   - Clean intensity (RPE) and form notes on both.

---

## 2. Deliverables Completed
- Models: `Exercise`, `UserExerciseTrack`, `ExerciseLog`.
- Migrations: `0001_initial`, `0002_seed_popular_exercises` (63 exercises), `0003_userexercisetrack`.
- Views: Shelf dashboard, modal catalog search with HTMX, track/untrack endpoints, tailored session logger.
- Templates: Standardized `list.html`, `detail.html`, `log_form.html`, `catalog_search_results.html`.
- Sidebar: Standardized neutral badge in `sidebar.html`.
- Tests: 8 automated tests passing (100% OK).
