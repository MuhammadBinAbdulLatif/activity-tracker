# Technical Implementation Plan: Movies & Series Tracking Engine

> **Feature Directory:** `specs/movies_and_series/plan.md`  
> **Status:** Draft / Active  

---

## 1. Architectural Strategy

We will deliver the tracking engines in two dedicated Django applications or a consolidated `media` app with distinct submodules. To maintain clean modularity across the project:

### Option Selected: Dedicated Apps `movies` and `series`
1. **`movies` App:**
   - Dedicated models: `Movie` / `MovieEntry`.
   - Views for `/movies/` (Watchlist, Currently Watching, Watched History).
   - Movie search & manual logging endpoints.
2. **`series` App:**
   - Dedicated models: `Series`, `Season`, `EpisodeLog`.
   - Lifecycle manager for automatic season roll-over and episode airing checks.
   - Views for `/series/` with episode stepper actions (`+1 Episode`, `Mark Season Completed`).
3. **Core Provider Service (`services/tmdb.py`):**
   - Reusable client encapsulated in a shared module.
   - Reads `TMDB_API_KEY` and `TMDB_READ_ACCESS_TOKEN` from environment.
   - Uses `requests` with connection timeouts and Redis caching (`django-redis` or LocMem cache fallback).
   - Endpoints:
     - `search_movie(query, year=None)`
     - `get_movie_details(tmdb_id)`
     - `search_tv(query, year=None)`
     - `get_tv_details(tmdb_id)`
     - `get_tv_season(tmdb_id, season_number)`

---

## 2. Step-by-Step Execution Plan

### Step 1: Specifications Authoring [IN PROGRESS]
- Complete `specs/movies_and_series/requirements.md`, `specs/movies_and_series/plan.md`, and `specs/movies_and_series/validation.md`.

### Step 2: Shared TMDB Client & Redis Caching
- Create `services/tmdb.py`:
  - Methods for searching and retrieving details for movies and TV series.
  - Redis cache keys: `tmdb:search:movie:<hash>`, `tmdb:detail:movie:<id>`, `tmdb:search:tv:<hash>`, `tmdb:detail:tv:<id>`.
  - Mock mode / fallback testing support when API calls are simulated.

### Step 3: Movies App Implementation (`movies`)
- Create app `movies` and register in `INSTALLED_APPS`.
- Define models in `movies/models.py`:
  - `MovieEntry` with user reference, TMDB metadata, tracking status, watch date, rating, review.
- Create views and HTMX-driven routes in `movies/views.py`:
  - `/movies/` (list/dashboard).
  - `/movies/search/` (HTMX live query dropdown).
  - `/movies/log/` (save TMDB item or manual item).
  - `/movies/update/<id>/` (edit rating, rewatch count, review).

### Step 4: Series App Implementation (`series`)
- Create app `series` and register in `INSTALLED_APPS`.
- Define models in `series/models.py`:
  - `SeriesEntry`, `SeasonEntry`, `EpisodeLog`.
- Implement Series Lifecycle Engine:
  - `advance_episode(series_entry)`:
    - Increments `current_episode_number`.
    - Creates `EpisodeLog` entry (timestamped for heatmaps).
    - Checks if `current_episode_number == season.episode_count`.
    - If so, triggers `complete_season(series_entry, season_number)`.
  - `complete_season(series_entry, season_number)`:
    - Marks current season completed.
    - Checks for next season in TMDB metadata.
    - If next season exists: rolls `current_season_number += 1`, resets episode to 0/1, status remains `WATCHING`.
    - If next season is unreleased: sets status to `WAITING_FOR_NEXT_SEASON` and stores expected release date.
    - If no more seasons and show status is `Ended`: sets status to `COMPLETED`.
  - `check_broadcast_updates(series_entry)`:
    - Compares user's current progress against TMDB's `next_episode_to_air` and `last_air_date`.
- Create views and HTMX-driven routes in `series/views.py`:
  - `/series/` (active show grid, up next, backlog).
  - `/series/search/` (live TMDB TV search).
  - `/series/add/` (track new show).
  - `/series/<id>/increment/` (HTMX instant `+1 Episode` trigger).

### Step 5: Templates & UI Styling
- Create templates in compliance with `specs/styles.md`:
  - `movies/list.html`, `movies/partials/search_results.html`, `movies/modals/log_modal.html`.
  - `series/list.html`, `series/partials/episode_controls.html`, `series/partials/airing_badge.html`.
- Update top sidebar links (`#movies` $\rightarrow$ `/movies/`, `#series` $\rightarrow$ `/series/`).

### Step 6: Automated Testing & Verification
- Unit tests for TMDB client (with mocked API fixtures).
- Model tests for Movie lifecycle and ratings.
- State-machine test suite for Series auto-season progression.
- Airing status and notification badge tests.

### Step 7: Specs Finalization & Git Push
- Mark all items in `specs/movies_and_series/` as completed.
- Commit and push to git.
