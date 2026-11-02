# Requirements Specification: Board Games & Tabletop Tracking Engine

> **Feature Directory:** `specs/boardgames_tracking/requirements.md`  
> **Status:** Completed / Closed

---

## 1. Persona & Product Purpose

Board games require a uniquely social tracking model:
- **Session-based, not continuous:** Unlike movies (one watch) or books (ongoing pages), board games are tracked by play *sessions* — discrete events with participants and outcomes.
- **Ownership vs. Played:** A user's relationship to a game spans Owned, Want to Play, Wishlist, Played, and Traded Away.
- **BGG as Authority:** BoardGameGeek is the canonical reference for mechanics, categories, designers, player counts, and community ratings. No other database comes close.
- **Group Play:** Users want to remember who they played with and their average session length.

---

## 2. Functional Requirements

### 2.1 Provider Client (`services/boardgame_service.py`)
- Query BGG XML API2 for searches and detail fetches.
- `search(query, limit=10)`: returns normalized list of dicts (title + external_id at minimum).
- `get_details(bgg_id)`: fetches full metadata from the `thing` endpoint; handles HTTP 202 (queued) with single retry after 2s.
- Normalize XML response to Python dict schema (see plan.md §1.1).
- Caching: 600-second TTL on detail fetches keyed by BGG ID.
- Graceful failure: returns `[]` / `{}` on timeout or parse error.

### 2.2 Data Model (`boardgames/models.py`)
- `BoardGameEntry` with all fields in plan.md §1.2.
- Required at minimum: `user`, `title`, `status`.
- `play_count` increments via the log-play endpoint.
- `last_played` updated automatically on each log-play action.
- `Meta`: `ordering = ['-updated_at']`.

### 2.3 Views & User Experience
- **`/boardgames/`** — List grouped by status shelves; stats bar (total, sessions, played, owned).
- **`/boardgames/search/`** — HTMX live search; shows name + year from BGG; "Already Tracked" badge.
- **`/boardgames/add/`** — Quick-add (triggers detail fetch from BGG for full metadata) + manual form fallback.
- **`/boardgames/<pk>/`** — Full detail with BGG info, personal stats, play log section.
- **`/boardgames/<pk>/log-play/`** — POST: increments `play_count` by 1, updates `last_played` to today. Redirects to detail.
- **`/boardgames/<pk>/update-details/`** — Full modal form update.
- **`/boardgames/<pk>/delete/`** — Deletes and redirects to list.

### 2.4 UI/UX Standards
- Matches `specs/styles.md`: dark zinc palette, emerald / amber accents.
- Status badge color coding:
  - Played → `bg-emerald-500/20 text-emerald-400 border-emerald-500/40`
  - Owned → `bg-zinc-800 text-zinc-300 border-zinc-700`
  - Want to Play → `bg-blue-500/10 text-blue-400 border-blue-500/30`
  - Wishlist → `bg-purple-500/10 text-purple-400 border-purple-500/30`
  - Traded Away → `bg-zinc-900/60 text-zinc-600 border-zinc-800`
- Sidebar `Board Games` link uses a dice / tabletop icon.
- Log Play button: prominent, quick-action emerald button.

---

## 3. Definition of Done

1. `boardgames` Django app created, registered in `INSTALLED_APPS`, URLs mounted at `/boardgames/`.
2. `BoardGameService` in `services/boardgame_service.py` with BGG XML search + detail.
3. `BoardGameEntry` model with migrations generated and applied.
4. All seven URL routes operational and login-protected.
5. Templates: `list.html`, `detail.html`, `partials/search_results.html` styled to spec.
6. Sidebar updated with Board Games link.
7. `boardgames/tests.py` fully covers model, service, and all views.
8. `python manage.py test boardgames` — **100% pass rate**.
9. `python manage.py test` — **full suite passes with 0 regressions**.
10. Specs marked **Completed / Closed**, committed, and pushed.
