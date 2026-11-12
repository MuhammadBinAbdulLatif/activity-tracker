# Validation & Test Gates: Cross-Media Recommendations Engine

> **Feature Directory:** `specs/cross_media_recommendations/`  
> **Status:** Completed / All Test Gates Passed  

---

## 1. Test Strategy Overview
Ensure all recommendation adapters, caching layers, and views function predictably with 100% test pass rate, handling network failures and rate limits gracefully.

---

## 2. Unit & Integration Test Checklist

### 2.1 Service Tests (`tests/test_recommendations_service.py`)
- [ ] **TMDB Service:**
  - `test_get_movie_recommendations_success`: Returns structured list with posters, titles, years.
  - `test_get_movie_recommendations_fallback_similar`: Falls back to similar endpoint when recommendations list is empty.
  - `test_get_movie_recommendations_cached`: Subsequent calls hit cache and avoid external HTTP requests.
  - `test_get_series_recommendations_success`: TV series recommendations parsed correctly.
- [ ] **Video Game Service:**
  - `test_get_game_recommendations_rawg`: Suggested games extracted with cover images and platforms.
  - `test_get_game_recommendations_empty_fallback`: Graceful empty list when no suggested items found.
- [ ] **Recommendation Engine (Orchestrator):**
  - `test_library_deduplication`: User's already tracked items are excluded from recommendations list.
  - `test_service_network_timeout_resilience`: Returns empty list and logs warning on HTTP connection errors without breaking page.

### 2.2 View & Endpoint Tests
- [ ] **Authentication Gate:** Anonymous requests redirect to login.
- [ ] **Async HTMX Endpoint:** Returns 200 OK with rendered recommendation card partial HTML.
- [ ] **Quick-Add Flow:** Clicking "+ Add" from a recommendation successfully creates a watchlist/backlog entry for the authenticated user.

---

## 3. Test Execution Command
```bash
python manage.py test services.tests.test_recommendation_engine movies.tests.test_recommendations games.tests.test_recommendations --verbosity=2
```

## 4. Definition of Done Test Gate
- Zero failing tests (`python manage.py test` passes completely).
- Zero console errors during async HTMX partial fetches.
- Cached results confirmed in Redis / Django cache.
