# Quality Assurance & Test Gates: Video Games Tracking Engine

> **Feature Directory:** `specs/videogames_tracking/validation.md`  
> **Status:** Completed / Closed

---

## 1. Test Cases

### 1.1 Model Tests (`GameModelTests`)
- [x] `GameEntry` saves with only required fields (`user`, `title`, `status`).
- [x] `display_cover` returns `custom_cover.url` when custom cover is set.
- [x] `display_cover` falls back to `cover_url` when no custom cover is set.
- [x] `display_cover` returns `''` when both are absent.
- [x] `hours_display` returns correctly formatted string (e.g. `"12.5h"`).
- [x] `completion_display` returns correctly formatted string (e.g. `"75%"`).
- [x] Default `status` is `BACKLOG`.
- [x] Default `hours_played` is `0.0`, default `completion_percentage` is `0`.

### 1.2 Service Tests (`GameServiceTests`)
- [x] `VideoGameService.search()` returns a list of normalized dicts on a mocked successful RAWG response.
- [x] Each result dict contains keys: `external_id`, `title`, `cover_url`, `release_year`, `platforms`, `genres`, `developers`.
- [x] `VideoGameService.search()` returns `[]` on HTTP error (mocked timeout / 500).
- [x] `VideoGameService.search()` returns `[]` when RAWG key is missing from env.
- [x] Results are cached: a second identical search hits cache, not the network.

### 1.3 View Tests (`GameViewTests`)
- [x] `GET /games/` returns HTTP 200 for authenticated user; redirects to login for anonymous.
- [x] `GET /games/` context contains `playing`, `backlog`, `completed`, `on_hold`, `dropped` lists.
- [x] `GET /games/search/?q=witcher` returns partial HTML (HTTP 200), no full page layout.
- [x] `POST /games/add/` with valid data creates a `GameEntry` and redirects to detail page.
- [x] `POST /games/add/` with missing `title` returns form error (HTTP 200 with errors).
- [x] `GET /games/<pk>/` returns HTTP 200 with correct game context.
- [x] `GET /games/<pk>/` returns HTTP 404 for a game owned by another user.
- [x] `POST /games/<pk>/update-details/` updates `hours_played`, `rating`, `review` and redirects.
- [x] `POST /games/<pk>/delete/` deletes the entry and redirects to `/games/`.
- [x] `POST /games/<pk>/delete/` returns 404 for entries belonging to another user.

---

## 1. Test Cases

### 1.1 Model Tests (`GameModelTests`)
- [ ] `GameEntry` saves with only required fields (`user`, `title`, `status`).
- [ ] `display_cover` returns `custom_cover.url` when custom cover is set.
- [ ] `display_cover` falls back to `cover_url` when no custom cover is set.
- [ ] `display_cover` returns `''` when both are absent.
- [ ] `hours_display` returns correctly formatted string (e.g. `"12.5h"`).
- [ ] `completion_display` returns correctly formatted string (e.g. `"75%"`).
- [ ] Default `status` is `BACKLOG`.
- [ ] Default `hours_played` is `0.0`, default `completion_percentage` is `0`.

### 1.2 Service Tests (`GameServiceTests`)
- [ ] `VideoGameService.search()` returns a list of normalized dicts on a mocked successful RAWG response.
- [ ] Each result dict contains keys: `external_id`, `title`, `cover_url`, `release_year`, `platforms`, `genres`, `developers`.
- [ ] `VideoGameService.search()` returns `[]` on HTTP error (mocked timeout / 500).
- [ ] `VideoGameService.search()` returns `[]` when RAWG key is missing from env.
- [ ] Results are cached: a second identical search hits cache, not the network.

### 1.3 View Tests (`GameViewTests`)
- [ ] `GET /games/` returns HTTP 200 for authenticated user; redirects to login for anonymous.
- [ ] `GET /games/` context contains `playing`, `backlog`, `completed`, `on_hold`, `dropped` lists.
- [ ] `GET /games/search/?q=witcher` returns partial HTML (HTTP 200), no full page layout.
- [ ] `POST /games/add/` with valid data creates a `GameEntry` and redirects to detail page.
- [ ] `POST /games/add/` with missing `title` returns form error (HTTP 200 with errors).
- [ ] `GET /games/<pk>/` returns HTTP 200 with correct game context.
- [ ] `GET /games/<pk>/` returns HTTP 404 for a game owned by another user.
- [ ] `POST /games/<pk>/update-details/` updates `hours_played`, `rating`, `review` and redirects.
- [ ] `POST /games/<pk>/delete/` deletes the entry and redirects to `/games/`.
- [ ] `POST /games/<pk>/delete/` returns 404 for entries belonging to another user.

---

## 2. Verification Commands

```bash
# Run app-specific tests only
python manage.py test games

# Run full project test suite for regression check
python manage.py test

# Check migrations are clean
python manage.py makemigrations --check

# Verify no import errors in new module
python -c "from services.videogame_service import VideoGameService; print('OK')"
python -c "from games.models import GameEntry, GameStatus; print('OK')"
```

---

## 3. Assertions Checklist (to be checked off during implementation)

- [ ] `game_list` view renders 3 status shelves (Playing, Backlog, Completed) correctly.
- [ ] HTMX search partial is returned at `/games/search/` with result cards.
- [ ] "Already Tracked" badge appears for a game already in user's library (status ≠ DROPPED).
- [ ] Quick-add from search creates entry with correct status and redirects cleanly.
- [ ] Cover art loads from `cover_url` on list and detail views.
- [ ] Custom cover upload replaces provider cover (local or S3 storage).
- [ ] Platform badge visible on game cards and detail pages.
- [ ] Hours Played and Completion % editable from detail modal.
- [ ] Status color badges are correct per `styles.md` spec.
- [ ] Sidebar `Games` link is visible and active when on any `/games/` route.
- [ ] `python manage.py test games` → **all tests pass**.
- [ ] `python manage.py test` → **full suite passes with 0 regressions**.
