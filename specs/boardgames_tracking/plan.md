# Technical Implementation Plan: Board Games & Tabletop Tracking Engine

> **Feature Directory:** `specs/boardgames_tracking/plan.md`  
> **Status:** Completed / Closed

---

## 1. Architecture & Components Overview

### 1.1 Provider Client Service (`services/boardgame_service.py`)
Class `BoardGameService`:
- **Single Provider: BoardGameGeek XML API2** (no auth key required — free public API)
  - Search: `GET https://boardgamegeek.com/xmlapi2/search?query={q}&type=boardgame`
    - Returns a list of items with `id` and `name` only.
  - Detail: `GET https://boardgamegeek.com/xmlapi2/thing?id={id}&stats=1`
    - Returns full metadata: name, description, year published, min/max players, playing time, designers, publishers, BGG average rating, BGG rank, image URL, thumbnail URL, categories, mechanics.
  - Rate limit: requests must be spaced; BGG may return HTTP 202 (queued) — retry with backoff.
- Search method: `search(query, limit=10) -> list[dict]` — returns normalized dicts.
- Detail method: `get_details(bgg_id: str) -> dict`
- Normalized output schema:
  ```python
  {
    "external_id": "bgg-{id}",
    "title": str,
    "cover_url": str,          # image URL from BGG
    "description": str,
    "year_published": int | None,
    "min_players": int | None,
    "max_players": int | None,
    "min_playtime": int | None,  # minutes
    "max_playtime": int | None,
    "designers": str,            # comma-joined
    "publishers": str,
    "categories": str,           # comma-joined
    "mechanics": str,            # comma-joined
    "bgg_rating": float | None,  # community average
    "bgg_rank": int | None,
  }
  ```
- BGG search only returns IDs; detail calls are needed to get full metadata per result.
  - To keep UX fast: search returns ID + name (fast), then each "Add" triggers a detail fetch.
- Caching: module-level dict with 600-second TTL (BGG data changes slowly).
- Error resilience: HTTP 202 triggers a single retry after 2s; other errors return `{}` / `[]`.

---

### 1.2 Data Model (`boardgames/models.py`)

**`BoardGameStatus` (TextChoices):**
- `PLAYED` ("Played")
- `OWNED` ("Owned / On Shelf")
- `WANT_TO_PLAY` ("Want to Play")
- `WISHLIST` ("Wishlist")
- `TRADED_AWAY` ("Traded Away")

**`BoardGameEntry` Model:**
- `user`: ForeignKey(User, CASCADE, related_name='boardgame_entries')
- `external_id`: CharField(max_length=100, blank=True) — e.g. `bgg-174430`
- `title`: CharField(max_length=255)
- `cover_url`: CharField(max_length=1000, blank=True)
- `custom_cover`: ImageField(upload_to='boardgames/covers/', null=True, blank=True)
- `description`: TextField(blank=True)
- `year_published`: PositiveSmallIntegerField(null=True, blank=True)
- `designers`: CharField(max_length=500, blank=True)
- `publishers`: CharField(max_length=500, blank=True)
- `categories`: CharField(max_length=500, blank=True)
- `mechanics`: CharField(max_length=500, blank=True)
- `min_players`: PositiveSmallIntegerField(null=True, blank=True)
- `max_players`: PositiveSmallIntegerField(null=True, blank=True)
- `min_playtime`: PositiveSmallIntegerField(null=True, blank=True) — minutes
- `max_playtime`: PositiveSmallIntegerField(null=True, blank=True)
- `bgg_rating`: DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
- `bgg_rank`: PositiveIntegerField(null=True, blank=True)
- `status`: CharField(max_length=20, choices=BoardGameStatus.choices, default=BoardGameStatus.WANT_TO_PLAY)
- `play_count`: PositiveIntegerField(default=0)
- `last_played`: DateField(null=True, blank=True)
- `avg_session_minutes`: PositiveIntegerField(null=True, blank=True)
- `favorite_players`: CharField(max_length=255, blank=True) — e.g. "2, 4"
- `rating`: DecimalField(max_digits=3, decimal_places=1, null=True, blank=True) — 1.0–10.0
- `review`: TextField(blank=True)
- `notes`: TextField(blank=True)
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)

**Computed Properties:**
- `display_cover`: custom_cover URL → cover_url → `''`
- `player_count_display`: `"{min}–{max} players"` or `"{min} player"` if equal
- `playtime_display`: `"{min}–{max} min"` or just `"{min} min"` if equal
- `status_badge_class`: CSS classes per status
- `total_hours_played`: `play_count × avg_session_minutes / 60` formatted string

---

### 1.3 Routing & Endpoints (`boardgames/urls.py` & `boardgames/views.py`)

| URL Pattern | View Name | Description |
|---|---|---|
| `GET /boardgames/` | `boardgame_list` | Main dashboard grouped by status |
| `GET /boardgames/search/` | `search_boardgames` | HTMX live search against BGG |
| `POST /boardgames/add/` | `add_boardgame` | Save from search or manual form |
| `GET /boardgames/<int:pk>/` | `boardgame_detail` | Full detail page |
| `POST /boardgames/<int:pk>/log-play/` | `log_play` | Quick-increment play count |
| `POST /boardgames/<int:pk>/update-details/` | `update_boardgame_details` | Full modal update |
| `POST /boardgames/<int:pk>/delete/` | `delete_boardgame` | Delete and redirect |

All views `@login_required`.

---

### 1.4 Frontend Templates & Components

**`boardgames/templates/boardgames/list.html`:**
- Header with icon + subtitle.
- Stats bar: total tracked, total play sessions, unique games played, games owned.
- **"Recently Played"** shelf — top 6 by `last_played` desc, play count badge on cover.
- **"Owned / On Shelf"** shelf — compact card grid.
- **"Want to Play"** list — minimal card rows.
- **"Wishlist"** collapsed section.
- Search modal trigger button.

**`boardgames/templates/boardgames/detail.html`:**
- Banner: blurred bg + sharp cover card + title + year + status badge.
- BGG metadata row: designers, publishers, player count range, playtime range, categories, mechanics.
- BGG rating badge + your personal rating.
- Play log section: total sessions, last played date, quick +1 Play button.
- Review & Notes display.
- Edit modal.

**`boardgames/templates/boardgames/partials/search_results.html`:**
- Rows: cover thumb, title, year, player count, playtime, BGG rating.
- "Already Tracked" badge.
- Quick-add buttons: "+ Owned" and "+ Want to Play".

---

### 1.5 System Integration
- `python manage.py startapp boardgames`
- Register in `INSTALLED_APPS`.
- Mount at `/boardgames/` in `utrack/urls.py`.
- Update sidebar: `boardgame_list` URL with a dice/tabletop icon.
