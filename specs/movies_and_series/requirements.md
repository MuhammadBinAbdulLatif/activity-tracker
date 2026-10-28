# Requirements: Movies & Series Tracking Engine

> **Feature Directory:** `specs/movies_and_series/requirements.md`  
> **Status:** Completed & Closed  

---

## 1. Overview & Objectives

Deliver the tracking subsystem for **Movies** and **Series (TV Shows)** as two distinct, first-class media categories within uTrack.

While both share TMDB (The Movie Database) as their primary open catalog provider, their consumption patterns, lifecycle states, and data models are structurally different:
- **Movies:** Discrete units with runtime (minutes), watch dates, rewatch counts, and single completion triggers.
- **Series (TV Shows):** Episodic, season-based multi-tier units that span weeks, months, or years. 

### Core New Paradigm:
1. **Separation of Categories:** Movies and Series are kept separate in dashboards, filters, models, and routes.
2. **Automatic Next-Season Roll-Over:** When a user completes the finale episode of Season $N$, the system automatically prompts or rolls them into Season $N+1$ (if released or announced).
3. **Episode Release & Schedule Awareness:** The system monitors TMDB broadcast metadata (`air_date`, `next_episode_to_air`, `last_air_date`, show status: *Returning Series*, *Ended*, *Canceled*) to notify the user:
   - When a new episode has aired and is ready to watch.
   - When an upcoming season has a confirmed release date.
   - When a show has concluded or been canceled.

---

## 2. Functional Requirements

### 2.1 Provider Client: TMDB Adapter & Caching
1. **Client Engine:** Robust TMDB API v3 / Bearer Token client with timeouts, retry handling, and Redis caching.
2. **Distinct Search Endpoints:**
   - `search_movies(query, page, year)` $\rightarrow$ calls TMDB `/search/movie`.
   - `search_series(query, page, first_air_date_year)` $\rightarrow$ calls TMDB `/search/tv`.
3. **Detail Enrichment:**
   - Movie details: `/movie/{id}` with credits, genres, runtime, release date, poster, backdrop.
   - Series details: `/tv/{id}` with season list, episode count, in-production status, `next_episode_to_air`, `last_episode_to_air`.
   - Season details: `/tv/{id}/season/{season_number}` with individual episode names, overviews, air dates, and still images.
4. **Caching Strategy:**
   - Search results cached in Redis for 6 hours.
   - Detailed series/season structures cached for 24 hours.

### 2.2 Data Models & Schema Structure

#### A. Movies (`MovieEntry`)
- `user`: ForeignKey to User.
- `tmdb_id`: Integer (null if custom entry).
- `title`: CharField.
- `original_title`: CharField (optional).
- `release_date`: DateField.
- `runtime`: PositiveIntegerField (minutes).
- `poster_path` / `backdrop_path`: CharField / URLField.
- `overview`: TextField.
- `genres`: JSONField or ManyToMany.
- `director`: CharField.
- **User Tracking State:**
  - `status`: Enum (`PLAN_TO_WATCH`, `WATCHING`, `COMPLETED`, `DROPPED`).
  - `watch_date`: DateField (date completed or watched).
  - `rating`: DecimalField / IntegerField (e.g., 1–10 or 1–5 stars).
  - `review`: TextField.
  - `rewatch_count`: PositiveIntegerField (default 0).
  - `is_custom`: Boolean (manual fallback if not on TMDB).

#### B. TV Series (`SeriesEntry`, `SeasonEntry`, `EpisodeLog`)
1. **`SeriesEntry` (Show-Level Record):**
   - `user`: ForeignKey to User.
   - `tmdb_id`: Integer.
   - `title`: CharField.
   - `first_air_date`: DateField.
   - `poster_path`, `backdrop_path`, `overview`, `genres`.
   - `show_status`: Enum (`RETURNING`, `ENDED`, `CANCELED`, `IN_PRODUCTION`).
   - `total_seasons`: IntegerField.
   - `total_episodes`: IntegerField.
   - `user_status`: Enum (`WATCHING`, `PLAN_TO_WATCH`, `COMPLETED`, `ON_HOLD`, `DROPPED`).
   - `current_season_number`: IntegerField (default 1).
   - `current_episode_number`: IntegerField (default 0).
   - `next_episode_air_date`: DateField (nullable, synced from TMDB).
   - `next_episode_name`: CharField (nullable).
   - `rating`: DecimalField (overall show rating).
   - `notes`: TextField.

2. **`SeasonEntry` (Season-Level State):**
   - `series`: ForeignKey to `SeriesEntry`.
   - `season_number`: IntegerField.
   - `name`: CharField (e.g., "Season 1").
   - `episode_count`: IntegerField.
   - `air_date`: DateField.
   - `is_completed`: BooleanField.
   - `completed_at`: DateTimeField (nullable).

3. **`EpisodeLog` (Granular Progress & Activity Heatmap Hook):**
   - `series`: ForeignKey to `SeriesEntry`.
   - `season_number`: IntegerField.
   - `episode_number`: IntegerField.
   - `watched_at`: DateTimeField (hooks into GitHub-style heatmap as a discrete activity!).

### 2.3 Intelligent Lifecycle Automations

#### 1. Automatic Next-Season Roll-Over
- When the user marks the final episode of Season $S$ as watched:
  - Season $S$ is marked `is_completed = True`.
  - The system checks if Season $S+1$ exists in the cached series metadata.
  - If Season $S+1$ exists and has aired episodes:
    - `current_season_number` advances to $S+1$, and `current_episode_number` resets to 0 (or 1 on first increment).
    - Status remains `WATCHING`.
    - User is presented with a celebratory toast: *"You completed Season S! Season S+1 is now active."*
  - If Season $S+1$ is announced but not yet aired:
    - Series status transitions to `WAITING_FOR_NEXT_SEASON`.
    - Next season's expected air date is pinned to the user's dashboard card.
  - If show is concluded (`show_status == 'ENDED'` and no more seasons):
    - Overall series transitions to `COMPLETED` with prompt for final review & rating.

#### 2. Broadcast & Release Notifications Engine
- **"New Episode Aired" Indicator:** If `WATCHING` and TMDB reports that episode $E$ aired in the past 7 days, render a bright badge: `New Episode Available: S{S}E{E}`.
- **"Upcoming Season" Countdown:** For series on hold or completed up to the current broadcast, display: `Season {S+1} airs on {Air Date}`.

### 2.4 User Interface Requirements
1. **Dedicated View: Movies (`/movies/`)**
   - Tabs: *Currently Watching*, *Watchlist (Plan to Watch)*, *Watched (Chronicle)*.
   - Search & Add modal with instant TMDB autocomplete.
   - Manual movie creation fallback form.
2. **Dedicated View: Series (`/series/`)**
   - Active series cards with Season/Episode stepper (`+1 Episode`, `Complete Season`).
   - Airing status badges (`Airing Today`, `Next Ep in 3 days`, `Series Finale Completed`).
   - Season tabs & episode checklist dropdown.
3. **Integration with Home Dashboard (`/`):**
   - Home "Currently In-Progress" cards reflect separate Movie and Series categories.
   - Heatmap logs discrete watches for both movies and episode increments.

---

## 3. Definition of Done (Acceptance Criteria)
- [x] Dedicated feature directory `specs/movies_and_series/` has `requirements.md`, `plan.md`, and `validation.md`.
- [x] TMDB client service implemented with Redis caching for movie and TV endpoints.
- [x] Separate models created for Movies and Series/Seasons/Episodes.
- [x] Next-season auto-roll-over algorithm passes unit and integration tests.
- [x] Episode release status detection (`New Episode Available`, `Upcoming Season`) verified.
- [x] Views and templates for `/movies/` and `/series/` styled in compliance with `specs/styles.md`.
- [x] 100% of automated tests pass with zero regressions.
- [x] Specs marked Completed & code committed and pushed to git.
