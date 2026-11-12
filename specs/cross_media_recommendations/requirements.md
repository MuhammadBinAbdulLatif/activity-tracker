# Requirements Specification: Broader Cross-Media Recommendations Engine

> **Feature Directory:** `specs/cross_media_recommendations/`  
> **Target App/Modules:** `services/`, `movies/`, `series/`, `games/`, `books/`, `audiobooks/`, `comics/`, `boardgames/`, `dashboard/`  
> **Status:** Draft / Active Specification  

---

## 1. Objective & Vision
Provide personalized, contextual discovery and recommendations across all media categories in uTrack. When a user views or completes a movie, TV show, video game, book, comic, audiobook, or board game, or visits their chronicle dashboard, uTrack surfaces high-relevance recommendations derived either directly from authoritative APIs or via metadata/content heuristics and local user affinity.

---

## 2. Supported Categories & Provider Strategy

### 2.1 Movies & Serialized Television
* **Provider:** TMDB API (`TMDBService`)
* **Endpoints:**
  * Movie: `GET /movie/{id}/recommendations` with fallback to `GET /movie/{id}/similar`.
  * Series: `GET /tv/{id}/recommendations` with fallback to `GET /tv/{id}/similar`.
* **Output Payload:** Poster path, title, release year, rating, genre tags, TMDB ID.

### 2.2 Video Games
* **Provider:** RAWG API (`VideogameService`) & IGDB API fallback
* **Endpoints:**
  * RAWG: `GET /games/{id}/game-series` and `GET /games/{id}/suggested` or `suggested-to`.
  * IGDB: Query `similar_games` field from IGDB payload.
* **Output Payload:** Cover image URL, title, release year, platforms, rating, external ID.

### 2.3 Anime, Manga & Comics
* **Provider:** AniList GraphQL / Jikan API (`ComicMangaService`)
* **Endpoints:**
  * AniList: `Media(id: $id) { recommendations { nodes { mediaRecommendation { ... } } } }`
  * Jikan: `GET /manga/{id}/recommendations`
* **Fallback for Western Comics:** Comic Vine / metadata query matching publisher + creator/character.

### 2.4 Books & Audiobooks
* **Provider:** Open Library / Google Books API (`OpenLibraryService`, `AudiobookService`)
* **Strategy (Heuristic / Content-based):**
  * Same author / creator search: `author:"<author_name>"` sorted by popularity/rating.
  * Subject / genre intersection: Query `/subjects/<subject>.json` or search by common subject tags.

### 2.5 Board Games
* **Provider:** BoardGameGeek XML API2 (`BoardGameService`)
* **Strategy (Metadata Heuristic):**
  * Same primary game designer (`boardgamedesigner`) or top mechanics (`boardgamemechanic`).

---

## 3. Unified Cross-Media Recommendation Service Architecture
* Create a centralized orchestrator: `services/recommendation_engine.py` with standard interface:
  ```python
  def get_recommendations_for_item(category: str, external_id: str, title: str, metadata: dict = None, limit: int = 6) -> list[dict]
  ```
* Standardized Recommendation Result Schema:
  ```python
  {
      "title": str,
      "category": str,  # 'movie', 'series', 'game', 'book', 'audiobook', 'comic', 'boardgame'
      "external_id": str,
      "poster_url": str,
      "year": str | int,
      "subtitle": str,  # e.g., author, developer, or director
      "rating": float | None,
      "reason": str,    # e.g. "Because you enjoyed Inception" or "By Christopher Nolan"
      "add_action_url": str, # Quick-add / watchlist route
  }
  ```

---

## 4. UI / UX Requirements (Shadcn Dark Minimalist)
1. **Item Detail Pages (Movies, Series, Games, Books, etc.):**
   - A dedicated section at the bottom of the item detail view: *"Recommended Next"* or *"You Might Also Enjoy"*.
   - Horizontal sliding card rack or responsive grid with quick "Add to Watchlist / Backlog" buttons.
   - Smooth HTMX async loading with subtle skeleton shimmer so slow external API calls never block the main detail page.
2. **Dashboard Chronology Shelf:**
   - A lightweight card on the main dashboard showing 3-5 curated recommendations based on the user's latest 5-star ratings or active in-progress items.

---

## 5. Performance & Caching Requirements
1. **Cache Layer:** All recommendations MUST be cached via Django's cache (`redis` or fallback locmem) with a TTL of 24 to 72 hours (`rec:<category>:<id>`).
2. **Resilience / Fallback:** External API timeouts (limit: 5 seconds) must fail gracefully, returning empty lists without raising 500 errors to the user.
3. **No Duplicate Items:** Any item already in the user's active library or completed history must be filtered out or flagged as already owned/watched.

---

## 6. Definition of Done (Acceptance Criteria)
* [x] Centralized `RecommendationService` created with provider adapters for TMDB, RAWG/IGDB, AniList/Comic, and Books.
* [x] Seamless non-blocking recommendation rendering on item detail pages.
* [x] High-contrast, dark minimalist carousel/grid rendered matching shadcn guidelines.
* [x] Quick-action "+ Watchlist" functional on recommendation cards.
* [x] Personal library deduplication ensuring tracked/owned titles are filtered out.
* [x] 100% test coverage for recommendation adapters, cache keys, and error-handling fallbacks.
