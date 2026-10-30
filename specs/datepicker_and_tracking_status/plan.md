# Implementation Plan: Date Picker UX & Search Untracked for Dropped/Deleted Items

> **Feature Directory:** `specs/datepicker_and_tracking_status/plan.md`  
> **Status:** Completed / Closed  

---

## 1. Plan Overview

### 1.1 Exclude DROPPED from `is_tracked` in Search Views
1. **Movies (`movies/views.py`)**:
   - In `search_movies_view`, modify `tracked_tmdb_ids` queryset:
     ```python
     tracked_tmdb_ids = set(
         MovieEntry.objects.filter(user=request.user, tmdb_id__isnull=False)
         .exclude(status=MovieStatus.DROPPED)
         .values_list("tmdb_id", flat=True)
     )
     ```
2. **Series (`series/views.py`)**:
   - In `search_series_view`, modify `tracked_tmdb_ids` queryset:
     ```python
     tracked_tmdb_ids = set(
         SeriesEntry.objects.filter(user=request.user, tmdb_id__isnull=False)
         .exclude(user_status=SeriesUserStatus.DROPPED)
         .values_list("tmdb_id", flat=True)
     )
     ```
3. **Books (`books/views.py`)**:
   - In `search_books_view`, modify `tracked_keys` queryset:
     ```python
     tracked_keys = set(
         BookEntry.objects.filter(user=request.user, openlibrary_key__gt="")
         .exclude(status=BookStatus.DROPPED)
         .values_list("openlibrary_key", flat=True)
     )
     ```

### 1.2 Date Picker UX and Dialog Integration
1. **Global CSS styling for Date Inputs (`dashboard/templates/base_app.html`)**:
   - Configure WebKit / Blink date picker calendar icon color-scheme and calendar icon picker styling:
     ```css
     input[type="date"]::-webkit-calendar-picker-indicator {
         filter: invert(0.8);
         cursor: pointer;
     }
     input[type="date"] {
         color-scheme: dark;
     }
     ```
   - Global script to automatically open date picker dialog when clicking anywhere on a date input:
     ```javascript
     document.addEventListener('click', function(e) {
         if (e.target && e.target.type === 'date') {
             if (typeof e.target.showPicker === 'function') {
                 try {
                     e.target.showPicker();
                 } catch (err) {}
             }
         }
     });
     ```
2. **Template Updates for Date Inputs**:
   - `movies/templates/movies/list.html` (Custom creation: `release_date`, `watch_date`)
   - `movies/templates/movies/detail.html` (Edit modal: `watch_date`)
   - `series/templates/series/detail.html` (Custom metadata: `first_air_date`)
   - `books/templates/books/detail.html` (Reading dates: `start_date`, `finish_date`)
   - Add calendar icon / helper UI and `cursor-pointer` to guarantee clicking brings up the native calendar dialog on all platforms.

---

## 2. Testing Strategy
- Add unit tests in `movies/tests.py`, `series/tests.py`, and `books/tests.py`:
  - Search returns `is_tracked=False` for a deleted item.
  - Search returns `is_tracked=False` for an item with status `DROPPED`.
  - Search returns `is_tracked=True` for items with active statuses (`WATCHING`, `PLAN_TO_WATCH`, `COMPLETED`, etc.).
