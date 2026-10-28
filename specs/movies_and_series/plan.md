# Technical Implementation Plan: Movies & Series Tracking Engine

> **Feature Directory:** `specs/movies_and_series/plan.md`  
> **Status:** Completed & Closed  

---

## 1. Architectural Strategy

We delivered the tracking engines in two dedicated Django applications: `movies` and `series` with a shared provider service:

1. **`movies` App:**
   - Dedicated model: `MovieEntry`.
   - Views for `/movies/` (Watchlist, Currently Watching, Watched History).
   - Movie search & manual logging endpoints.
2. **`series` App:**
   - Dedicated models: `SeriesEntry`, `SeasonEntry`, `EpisodeLog`.
   - Lifecycle manager (`SeriesProgressionEngine`) for automatic season roll-over and episode airing checks.
   - Views for `/series/` with episode stepper actions (`+1 Episode`, `Sync TMDB schedule`).
3. **Core Provider Service (`services/tmdb.py`):**
   - Reusable client encapsulated in a shared module.
   - Reads `TMDB_API_KEY` and `TMDB_READ_ACCESS_TOKEN` from environment.
   - Uses `requests` with connection timeouts and Redis caching (`django-redis` or LocMem cache fallback).
   - Endpoints:
     - `search_movies(query, year=None)`
     - `get_movie_details(tmdb_id)`
     - `search_series(query, year=None)`
     - `get_series_details(tmdb_id)`
     - `get_season_details(tmdb_id, season_number)`

---

## 2. Step-by-Step Execution Plan

### Step 1: Specifications Authoring [COMPLETED]
- Completed `specs/movies_and_series/requirements.md`, `specs/movies_and_series/plan.md`, and `specs/movies_and_series/validation.md`.

### Step 2: Shared TMDB Client & Redis Caching [COMPLETED]
- Created `services/tmdb.py`:
  - Methods for searching and retrieving details for movies and TV series.
  - Multi-tier caching in Redis.

### Step 3: Movies App Implementation (`movies`) [COMPLETED]
- Created app `movies` and registered in `INSTALLED_APPS`.
- Defined `MovieEntry` with user reference, TMDB metadata, tracking status, watch date, rating, review.
- Migrated database schema.
- Created views and HTMX-driven routes in `movies/views.py`:
  - `/movies/` (list/dashboard).
  - `/movies/search/` (live query dropdown).
  - `/movies/add/` (save TMDB item or manual item).
  - `/movies/update/<id>/` (edit status/rating).
  - `/movies/rewatch/<id>/` (log rewatch).

### Step 4: Series App Implementation (`series`) [COMPLETED]
- Created app `series` and registered in `INSTALLED_APPS`.
- Defined models in `series/models.py`:
  - `SeriesEntry`, `SeasonEntry`, `EpisodeLog`.
- Migrated database schema.
- Implemented `SeriesProgressionEngine`:
  - Incrementing episodes and logging timestamps for the activity heatmap.
  - Auto-completing seasons when episode finale is reached.
  - Advancing automatically to next season if available.
  - Transitioning to `WAITING_FOR_NEXT_SEASON` if next season is in the future or pending broadcast.
  - Transitioning to `COMPLETED` when entire ended series is watched.
  - Calculating `has_new_episode_aired` and `upcoming_episode_days_away`.

### Step 5: Templates & UI Styling [COMPLETED]
- Created templates in compliance with `specs/styles.md`:
  - `movies/list.html`, `movies/partials/search_results.html`.
  - `series/list.html`, `series/partials/search_results.html`.
- Updated sidebar links to point directly to `{% url 'movie_list' %}` and `{% url 'series_list' %}`.

### Step 6: Automated Testing & Verification [COMPLETED]
- Unit tests for Movie models, TMDB addition, rewatches, and manual entries.
- Unit and integration tests for Series episode stepping, auto-rollover, upcoming season waiting state, and ended show completion.
- Full 31-test suite passing with 0 errors.

### Step 7: Specs Finalization & Git Push [COMPLETED]
- Marked all items in `specs/movies_and_series/` as completed.
- Committed and pushed to GitHub.
