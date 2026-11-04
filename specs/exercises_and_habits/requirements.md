# Exercises & Physical Activity Tracking — Requirements Specification

> **Target Directory:** `specs/exercises_and_habits/requirements.md`  
> **Status:** Completed / Closed  
> **Audience:** Development Agent & Engineering Team

---

## 1. Functional Requirements Verification

### 1.1 Curated Popular Exercises Library (Extensive Seed Catalog)
- [x] **FR 1.1:** The system comes pre-populated with an extensive library of 63 curated exercises spanning:
  - **Chest:** Barbell Bench Press, Incline Dumbbell Press, Decline Barbell Bench Press, Dumbbell Chest Flyes, Push-Ups, Chest Dips, Cable Crossover, Pec Deck Machine.
  - **Back:** Barbell Conventional Deadlift, Barbell Bent-Over Row, Pull-Ups, Chin-Ups, Lat Pulldown, Seated Cable Row, Single-Arm Dumbbell Row, T-Bar Row, Face Pulls.
  - **Legs:** Barbell Back Squat, Front Squat, Leg Press, Romanian Deadlift (RDL), Bulgarian Split Squat, Walking Lunges, Barbell Hip Thrust, Leg Extension, Lying Leg Curl, Standing Calf Raise, Goblet Squat.
  - **Shoulders:** Overhead Barbell Press, Seated Dumbbell Shoulder Press, Dumbbell Lateral Raise, Arnold Press, Rear Delt Dumbbell Flyes, Cable Lateral Raise, Barbell Upright Row.
  - **Arms:** Barbell Bicep Curl, Dumbbell Hammer Curl, Incline Dumbbell Curl, Preacher Curl, Tricep Rope Pushdown, Skull Crushers, Close-Grip Barbell Bench Press, Overhead Dumbbell Tricep Extension.
  - **Core & Abdominals:** Standard Plank, Hanging Leg Raise, Ab Rollout, Cable Woodchopper, Russian Twists, Bicycle Crunches.
  - **Cardio & Conditioning:** Outdoor Running, Treadmill Running, Stationary Cycling, Indoor Rowing Machine, Jump Rope, Stairmaster, HIIT Burpees, Swimming.
  - **Functional, Olympic & Mobility:** Kettlebell Swing, Barbell Clean and Jerk, Barbell Snatch, Farmers Walk, Turkish Get-Up, Plyometric Box Jump.
- [x] **FR 1.2:** Each exercise includes category, target muscle group, secondary muscles, equipment required, instructions, and custom badge flags.

### 1.2 Custom Exercise Creation
- [x] **FR 2.1:** Users can create custom exercises tailored to their routine.
- [x] **FR 2.2:** Custom movements are attributed to `created_by` and accessible in their catalog.

### 1.3 Workout & Exercise Logging (Personal Chronicle)
- [x] **FR 3.1:** Users can log sessions with date, sets, reps, weight (kg), duration (min), distance (km), calories, RPE, and notes.
- [x] **FR 3.2:** Quick logging and personal record (PR) calculation on the exercise detail page.
- [x] **FR 3.3:** Chronological log history with deletion support.

### 1.4 Filtering & Search Experience
- [x] **FR 4.1:** Real-time HTMX instant search by name, instructions, or muscle synergists.
- [x] **FR 4.2:** Filter by Muscle Group (Chest, Back, Quads, Hamstrings, Shoulders, Arms, Core, Cardio, etc.).
- [x] **FR 4.3:** Filter by Equipment (Barbell, Dumbbell, Cable, Machine, Bodyweight, etc.).
- [x] **FR 4.4:** Tabbed views: "All Catalog", "My Logged", and "My Custom".

### 1.5 UI/UX & Design System Consistency
- [x] **FR 5.1:** Conforms to `specs/styles.md` (dark zinc aesthetic, hairline borders, teal/emerald vitality accents).
- [x] **FR 5.2:** Sidebar navigation updated with active indicator for `/exercises/`.
- [x] **FR 5.3:** Pagination and clean empty states.
