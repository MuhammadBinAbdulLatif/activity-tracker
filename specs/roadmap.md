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

## Phase 3: Provider Client Infrastructure & Caching
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

## Phase 4: Media Tracking Engines (Category by Category)

Each category supports two paths of entry:
1. **Automated Search & Enrichment (Primary):** User queries a title $\rightarrow$ metadata, poster, release date, creator/director/author auto-fetched $\rightarrow$ user inputs personal tracking details (date consumed, user rating, personal notes, status).
2. **Custom / Manual Fallback:** If an item is unlisted or niche, the user can manually create an entry with full custom details (title, release year, creator, description, custom cover/poster).

### Step 3.1: Movies & Series
- Search TMDB by title/year.
- Instant auto-fill: poster path, overview, genres, director/cast, runtime, release date/year.
- User inputs: watch date, user rating (e.g. 1–10 or 1–5 stars), review/notes, rewatch count, episodes/seasons watched (for series).
- Manual creation fallback for indie, unlisted, or home video items.

### Step 3.2: Books & Literature
- Search Open Library / Google Books by title, author, or ISBN.
- Auto-fill: book cover, author(s), publisher, publication year, page count, synopsis.
- User inputs: date completed/started, reading progress (pages/percentage), user rating, review, format (hardcover, paperback, ebook).
- Manual creation fallback.

### Step 3.3: Audiobooks
- Search Open Library / iTunes Search / Audnexus.
- Auto-fill: cover art, narrator, author, total duration/audio length.
- User inputs: listen date, listening speed/progress, personal rating, thoughts.
- Manual creation fallback.

### Step 3.4: Comics & Manga / Anime
- Search Comic Vine / AniList / Jikan.
- Auto-fill: issue/volume count, artist, writer, status, covers.
- User inputs: issues/chapters read, date consumed, rating, notes.
- Manual creation fallback.

---

## Phase 5: Universal Unified Search
- Unified search bar across all supported categories.
- Real-time suggestions (instant search results grouped by category: Movies, Books, Anime, etc.).
- Direct "One-Click Track" action from search results.

---

## Phase 6: Home Page Dashboard & Temporal Retrospectives (The Mission Delivery)

### 6.1 The Home Page ("Currently Engaging & Immediate Focus")
The home page is the first screen the user sees upon opening uTrack. It must immediately ground them with their active pursuits:
- **"Currently In-Progress" Hub:**
  - **Books & Comics/Manga:** Exactly where the user is right now (e.g., *"Page 184 of 320"*, chapters read, % completed progress bar).
  - **Series & Anime:** What they are actively binging (e.g., *"Season 2, Episode 4"*, next episode up).
  - **Audiobooks:** Current playback position / chapters listened.
  - **Quick-Update Controls:** One-click increment (e.g., `+1 Episode`, `Update Page Number`) directly from the home screen without navigating deep into subpages.
- **"Watchlist / Up Next" Carousel:**
  - Pinned movies, books, and shows queued for immediate consumption.
- **Recent Activity Highlights:**
  - Items completed in the last few days with quick-rate/review prompts.

### 6.2 The Activity Contribution Heatmap ("GitHub-Style Life Activity Graph")
A prominent, visual heat-grid calendar (inspired by GitHub's contribution graph):
- **Visual Representation:**
  - 365-day / 52-week rolling heat map showing green/intensity shaded squares for each day.
  - Hover / click on any square reveals that day's log: *"Oct 24: 1 Movie watched, 42 pages read, 1 workout completed"*.
- **Multi-Category Aggregate:**
  - Calculates daily activity intensity across all categories (pages read, episodes watched, audio minutes listened, workouts done).
  - Provides instant positive reinforcement and visual proof that the user has been active and engaged, banishing the feeling of wasted time.
- **Placement:** Displayed prominently on the Home Page and on User Profile / Retrospective pages.

### 6.3 Retrospectives & Timelines ("What I Did")
- **Monthly Summary ("What I Did This Month"):**
  - Aggregated view of everything watched, read, listened to, and completed in any chosen month.
  - Cumulative totals (hours watched, pages read, audio hours listened).
  - Top-rated items of the month and personal highlights.
- **Daily Log / Timeline:** Chronological feed of daily activities and consumption.
- **Yearly Wrapped / Retrospective:** Comprehensive yearly breakdown and trends.

---

## Phase 7: Life & Habit Activity Tracking (Extensibility)
- Workouts, exercise sessions, and custom daily hobbies integrated into the same unified timeline.
