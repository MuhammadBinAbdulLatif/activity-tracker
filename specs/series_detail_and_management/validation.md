# Validation Plan: TV Series Detail Page & Episode/Status Management

> **Status:** Completed & Closed (45/45 Tests Passed)  
> **Date:** 2026-10-29  

## 1. Test Strategy & Quality Gates
Every capability introduced must have corresponding unit and integration test coverage. Tests will execute against a fresh test database with all fixtures and mocks isolated.

---

## 2. Test Checklist

### 2.1 View Rendering & Navigation Tests
- [x] `test_series_detail_view_rendering`: Verify `GET /series/<id>/` returns HTTP 200, contains title, genres, cast pills, current season/episode, and broadcast info.
- [x] `test_series_detail_view_isolation`: Verify User B cannot access User A's series detail page (returns 404).
- [x] `test_list_cards_link_to_detail`: Verify that cards on `/series/` contain the `href` pointing to `/series/<id>/`.

### 2.2 Status Management & Reversion Tests
- [x] `test_series_status_reversion_completed_to_watching`:
  - Mark series as `COMPLETED`.
  - POST to `/series/<id>/update-details/` with `status=WATCHING`.
  - Verify `user_status` is updated to `WATCHING`.
- [x] `test_series_status_reversion_completed_to_plan_to_watch`:
  - Verify reverting to `PLAN_TO_WATCH` sets status and resets or retains appropriate episode numbers.
- [x] `test_series_progress_update_via_details`:
  - Update `current_season_number` and `current_episode_number` via detail form, verify persistence.

### 2.3 Personal Chronicle & Custom Metadata Tests
- [x] `test_series_update_personal_log`:
  - Update rating (e.g. 9.5) and review text; verify saved on `SeriesEntry`.
- [x] `test_series_custom_metadata_update`:
  - For a custom series, update title, overview, and cast; verify persistence.
- [x] `test_series_delete`:
  - POST to `/series/<id>/delete/`; verify series and child seasons are deleted from database.

---

## 3. CLI Validation Commands
Run test suite:
```powershell
python manage.py test series
python manage.py test
```
**Gate Requirement:** 100% of tests must pass with 0 errors and 0 failures.
