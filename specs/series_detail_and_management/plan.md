# Implementation Plan: TV Series Detail Page & Episode/Status Management

> **Status:** Completed & Closed  
> **Date:** 2026-10-29  

## 1. Technical Strategy & Architecture

### 1.1 Model Enhancements (`series/models.py`)
- Add `cast` (`models.TextField(blank=True)`) to `SeriesEntry` to store top cast members (e.g. comma-separated names).
- Add `tagline` or `network` (`models.CharField(max_length=255, blank=True)`).
- Add property `cast_list` to return `[c.strip() for c in self.cast.split(",") if c.strip()]`.
- Add property `backdrop_url` with fallback to standard backdrop or placeholder.
- Add helper method/property on `SeriesEntry` to compute overall series watch progress percentage based on current season/episode and total episodes.

### 1.2 TMDB Service Integration (`services/tmdb.py` & `series/engine.py`)
- When fetching details for a TV series (`tmdb_service.get_series_details`), ensure `append_to_response=credits` is included (or add helper method `get_series_credits`).
- Update `SeriesProgressionEngine.sync_tmdb_metadata` and `add_series_view` to extract cast and crew/creators.

### 1.3 View Layer (`series/views.py` & `series/urls.py`)
- `series_detail_view(request, series_id)`:
  - Validates `user=request.user`.
  - Backfills cast and backdrop if missing for TMDB shows.
  - Queries seasons ordered by `season_number`.
  - Calculates season-level progress and airing status.
- `update_series_details_view(request, series_id)`:
  - Handles status transitions and reversion (e.g., from `COMPLETED` back to `WATCHING` or `PLAN_TO_WATCH`).
  - Handles rating, personal review, current season, and current episode adjustments.
  - If `is_custom=True`, processes title, overview, genres, cast, total seasons/episodes, and custom poster upload to S3.
- `delete_series_view(request, series_id)`:
  - Deletes the `SeriesEntry` (cascading to seasons and episode logs) and redirects to `series_list`.
- Wire routes in `series/urls.py`:
  - `path('<int:series_id>/', series_detail_view, name='series_detail')`
  - `path('<int:series_id>/update-details/', update_series_details_view, name='series_update_details')`
  - `path('<int:series_id>/delete/', delete_series_view, name='series_delete')`

### 1.4 Template Layer (`series/templates/series/detail.html` & `list.html`)
- `detail.html`:
  - Cinematic hero backdrop with dark radial vignette and responsive layout.
  - Show header: poster, title, air date/status, total seasons/episodes, genres, overview.
  - Broadcast status badges: New episode aired indicator, days to next episode, upcoming episode name and date.
  - Cast pills list.
  - Status switcher (Watching, Waiting for Next Season, Plan to Watch, Completed, On Hold, Dropped).
  - Season & Episode Tracker: Accordion or list of seasons showing progress, episode count, air date, and interactive "+1 Ep" buttons.
  - Personal Chronicle & Review panel (1–10 rating, review notes, season/episode adjusters).
  - Custom Show editing modal/section (if `is_custom`).
  - Danger zone (Delete series).
- `list.html`:
  - Wrap poster, show title, and card body in links pointing to `{% url 'series_detail' s.id %}`.
  - Maintain quick action buttons (+1 Ep) without event bubbling conflicts.

---

## 2. Step-by-Step Execution Sequence
1. Check `services/tmdb.py` to ensure TV show credits retrieval is available.
2. Update `series/models.py` with `cast`, `backdrop_url`, and `cast_list`.
3. Create and apply migrations (`python manage.py makemigrations series && python manage.py migrate`).
4. Update `series/engine.py` to extract cast on sync.
5. Implement views in `series/views.py` and routes in `series/urls.py`.
6. Create `series/templates/series/detail.html`.
7. Update `series/templates/series/list.html` cards with detail page links.
8. Author test suite in `series/tests.py` covering all new functionality.
9. Execute validation suite, verify 100% pass, and update documentation before git commit & push.
