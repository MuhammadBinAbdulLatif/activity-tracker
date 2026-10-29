# Scope & Requirements: Dedicated Movie Detail Page & Status Management

> **Feature Directory:** `specs/movie_detail_and_management/requirements.md`  
> **Status:** Completed & Closed  

---

## 1. Overview & Objectives

Provided a dedicated, full-screen detail and management page for every tracked movie in uTrack (`/movies/<id>/`). 

Clicking any movie card or title from the list, watchlist, or history navigates directly to this dedicated space, giving users:
1. **Rich Media Presentation:** Comprehensive movie details including cast / actors, director, overview/synopsis, release date, runtime, genres, backdrop, and poster art.
2. **Status Reversion & State Management:** The ability to freely change or revert movie status (*Plan to Watch*, *Currently Watching*, *Completed*, *Dropped*) at any time (e.g. if a movie was marked "Watched" by accident, it can be reverted back to "Plan to Watch" or "Currently Watching" and have its watch date cleared or updated).
3. **Personal Chronicle Editor:** Direct editing of personal rating (1–10), review reflections, rewatch counts, watch dates, and custom notes.
4. **Custom Media Enrichment:** If the movie is custom, the user can edit or update cast/actors, director, runtime, and upload/replace custom poster artwork.

---

## 2. Functional Requirements

### 2.1 Navigation & Card Interactivity
- Every movie card and title in `/movies/` (in *Currently Watching*, *Watchlist / Queue*, and *Watched Chronicle*) is clickable and links directly to `/movies/<id>/`.
- Quick action buttons on the card (*Start Watching*, *Mark Watched*, *Rewatch*) continue to work independently.

### 2.2 Dedicated Detail View (`/movies/<id>/`)
- **Layout & Aesthetic:** Modern shadcn-inspired cinematic layout (`specs/styles.md`):
  - Atmospheric blurred backdrop header using `backdrop_url` with dark gradient vignette.
  - Large movie poster (`w-52 sm:w-64 rounded-2xl shadow-2xl`).
  - Title, tagline, release year, runtime, genres badges, and TMDB / personal rating badges.
  - Full synopsis / overview text.
- **Cast & Crew Section:**
  - Director name with title badge.
  - Top cast / actors list displayed with indicator pills.
- **Interactive Status & Progress Control:**
  - Prominent status switcher pill buttons:
    - ⏳ **Plan to Watch (Watchlist)**
    - ▶ **Currently Watching**
    - ✓ **Completed (Watched)**
    - ✖ **Dropped**
  - Instant status transition with automatic watch date handling:
    - If transitioned to *Completed*, watch date defaults to today if unset.
    - If reverted from *Completed* to *Plan to Watch*, the watch date is cleared.
- **Personal Log & Review Section:**
  - Editable star/numeric rating (0.5 to 10.0).
  - Watch date picker.
  - Rewatch count stepper.
  - Personal review textarea with formatted display.
  - Save button with toast notification.
- **Delete / Remove Action:**
  - Option to remove the movie entry from the tracker with confirmation.

### 2.3 Cast & Actor Storage in Data Model
- Added `cast` and `tagline` fields to `MovieEntry`:
  - Automatically populated from TMDB credits on addition.
  - Editable for custom movie entries.

---

## 3. Definition of Done (Acceptance Criteria)
- [x] Dedicated feature directory `specs/movie_detail_and_management/` contains `requirements.md`, `plan.md`, `validation.md`.
- [x] Clicking any movie card on `/movies/` navigates to `/movies/<id>/`.
- [x] Detail page renders movie title, poster, backdrop, synopsis, genres, director, and actors/cast.
- [x] Status can be seamlessly updated and reverted between *Plan to Watch*, *Watching*, *Completed*, and *Dropped*.
- [x] Personal rating, review, rewatch counter, and watch date can be updated and persisted.
- [x] Automated tests verify navigation, cast population, status reversion, and detail rendering.
- [x] 100% of tests pass (37/37).
- [x] Specifications marked Completed & closed, changes committed and pushed.
