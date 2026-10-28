# Validation & Quality Assurance: Movies & Series Tracking

> **Feature Directory:** `specs/movies_and_series/validation.md`  
> **Status:** Draft / Active Specification  

---

## 1. Test Verification Strategy

The Movies and Series modules must be thoroughly validated with automated unit, integration, and state-machine tests across `movies/tests.py`, `series/tests.py`, and `services/tests.py`.

### 1.1 Test Matrix & Verification Checklist

| Test Target | Scenario / Condition | Expected Assertion |
| :--- | :--- | :--- |
| **TMDB Client** | Search movie & TV show with valid credentials | Returns formatted results dictionary; caches payload in Redis |
| **TMDB Caching** | Second identical query | Served directly from Redis cache without outgoing HTTP request |
| **Movie Tracking** | Save movie from TMDB result | `MovieEntry` created with poster, runtime, genres, and user watch date |
| **Movie Rewatch** | User logs rewatch | `rewatch_count` increments, watch history preserved |
| **Movie Custom** | User logs indie/unlisted movie | `is_custom=True`, metadata saved cleanly |
| **Series Advance** | User clicks `+1 Episode` | `current_episode_number` increments, `EpisodeLog` created for today |
| **Season Completion** | User finishes final episode of Season 1 (when Season 2 exists) | Season 1 marked completed; series automatically rolls into Season 2 Episode 0/1; toast generated |
| **Upcoming Season** | User finishes latest season of an ongoing show | Series enters `WAITING_FOR_NEXT_SEASON`; displays upcoming air date badge |
| **Series Concluded** | User finishes final episode of final season of an *Ended* show | Series status transitions to `COMPLETED`; prompts overall rating |
| **Broadcast Alert** | TMDB reports episode aired in last 7 days | Badge rendered: `New Episode Available: S{S}E{E}` |
| **UI Routes** | Unauthenticated access to `/movies/` or `/series/` | Redirects (`302`) to `/accounts/login/` |
| **Sidebar Links** | Inspect sidebar navigation | Links navigate to `/movies/` and `/series/` |

---

## 2. Test Execution Commands

```bash
# Test TMDB client service
python manage.py test services

# Test Movies tracking app
python manage.py test movies

# Test Series tracking & auto-rollover engine
python manage.py test series

# Run entire suite across all apps
python manage.py test
```

---

## 3. Pass Criteria & Test Gates
- [ ] 0 syntax, import, or linting errors.
- [ ] All test cases across `movies`, `series`, and `services` pass with 100% success.
- [ ] All previous tests in `accounts` and `dashboard` continue to pass with 0 regressions.
- [ ] All specification files in `specs/movies_and_series/` updated to Completed & Closed upon delivery.
