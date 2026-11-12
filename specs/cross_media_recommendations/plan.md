# Implementation Plan: Cross-Media Recommendations Engine

> **Feature Directory:** `specs/cross_media_recommendations/`  
> **Status:** Completed / Verified  

---

## 1. Technical Architecture & File Layout

### 1.1 Backend Service Layer (`services/`)
1. **`services/tmdb.py` Updates:**
   - Add `get_movie_recommendations(tmdb_id, page=1)`
   - Add `get_series_recommendations(tmdb_id, page=1)`
   - Automatic fallback to `similar` if recommendations return fewer than 4 items.
2. **`services/videogame_service.py` Updates:**
   - Add `get_game_recommendations(rawg_id_or_slug)` calling RAWG's suggested/game-series endpoints or IGDB similar games.
3. **`services/comic_manga_service.py` Updates:**
   - Add `get_manga_recommendations(anilist_id)`
4. **`services/openlibrary.py` & `services/audiobook_service.py` Updates:**
   - Add `get_author_or_subject_recommendations(author_name, subject, exclude_title)`
5. **`services/recommendation_engine.py` (New Orchestrator):**
   - Universal interface normalizing response structures across all providers.
   - User filter: excludes items already in user's library (`user.movie_set`, `user.uservideogame_set`, etc.).
   - Multi-tier cache handling.

### 1.2 Routing & HTMX Endpoints
Create HTMX recommendation endpoints so the initial page render is instant, and recommendations load asynchronously via `hx-get`:
* `GET /<category>/<pk>/recommendations/` (e.g. `/movies/<pk>/recommendations/`, `/games/<pk>/recommendations/`)
* Returns an HTML partial: `includes/recommendation_cards.html`

### 1.3 UI Templates & Components
1. **`templates/includes/recommendations_carousel.html`:**
   - Dark slate cards (`#18181b`), border (`#27272a`), emerald hover accent (`#10b981`).
   - Image cover with poster aspect ratio.
   - Title, Year, Subtitle (Author/Developer/Director).
   - Direct "+ Add" action button triggering quick-add to the user's watchlist/backlog.
2. **Detail Page Integration:**
   - Update `movies/templates/movies/movie_detail.html`
   - Update `series/templates/series/series_detail.html`
   - Update `games/templates/games/game_detail.html`
   - Update `books/templates/books/book_detail.html`

---

## 2. Step-by-Step Implementation Sequence

```
Step 1: Expand Service Adapters
  ├── Extend TMDB service with recommendations endpoints
  ├── Extend RAWG/IGDB service with game suggestion endpoints
  └── Extend Books/Comics adapters with discovery fallbacks

Step 2: Build Centralized Recommendation Engine
  ├── Create services/recommendation_engine.py
  ├── Add user library exclusion filter (deduplication)
  └── Implement Redis/Cache layer with 24-hr TTL

Step 3: HTMX Endpoints & Views
  ├── Add recommendation views for movies, series, games
  ├── Render partial template with async skeleton placeholder

Step 4: UI Component & Frontend Polish
  ├── Horizontal carousel / flex rack with smooth scrolling
  ├── "Quick-Add" HTMX button with toast confirmation

Step 5: Automated Testing & Verification
  ├── Test service mocks, API fallbacks, and caching
  ├── Test view authorization and exclusion of already-tracked items
```
