# Exercises & Physical Activity Tracking — Plan Specification

> **Target Directory:** `specs/exercises_and_habits/plan.md`  
> **Status:** Completed / Closed  
> **Audience:** Development Agent & Engineering Team

---

## 1. Feature Overview & Architecture

Exercises & Habits provides physical activity logging and life progression to complement media tracking.
The user requested:
> *"start by creating all the most popular exercises. The more the exercises that you enter, the better the end result and user satisfaction will be. Make sure that it is up to standards, tested, validated, good and consistent ui"*

### 1.1 Architectural Decisions
1. **Dedicated Django App (`exercises`):**
   - Registered in `INSTALLED_APPS` in `utrack/settings.py`.
   - Dedicated `models.py`, `forms.py`, `views.py`, `urls.py`, `tests.py`.
   - Seeded curated exercise catalog / library + user custom exercises.
2. **Data Model Strategy:**
   - **`Exercise` (Catalog / Library):**
     - Canonical exercises (chest, back, legs, shoulders, arms, core, cardio, flexibility/mobility, bodyweight/calisthenics, olympic lifting).
     - Fields: `name`, `slug`, `category` (Strength, Cardio, Bodyweight, Mobility, etc.), `target_muscle_group` (Chest, Back, Quads, Hamstrings, Shoulders, Biceps, Triceps, Core, Full Body, Cardiovascular), `secondary_muscles`, `equipment_needed` (Barbell, Dumbbell, Machine, Cable, Bodyweight, Kettlebell, Resistance Band, None), `instructions`, `is_custom`, `created_by` (null for global catalog).
   - **`ExerciseLog` (Tracking & Progression):**
     - User logs workout sessions and exercise performances.
     - Key metrics: date, duration, sets, reps, weight (kg), distance (km), calories, difficulty/RPE, personal notes.
3. **Comprehensive Seed Catalog:**
   - Rich, curated catalog of **63 popular exercises** spanning all major muscle groups and modalities (Compound lifts, Isolation, Bodyweight/Calisthenics, Cardio & Endurance, Mobility & Core).
   - Automatic seeding via Django data migration `0002_seed_popular_exercises.py` so it's populated out of the box.
4. **UI Design & Aesthetic:**
   - Follows `specs/styles.md`: dark zinc/slate surfaces (`#09090b`, `#18181b`), hairline borders (`border-zinc-800`), teal/emerald accents (`#14b8a6` / `#10b981`), HTMX live filter/search, modal/drawer exercise selector, and workout logging.
   - Interactive exercise catalog explorer with category pills, muscle group filtering, and equipment filters.
   - Integrated with sidebar navigation (`dashboard/templates/dashboard/sidebar.html`).

---

## 2. Completed Implementation Deliverables

1. **Specs Phase:** Created `plan.md`, `requirements.md`, and `validation.md` under `specs/exercises_and_habits/`.
2. **App Creation & Configuration:**
   - Added `'exercises'` to `INSTALLED_APPS` in `utrack/settings.py`.
   - Included `path('exercises/', include('exercises.urls'))` in `utrack/urls.py`.
3. **Data Models & Migrations:**
   - Defined `ExerciseCategory`, `MuscleGroup`, `EquipmentType`, `Exercise`, and `ExerciseLog`.
   - Initial migration `0001_initial.py` and data migration `0002_seed_popular_exercises.py` applied.
   - 63 popular exercises seeded across Chest, Back, Legs, Shoulders, Arms, Core, Cardio, Olympic lifting, and Functional mobility.
4. **Forms & Views:**
   - `ExerciseForm` for custom movements.
   - `ExerciseLogForm` for logging sets, reps, weights, duration, distance, RPE, and notes.
   - Views for listing/filtering with HTMX live search, detail view with PR analytics, custom creation, and log deletion.
5. **Templates & UI:**
   - `exercises/list.html`, `exercises/partials/exercise_grid.html`, `exercises/detail.html`, `exercises/log_form.html`, `exercises/create.html`.
   - Updated `dashboard/templates/dashboard/sidebar.html` with active route detection.
6. **Testing & Quality Assurance:**
   - 10 automated test cases in `exercises/tests.py` passing with 100% success.
