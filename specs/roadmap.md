# Development Roadmap & Implementation Plan

> **Target Directory:** `specs/roadmap.md`  
> **Audience:** Development Agent & Engineering Team  
> **Status:** Active Execution Guide  

---

## Phase 1: Baseline Authentication & User Profiles [COMPLETED]
- **Status:** Complete & Verified
- **Deliverables Completed:**
  - Standard user registration, login, logout, and password management via `django.contrib.auth`.
  - Security-question account recovery flow with case-insensitive normalization.
  - Dedicated `accounts` app, `Profile` model, and fully tested session verification.
  - Modern shadcn-inspired 50/50 split layout, activity heatmap matrix logo, subtle cinematic texture, dynamic quote engine, inline loading feedback, and Sonner-style floating toasts.
  - 14/14 automated tests passing.

---

## Phase 2: Tool Gathering & Environment Configuration [COMPLETED]
- **Status:** Complete & Verified
- **Deliverables Completed:**
  - Comprehensive `.env` configuration file created at root with all required variables (PostgreSQL, Redis, Provider keys).
  - Provider catalog mapping out each media category to its primary open database and authentication requirements.
  - Verification that `.env` is safely ignored by `.gitignore`.
  - Specs finalized in `specs/tool_gathering/`.

---

## Phase 3: Dashboard & Home Page Experience (UI & Demo Prototype) [COMPLETED]
- **Status:** Complete & Verified
- **Deliverables Completed:**
  - Dedicated `dashboard` app integrated with routing at `/` with login protection.
  - Sleek, dark minimalist sidebar navigation with branding, core dashboard link, dedicated category links (Books, Audiobooks, Movies, Series & TV, Comics & Manga, Exercises & Habits), visual breaker, and user profile/settings/sign-out card.
  - GitHub-style 52-week life activity contribution heatmap with 5 calibrated emerald intensity tiers and daily tooltips.
  - Key performance metric bar (active streak, annual logged count, monthly engagement hours, daily average minutes).
  - Rich "Currently In-Progress" cards across multiple media types with progress meters and quick increment actions.
  - "Planned to Watch & Read" queue and "Recently Completed" retrospective highlights with star ratings and reviews.
  - Realistic modular demo data provider (`dashboard/demo_data.py`) prepared for clean future ORM model binding.
  - 5/5 automated dashboard tests passing (19/19 across entire test suite).
  - Specs finalized in `specs/homepage/`.

---

## Phase 4: Provider Client Infrastructure & Caching
- **Goal:** Build reusable client adapters for open databases with Redis caching to avoid rate-limits and optimize search speeds.
- **Target Providers:**
  - **Movies & Series:** TMDB (The Movie Database) API
  - **Books:** Open Library API / Google Books API
  - **Audiobooks:** Open Library / LibriVox / iTunes Search API / Audnexus
  - **Comics & Graphic Novels:** Comic Vine API / Grand Comics Database (GCD)
  - **Anime & Manga:** AniList GraphQL / Jikan (MyAnimeList open API)
- **Architecture:**
  - Common `ProviderBase` interface (`search(query)`, `get_details(external_id)`).
  - Multi-tier caching in Redis for search queries and metadata payloads.

---

## Phase 5: Media Tracking Engines & Data Models (Category by Category)

Transition the dashboard from demo data to persisted user logs with dual entry pathways:
1. **Automated Search & Enrichment (Primary):** User queries a title $\rightarrow$ metadata, poster, release date, creator/director/author auto-fetched $\rightarrow$ user inputs personal tracking details (date consumed, user rating, personal notes, status).
2. **Custom / Manual Fallback:** If an item is unlisted or niche, the user can manually create an entry with full custom details (title, release year, creator, description, custom cover/poster).

### Step 5.1: Movies & Series
- Search TMDB by title/year.
- Instant auto-fill: poster path, overview, genres, director/cast, runtime, release date/year.
- User inputs: watch date, user rating (e.g. 1–10 or 1–5 stars), review/notes, rewatch count, episodes/seasons watched (for series).
- Manual creation fallback for indie, unlisted, or home video items.

### Step 5.2: Books & Literature
- Search Open Library / Google Books by title, author, or ISBN.
- Auto-fill: book cover, author(s), publisher, publication year, page count, synopsis.
- User inputs: date completed/started, reading progress (pages/percentage), user rating, review, format (hardcover, paperback, ebook).
- Manual creation fallback.

### Step 5.3: Audiobooks
- Search Open Library / iTunes Search / Audnexus.
- Auto-fill: cover art, narrator, author, total duration/audio length.
- User inputs: listen date, listening speed/progress, personal rating, thoughts.
- Manual creation fallback.

### Step 5.4: Comics & Manga / Anime
- Search Comic Vine / AniList / Jikan.
- Auto-fill: issue/volume count, artist, writer, status, covers.
- User inputs: issues/chapters read, date consumed, rating, notes.
- Manual creation fallback.

---

## Phase 6: Universal Unified Search
- Unified search bar across all supported categories in the top navigation header.
- Real-time suggestions (instant search results grouped by category: Movies, Books, Anime, etc.).
- Direct "One-Click Track" action from search results.

---

## Phase 7: Retrospectives & Deep Timelines ("What I Did")
- **Monthly Summary ("What I Did This Month"):**
  - Aggregated view of everything watched, read, listened to, and completed in any chosen month.
  - Cumulative totals (hours watched, pages read, audio hours listened).
  - Top-rated items of the month and personal highlights.
- **Daily Log / Timeline:** Chronological feed of daily activities and consumption.
- **Yearly Wrapped / Retrospective:** Comprehensive yearly breakdown and trends.

---

## Phase 8: Life & Habit Activity Tracking (Extensibility)
- Workouts, exercise sessions, and custom daily hobbies integrated into the same unified timeline and heatmap engine.
