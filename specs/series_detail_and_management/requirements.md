# Requirements: TV Series Detail Page & Episode/Status Management

> **Status:** Completed & Closed  
> **Date:** 2026-10-29  

## 1. Feature Overview
Provide a dedicated, comprehensive detail view for every TV series (`/series/<id>/`). Clicking on any series card or title from the list view navigates directly to this page. The page provides full metadata, cast and creator information, complete season and episode breakdown, granular episode progression, broadcast air alerts, status reversion capabilities, personal chronicles (rating and review), and custom series editing with S3 poster uploads.

---

## 2. Functional Requirements

### 2.1 Navigation & Card Affordance
- Every card on the series list page (`/series/`) across all statuses (*Currently Watching*, *Waiting for Next Season*, *Watchlist*, *Completed*, *Dropped*) must clearly link to `/series/<id>/`.
- The poster image, title, and card surface must be clickable without interfering with the quick "+1 Ep" advance button.

### 2.2 Cinematic Detail View (`/series/<id>/`)
- **Cinematic Backdrop Hero:** Display TMDB backdrop or custom backdrop with radial dark vignette, matching the shadcn/ui dark aesthetic (`#09090b`).
- **Hero Metadata:** Large poster, title, first air date / release year, show status (Returning, Ended, Canceled), genres, network/creators if available, total seasons, total episodes, and overview.
- **Cast & Stars:** Show cast pills dynamically parsed from TMDB credits or custom input.
- **Airing & Broadcast Schedule:** Show clear badges indicating:
  - If a new episode aired within the last 7 days ("New Episode Aired!").
  - Upcoming next episode air date and countdown in days.
  - Next episode title and code (e.g., S03E04).
  - Manual button to sync freshest broadcast schedule from TMDB.

### 2.3 Season & Episode Breakdown
- Display list of all seasons (`SeasonEntry`) for the series.
- Show season completion progress bar and episode tracker:
  - Season name and season number.
  - Number of episodes.
  - Status indicator (Completed / In Progress / Upcoming).
  - Ability to advance episodes individually from the detail page (+1 Ep).
  - Ability to mark an entire season as watched/completed or revert it.

### 2.4 Status Switcher & Complete Reversion
- User can transition or revert show status at any time between:
  - **Currently Watching** (`WATCHING`)
  - **Waiting for Next Season** (`WAITING_FOR_NEXT_SEASON`)
  - **Plan to Watch** (`PLAN_TO_WATCH`)
  - **Completed** (`COMPLETED`)
  - **On Hold** (`ON_HOLD`)
  - **Dropped** (`DROPPED`)
- If marked as "Completed" by mistake or user wants to rewatch/revert, clicking **Plan to Watch** or **Watching** resets status and restores appropriate state.

### 2.5 Personal Chronicle & Custom Management
- **Personal Review & Rating:** User can set a 1–10 rating and write personal journal notes.
- **Custom Series Editing:** For custom series (`is_custom=True`), allow editing title, first air date, overview, total seasons, total episodes, genres, cast, and uploading custom poster artwork directly to S3.
- **Delete Action:** Allow safe deletion of tracked series with confirmation modal.

---

## 3. Definition of Done
1. Dedicated route `/series/<id>/` implemented and rendering rich detail template.
2. Clicking any card/poster on `/series/` navigates to `/series/<id>/`.
3. Cast metadata parsed and displayed for TMDB shows and editable for custom shows.
4. Seasons and episodes clearly broken down with progress visualization and episode advancement.
5. Status switching and reversion fully operational across all statuses.
6. Custom series editing and S3 poster upload tested and working.
7. 100% of test suite passing with new comprehensive tests for series detail and reversion.
