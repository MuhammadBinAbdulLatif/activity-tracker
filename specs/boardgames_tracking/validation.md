# Quality Assurance & Test Gates: Board Games & Tabletop Tracking Engine

> **Feature Directory:** `specs/boardgames_tracking/validation.md`  
> **Status:** Completed / Closed

---

## 1. Test Cases

### 1.1 Model Tests (`BoardGameModelTests`)
- [x] `BoardGameEntry` saves with only required fields (`user`, `title`, `status`).
- [x] Default `status` is `WANT_TO_PLAY`, default `play_count` is `0`.
- [x] `display_cover` returns `custom_cover.url` when set, else `cover_url`, else `''`.
- [x] `player_count_display` returns `"2–4 players"` for min=2, max=4.
- [x] `player_count_display` returns `"2 players"` when min == max.
- [x] `playtime_display` returns `"30–90 min"` and `"60 min"` (equal).
- [x] `status_badge_class` returns correct CSS class for each status.
- [x] `__str__` includes title and username.

### 1.2 Service Tests (`BoardGameServiceTests`)
- [x] `search()` returns list of dicts with `external_id` and `title` on mocked BGG XML response.
- [x] `search()` returns `[]` on network error.
- [x] `search()` returns `[]` for empty query.
- [x] `get_details()` returns normalized dict with all metadata fields on mocked response.
- [x] `get_details()` retries once on HTTP 202 and returns result.
- [x] `get_details()` returns `{}` on parse error.
- [x] Detail results are cached: second call for same ID hits cache.

### 1.3 View Tests (`BoardGameViewTests`)
- [x] `GET /boardgames/` → 200 for authenticated user, redirect for anonymous.
- [x] List view context has `played`, `owned`, `want_to_play`, `wishlist`, `traded_away` keys.
- [x] `GET /boardgames/search/?q=catan` → 200, returns partial template.
- [x] `POST /boardgames/add/` with valid data creates entry and redirects to detail.
- [x] `POST /boardgames/add/` missing title returns form errors.
- [x] `GET /boardgames/<pk>/` → 200 with correct entry context.
- [x] `GET /boardgames/<pk>/` → 404 for another user's entry.
- [x] `POST /boardgames/<pk>/log-play/` increments play_count and updates last_played.
- [x] `POST /boardgames/<pk>/update-details/` saves all changed fields.
- [x] `POST /boardgames/<pk>/delete/` removes entry and redirects to list.
- [x] `POST /boardgames/<pk>/delete/` → 404 for another user's entry.

---

## 2. Verification Commands

```bash
python manage.py test boardgames
python manage.py test
python manage.py makemigrations --check
python -c "from services.boardgame_service import BoardGameService; print('OK')"
python -c "from boardgames.models import BoardGameEntry, BoardGameStatus; print('OK')"
```

---

## 3. Assertions Checklist

- [x] List view renders status shelves correctly.
- [x] HTMX search returns partial HTML at `/boardgames/search/`.
- [x] "Already Tracked" badge appears for existing entries.
- [x] Quick-add creates entry with BGG metadata auto-filled.
- [x] Log Play increments play count by 1 and sets `last_played` to today.
- [x] Detail page shows BGG rating, player count, playtime, mechanics.
- [x] Status color badges match `styles.md` spec.
- [x] Sidebar `Board Games` link navigates to `/boardgames/`.
- [x] `python manage.py test boardgames` → all pass.
- [x] `python manage.py test` → full suite, 0 regressions.
