# Technical Implementation Plan: Video Games Tracking Engine

> **Feature Directory:** `specs/videogames_tracking/plan.md`  
> **Status:** Completed / Closed

---

## 1. Architecture & Components Overview

### 1.1 Provider Client Service (`services/videogame_service.py`)
Class `VideoGameService`:
- Unified facade supporting two provider backends with automatic fallback:
  1. **Primary: RAWG Video Games Database API** (`https://api.rawg.io/api/games`)
     - No OAuth required — just a `key=` query param (RAWG_API_KEY from `.env`).
     - Captures: title (`name`), background image (`background_image`), release date, genres, platforms, developer(s), publisher(s), Metacritic score, ESRB rating, description.
     - Search: `GET /api/games?search={query}&key={key}&page_size=10`
     - Detail: `GET /api/games/{slug}?key={key}` for full metadata including description.
  2. **Fallback: IGDB API** (Twitch OAuth2 Bearer — `IGDB_CLIENT_ID` + `IGDB_CLIENT_SECRET`)
     - Endpoint: `https://api.igdb.com/v4/games` (POST with Apicalypse body).
     - Captures: name, cover art (`cover.url`), release dates, genres, platforms, involved companies (developer/publisher), summary/storyline.
     - Token Management: `POST https://id.twitch.tv/oauth2/token` → `client_credentials` grant → cache Bearer token with TTL.
- Search method: `search(query, limit=10) -> list[dict]`
- Detail method: `get_details(rawg_slug_or_igdb_id, source='rawg') -> dict`
- Normalize output to a canonical dict schema:
  ```python
  {
    "external_id": "rawg-{id}",   # or "igdb-{id}"
    "source": "rawg",             # or "igdb"
    "title": str,
    "cover_url": str,
    "description": str,
    "release_year": int | None,
    "developers": str,           # comma-joined list
    "publishers": str,
    "genres": str,               # comma-joined
    "platforms": str,            # comma-joined (PC, PS5, Xbox, Switch, etc.)
    "metacritic_score": int | None,
  }
  ```
- In-memory caching using a module-level dict keyed on `sha256(query)` with 300-second TTL.
- Graceful timeout (8 seconds), returns `[]` on provider failure — never raises to the view layer.

---

### 1.2 Data Model (`games/models.py`)

**`GameStatus` (TextChoices):**
- `PLAYING` ("Currently Playing")
- `COMPLETED` ("Completed")
- `ON_HOLD` ("On Hold")
- `DROPPED` ("Dropped")
- `BACKLOG` ("Backlog / Plan to Play")

**`GameEntry` Model:**
- `user`: ForeignKey(User, on_delete=CASCADE, related_name='game_entries')
- `external_id`: CharField(max_length=100, blank=True) — e.g. `rawg-3498`, `igdb-1942`
- `title`: CharField(max_length=255)
- `cover_url`: CharField(max_length=1000, blank=True)
- `custom_cover`: ImageField(upload_to='games/covers/', null=True, blank=True)
- `description`: TextField(blank=True)
- `release_year`: PositiveSmallIntegerField(null=True, blank=True)
- `developers`: CharField(max_length=500, blank=True)
- `publishers`: CharField(max_length=500, blank=True)
- `genres`: CharField(max_length=500, blank=True)
- `platforms_available`: CharField(max_length=500, blank=True) — all platforms the game ships on
- `platform_played`: CharField(max_length=100, blank=True) — which one *this user* played on
- `status`: CharField(max_length=20, choices=GameStatus.choices, default=GameStatus.BACKLOG)
- `hours_played`: DecimalField(max_digits=6, decimal_places=1, default=0.0)
- `completion_percentage`: PositiveSmallIntegerField(default=0) — 0–100
- `rating`: DecimalField(max_digits=3, decimal_places=1, null=True, blank=True) — 1.0–10.0
- `review`: TextField(blank=True)
- `notes`: TextField(blank=True)
- `start_date`: DateField(null=True, blank=True)
- `finish_date`: DateField(null=True, blank=True)
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)

**Computed Properties:**
- `display_cover`: Returns `custom_cover.url` if set, otherwise `cover_url`, otherwise `''`.
- `hours_display`: Returns `"{hours}h"` formatted string.
- `completion_display`: Returns `"{completion_percentage}%"`.
- `status_badge_class`: Returns CSS class string based on status (e.g. emerald for Playing, zinc for Backlog).

---

### 1.3 Routing & Endpoints (`games/urls.py` & `games/views.py`)

| URL Pattern | View Name | Description |
|---|---|---|
| `GET /games/` | `game_list` | Main dashboard grouped by status |
| `GET /games/search/` | `search_games` | HTMX live search against RAWG/IGDB |
| `POST /games/add/` | `add_game` | Save from search result or manual form |
| `GET /games/<int:pk>/` | `game_detail` | Detail page with stats and editable modal |
| `POST /games/<int:pk>/update-details/` | `update_game_details` | Update all tracked fields via modal form |
| `POST /games/<int:pk>/delete/` | `delete_game` | Delete entry and redirect to list |

All views require `@login_required`.

---

### 1.4 Frontend Templates & Components

**`games/templates/games/list.html`:**
- Top section: Stats bar (total games played, hours logged, currently playing count, completed count).
- **Currently Playing** shelf — game card grid (cover + title + hours played + completion % bar + platform badge).
- **Backlog** shelf — compact card list.
- **Completed** shelf — cover grid with star rating badge.
- **On Hold / Dropped** collapsed shelf.
- Search trigger button → opens search modal (like comics/books pattern).
- Manual add button inside modal.

**`games/templates/games/detail.html`:**
- Full-width banner: game cover (blurred, background) + focused cover art card + title + platform badge + developer/publisher credits.
- Stats row: Hours Played, Completion %, Status badge, Release Year.
- Ratings row: Overall rating (1–10) + optional Metacritic reference.
- Review & Notes textarea display.
- Start / Finish date display with edit button.
- Edit modal triggered by floating edit button — full field form inline.
- Delete button (with confirmation prompt).

**`games/templates/games/partials/search_results.html`:**
- Rendered via HTMX `hx-target`, returns card rows.
- Each row: small cover thumb, title, release year, platform pills, genres, developer.
- Buttons: **"Add to Playing"** / **"Add to Backlog"** — each a POST to `/games/add/`.
- **"Already Tracked"** indicator (emerald badge) if the title exists for this user (non-DROPPED).

---

### 1.5 System Integration
- Create `games` Django app: `python manage.py startapp games`.
- Register in `utrack/settings.py` `INSTALLED_APPS`.
- Include `games.urls` in `utrack/urls.py` under prefix `games/`.
- Add `RAWG_API_KEY` and `IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET` to `.env` (already present from Phase 2 tool gathering).
- Update sidebar navigation in `dashboard/templates/dashboard/sidebar.html` — add Games link pointing to `{% url 'game_list' %}`.
- Update `dashboard/demo_data.py` or live ORM-query helpers to include game entries in the heatmap and in-progress feed.

---

### 1.6 Tests (`games/tests.py`)
- `GameModelTests`: Field defaults, `display_cover`, `hours_display`, `completion_display` computed properties.
- `GameServiceTests`: Search and detail method return correct schema; graceful empty list on HTTP error (mock `requests.get`).
- `GameViewTests`:
  - `game_list` renders correct template and status-grouped context.
  - `search_games` returns partial HTML and is HTMX-aware.
  - `add_game` creates a `GameEntry` and redirects.
  - `game_detail` shows correct game data.
  - `update_game_details` updates all fields and redirects.
  - `delete_game` removes entry and redirects.
- All new tests pass; full suite regression check confirms 0 failures.
