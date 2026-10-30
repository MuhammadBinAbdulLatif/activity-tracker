# Requirements: Date Picker UI & Untracked State for Dropped/Deleted Items

> **Feature Directory:** `specs/datepicker_and_tracking_status/requirements.md`  
> **Status:** Completed / Closed  

---

## 1. Context & Motivation

1. **Date Input Experience:**  
   Users currently face issues when clicking on date fields in web browsers (especially Chromium/Firefox/WebKit on dark themes) where the native `<input type="date">` may not automatically pop open the calendar dialog unless clicking a tiny calendar icon, or where styling prevents easy visual picking. Everywhere in the app where dates are requested (movies, series, books, manual forms, detail edit modals), users must be presented with an intuitive, native clickable date picker dialog with calendar icons and automatic picker triggering (`onclick="this.showPicker()"`).
   
2. **Search Tracked Status vs Dropped/Deleted:**  
   When searching for movies or series via TMDB (or books via Open Library), items that have been **deleted** or set to **DROPPED** status should **not** show up as `Tracked`. Instead, the user must be given the active actions (e.g. `+ Watchlist`, `Watched`, `Track & Watch`) so they can track or re-add them without false "Already Tracked" badges.

---

## 2. Functional Requirements

### 2.1 Date Input Picker Enhancement
- All `<input type="date">` fields across `movies`, `series`, and `books` templates must:
  - Have explicit calendar indicator support (e.g., `scheme: dark`, `cursor-pointer`, and `onclick="if(this.showPicker) this.showPicker()"` or equivalent global helper).
  - Include an icon or clickable trigger allowing one-click opening of the browser's date picker dialog without requiring manual typing.
  - Retain proper ISO format parsing (`YYYY-MM-DD`) on form submission.

### 2.2 Search Tracking Status Resolution
- In `movies/views.py:search_movies_view`:
  - `tracked_tmdb_ids` must only consider active/tracked movies. Specifically, exclude entries with `status=MovieStatus.DROPPED`.
  - Deleted entries (already completely removed from DB) will naturally not be present.
- In `series/views.py:search_series_view`:
  - `tracked_tmdb_ids` must exclude `user_status=SeriesUserStatus.DROPPED`.
- In `books/views.py:search_books_view`:
  - `tracked_keys` must exclude `status=BookStatus.DROPPED`.
- If a user previously dropped a movie/series/book, or deleted it, searching for that title will display the actionable buttons (`+ Watchlist`, `Watched`, `Track`) rather than a disabled/static `Tracked` badge.
- If re-adding a previously dropped item, `update_or_create` properly revives it with the new status selected by the user.

---

## 3. Definition of Done
1. All date inputs across all apps feature native calendar dialog invocation with clear dark styling.
2. TMDB movie search results exclude `DROPPED` movies from `is_tracked`.
3. TMDB series search results exclude `DROPPED` series from `is_tracked`.
4. OpenLibrary book search results exclude `DROPPED` books from `is_tracked`.
5. Automated tests verify search endpoints correctly mark `DROPPED` and deleted items as `is_tracked=False`.
6. Complete test suite passes with zero failures.
