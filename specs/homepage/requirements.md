# Scope & Requirements: Dashboard & Home Page

> **Feature Directory:** `specs/homepage/requirements.md`  
> **Status:** Completed & Closed  

---

## 1. Overview & Objective
Deliver the primary dashboard experience of **uTrack** (`/`) to provide an immediate, visual, and grounded overview of the user's ongoing and planned life pursuits. 

Until dynamic provider integrations and user logging flows are fully wired in future phases, the dashboard must feature authentic, realistic mock/demo data so the user experience feels rich, tactile, and complete from day one.

---

## 2. Functional Requirements

### 2.1 Navigation & Left Sidebar
1. **Persistent Left Sidebar:**
   - Dark, sleek, and fixed/sticky on desktop; collapsible/responsive on mobile screens.
   - Branding section at the top featuring the official uTrack logo mark (`logo.svg`), app title, and chronicle tagline.
   - Primary navigation links with distinct icons:
     - **Home / Dashboard** (active state indicator)
     - **Movies**
     - **Series & TV**
     - **Books**
     - **Audiobooks**
     - **Comics & Manga**
     - **Fitness & Habits** (Life Activities)
   - Visual separator / breaker (`border-t border-zinc-800/80` with subtle spacing).
   - Bottom Profile & Settings Section:
     - Current user avatar placeholder / initial badge.
     - User's username and display moniker.
     - Quick link to **Settings** / Profile preferences.
     - Direct **Sign Out** action trigger.

### 2.2 Top Header & Quick Context
1. Modern minimalist header displaying current greetings (e.g., *"Welcome back, <username>"*), current date/time context, and quick actions (e.g., Quick Log button placeholder, Global Search input placeholder).

### 2.3 Life Activity Heatmap ("GitHub-Style Chronicle")
1. Visual 52-week / 365-day rolling activity contribution matrix.
2. Distinct intensity shading steps (from `#18181b` empty to vibrant emerald `#10b981`).
3. Tooltip or day details indicator showing what was consumed on selected dates (e.g., *"1 movie watched, 35 pages read, 1 workout"*).
4. Quick summary statistics bar:
   - Current streak (days).
   - Total activities logged this year.
   - Most active day / category.

### 2.4 "Currently In-Progress" Active Hub
Rich cards for items currently in consumption across multiple categories:
- **Watching Movies / Series:** e.g., *Dune: Part Two*, *Severance Season 2* (Season 2 Episode 4 with progress bar and quick `+1 Ep` button).
- **Reading Books:** e.g., *Project Hail Mary* (Page 214 of 496, 43% completed, progress slider/bar).
- **Audiobooks:** e.g., *Atomic Habits* (Ch. 6 of 20, speed 1.2x).
- **Comics / Manga:** e.g., *Berserk* (Chapter 182).

### 2.5 "Recently Completed & Retrospective Highlights"
- Chronological row/grid of recently finished media and activities with user star ratings, completed date, and brief snippet/reflection.

### 2.6 "Plan to Watch / Watchlist Queue"
- Sleek up-next carousel / card grid of items the user has planned to watch/read next, with priority badges and category tags.

### 2.7 Modular Demo Data Architecture
- Demo/dummy data must be structured cleanly in a dedicated context generator or helper (e.g. `dashboard/demo_data.py`) so it can be swapped seamlessly for real database queries in later phases without refactoring templates.

---

## 3. Non-Functional & Aesthetic Requirements
- Strict compliance with `specs/styles.md`: dark palette (`#09090b`), zinc borders (`#27272a`), emerald accents (`#10b981`), Inter font typography.
- Fully responsive across desktop, tablet, and mobile views.
- Clean semantic HTML structure using Django Template Language (DTL) and Tailwind CSS.

---

## 4. Definition of Done (Acceptance Criteria)
- [x] Dedicated feature directory `specs/homepage/` contains `plan.md`, `requirements.md`, and `validation.md`.
- [x] Navigating to `/` as an authenticated user renders the full sidebar, heatmap, in-progress items, recently completed items, and plan-to-watch queue.
- [x] Left sidebar contains all requested links (Books, Audiobooks, Movies, Series, Comics, Exercises), the breaker line, and the user settings/profile block.
- [x] Heatmap renders a 52-week grid with emerald activity intensity levels.
- [x] In-progress items display intuitive progress bars and category badges.
- [x] Unauthenticated users attempting to visit `/` are redirected to `/accounts/login/`.
- [x] Automated tests pass with 100% success.
- [x] Specs updated to Completed and changes committed to git.
