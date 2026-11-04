# Exercises & Physical Activity Tracking — Validation Specification

> **Target Directory:** `specs/exercises_and_habits/validation.md`  
> **Status:** Completed / Closed  
> **Audience:** Development Agent & Engineering Team

---

## 1. Test Verification Results

All test cases in `exercises/tests.py` ran and passed with 100% success.

### 1.1 Model & Data Validation Tests
- [x] **Curated Exercise Seed & Types Test:** Verified 63 seeded exercises exist and compute `.is_resistance_type` and `.is_cardio_type` properties accurately.
- [x] **Tracking Shelves Model Test:** Verified `UserExerciseTrack` supports `IN_PROGRESS`, `PLANNED`, and `COMPLETED`.
- [x] **Exercise Log Model Test:** Verified `ExerciseLog` records dates, sets, reps, weight, RPE, and notes.

### 1.2 View & Endpoint Validation Tests
- [x] **Exercise Shelf Dashboard (`/exercises/`):**
  - Displays user's personal shelves (`in_progress`, `planned`, `completed`).
  - Separates tracked user items from the catalog.
- [x] **Search Catalog Modal (`/exercises/search-catalog/`):**
  - HTMX search endpoint returns filtered exercises with "+ Track" actions.
- [x] **Track & Status Transitions (`/exercises/track/<id>/`, `/exercises/tracks/<id>/status/`):**
  - Correctly moves exercises across shelves and deletes on untrack.
- [x] **Form Field Tailoring Test:**
  - Verified strength/dumbbell/barbell exercises display resistance metrics only and hide cardio.
  - Verified cardio exercises display duration, distance, calories and hide sets/reps/weight.
- [x] **Custom Exercise Creator:**
  - Creates custom movement and automatically tracks it in user's routine.

### 1.3 UI & Navigation Consistency
- [x] **Sidebar Badge Neutrality:** Fixed badge to `bg-zinc-800/60 text-zinc-400` matching all other categories.
- [x] **Design Conformity:** Uses standard shadcn-style dark aesthetic (`#09090b`), dialog modals, and shelf grids matching Movies, Video Games, and Board Games.

### 1.4 Test Run Output
```
Ran 8 tests in 13.700s
OK
```
