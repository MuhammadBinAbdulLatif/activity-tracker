# Requirements Specification: Video Games Tracking Engine

> **Feature Directory:** `specs/videogames_tracking/requirements.md`  
> **Status:** Completed / Closed

---

## 1. Persona & Product Purpose

Gaming is one of the most time-intensive media forms, yet remains the most poorly tracked by general-purpose life-log tools. Users need:
- **Session Tracking:** Hours played and completion percentage — the "how deep did I go?" metric.
- **Platform Awareness:** The same title on PS5 vs PC is a different experience; the specific platform played must be captured.
- **Backlog Management:** A curated "Plan to Play" queue is central to managing the ever-growing backlog.
- **API-Enriched Entries:** Searching by title should auto-fill box art, genre, developer, release year, and platform list — no typing required.
- **Manual Fallback:** Indie titles, retro games, or platform-exclusive niche releases must be manually loggable.

---

## 2. Functional Requirements

### 2.1 Provider Client (`services/videogame_service.py`)
- **Primary Provider: RAWG Video Games Database API**
  - `search(query, limit=10)` returns up to 10 results.
  - Each result normalized to the canonical dict schema (see plan.md §1.1).
  - Uses `RAWG_API_KEY` from environment (gracefully disables if missing).
- **Fallback Provider: IGDB API (Twitch OAuth2)**
  - Activated when RAWG is unavailable or returns no results.
  - OAuth2 Bearer token obtained from Twitch via `client_credentials` and cached.
  - Uses `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET` from environment.
- **Caching:** In-memory cache keyed on search query hash, 300-second TTL.
- **Error Resilience:** Any network failure, timeout, or API error returns `[]` — never raises to the view.

### 2.2 Data Model (`games/models.py`)
- `GameEntry` model with all fields described in plan.md §1.2.
- Fields required (non-blank) at minimum: `user`, `title`, `status`.
- `platform_played` is optional at creation but encouraged at status = PLAYING or COMPLETED.
- `completion_percentage` clamped 0–100; `hours_played` clamped ≥ 0.
- `rating` is optional and free-form (1.0–10.0, one decimal).
- Proper `Meta`: `ordering = ['-updated_at']`, `verbose_name = "Game Entry"`.

### 2.3 Views & User Experience (`games/views.py`)
- **`/games/` — List View:**
  - All entries for the authenticated user, segmented into status shelves.
  - Stats bar (total tracked, hours logged, currently playing, completed).
  - Search modal trigger button; HTMX search against provider.
  - Manual add modal fallback.
- **`/games/search/` — Live Search (HTMX):**
  - Returns `search_results.html` partial.
  - Shows "Already Tracked" badge if title exists for user and status ≠ DROPPED.
  - Inline quick-add buttons: "Add as Playing" and "Add to Backlog".
- **`/games/add/` — Add Entry (POST):**
  - Accepts both search-enriched payload (pre-filled metadata) and manual form.
  - Defaults `status` to `BACKLOG` if not provided.
  - Redirects to `game_detail` on success.
- **`/games/<pk>/` — Detail View:**
  - Full game presentation: cover art, stats, review, notes.
  - Editable via inline modal (no separate edit page).
- **`/games/<pk>/update-details/` — Update (POST):**
  - Accepts all editable fields; validates and saves; redirects to detail page.
- **`/games/<pk>/delete/` — Delete (POST):**
  - Deletes entry; redirects to `/games/`.

### 2.4 Template & UI Standards
- Follows `specs/styles.md` exactly: dark zinc palette, emerald accents, hairline borders.
- Cover display: blurred background + sharp foreground card (mirrors movies & books pattern).
- Status badge color coding:
  - Playing → `bg-emerald-500/20 text-emerald-400 border-emerald-500/40`
  - Completed → `bg-zinc-800 text-zinc-300 border-zinc-700`
  - Backlog → `bg-blue-500/10 text-blue-400 border-blue-500/30`
  - On Hold → `bg-yellow-500/10 text-yellow-400 border-yellow-500/30`
  - Dropped → `bg-red-950/40 text-red-400 border-red-800/40`
- Sidebar navigation item added for **Games** with a gamepad/controller icon.
- All interactive forms use HTMX where applicable; loading spinners on search.

### 2.5 Sidebar & Dashboard Integration
- Sidebar `Games` link is active and navigates to `/games/`.
- Dashboard currently-in-progress feed includes PLAYING games when ORM bindings exist.

---

## 3. Definition of Done

1. `games` Django app created, registered in `INSTALLED_APPS`, URLs mounted at `/games/`.
2. `VideoGameService` in `services/videogame_service.py` with working RAWG search (IGDB fallback included but tested with mocks since API keys may not be set in CI).
3. `GameEntry` model with migrations generated and applied (`0001_initial.py`).
4. All six URL routes operational and login-protected.
5. Templates: `list.html`, `detail.html`, `partials/search_results.html` created and styled to spec.
6. Sidebar navigation updated to include Games link.
7. `games/tests.py` fully covers model, service, and all views.
8. `python manage.py test games` — **100% pass rate**.
9. `python manage.py test` — **full suite passes with 0 regressions**.
10. All three spec files updated to **Completed / Closed** status, committed, and pushed.
