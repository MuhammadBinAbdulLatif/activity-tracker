# Requirements Specification: Comics & Manga Tracking Engine

> **Feature Directory:** `specs/comics_and_manga/requirements.md`  
> **Status:** Completed / Closed  

---

## 1. Persona & Product Purpose

Comics and Manga enthusiasts have distinct tracking needs compared to conventional prose books:
- **Dual Chapter & Volume Paradigms:** Manga is commonly consumed chapter-by-chapter (weekly/monthly serialized releases) or by compiled *Tankōbon* volumes. Western comics are tracked by single issues or trade paperbacks (TPBs).
- **Art as a Primary Pillar:** Visual art style and linework are as critical as narrative writing. Users demand a separate rating for **Art / Linework** in addition to overall score.
- **Publisher & Creative Teams:** Distinct tracking for writers (script) vs artists/mangaka (penciler, inker, colorist).
- **Dual Catalog Sources:** Western comics are powered by **Comic Vine**, whereas Eastern Manga/Manhwa/Manhua are powered by **AniList** and **Jikan**.
- **Manual Fallback:** Indie comics, doujinshi, webtoons, or rare prints must be manually loggable with full custom cover upload.

---

## 2. Functional Requirements

### 2.1 Provider Client Infrastructure (`services/comic_manga_service.py`)
- Query **AniList GraphQL API** for manga, manhwa, and light novels:
  - Romaji and English title resolution.
  - Mangaka / author / illustrator detection.
  - Total chapters and total volume metadata.
  - Publishing status (`RELEASING`, `FINISHED`, `CANCELLED`).
  - High-res cover image (`coverImage.extraLarge` or `large`).
- Query **Comic Vine API** (with configured `COMIC_VINE_API_KEY` and User-Agent) for western comics and graphic novels:
  - Series/volume title, publisher, start year, issue count, cover art.
- Query fallback:
  - Graceful timeout handling (max 8 seconds).
  - Multi-tier in-memory caching to avoid rate-limiting.

### 2.2 Data Model (`comics/models.py`)
- Track:
  - Item Type: `COMIC`, `MANGA`, `LIGHT_NOVEL`.
  - Status: `PLAN_TO_READ`, `READING`, `COMPLETED`, `ON_HOLD`, `DROPPED`.
  - Titles: Primary title and original Japanese/Kanji title.
  - Creators: Author/Writer and Artist/Illustrator.
  - Tracking numbers: `current_chapter`, `total_chapters`, `current_volume`, `total_volumes`.
  - Dual Ratings: Overall Rating (1–10) and Art Rating (1–10).
  - Editorial fields: Review, Favorite Arc or Issue, Notes.
  - Reading timeline: `start_date`, `finish_date`, `reread_count`.
  - Custom Cover: Local file storage or S3 compatible upload with fallback to provider CDN image URL.

### 2.3 User Experience & Views (`comics/views.py`)
- **Index View (`/comics/`):**
  - Navigation bar and search trigger modal.
  - Filter pills: All, Comics, Manga.
  - Currently Reading shelf with progress bar and quick `+1 Ch` / `+1 Vol` increment controls.
  - Plan to Read watchlist.
  - Completed shelf with rating badges and art rating stars.
- **Live Search Endpoint (`/comics/search/`):**
  - Instant live response for HTMX.
  - Type toggle in search bar (Comics vs Manga vs All).
  - Shows "Already Tracked" indicator when item is already active in user's library (ignoring `DROPPED`/deleted).
  - Quick action buttons to immediately save as "Currently Reading" or "Plan to Read".
- **Manual Fallback Entry (`/comics/add/`):**
  - Complete form allowing custom title, type, writer, artist, chapters/volumes, and image upload.
- **Detail View (`/comics/<id>/`):**
  - High-res banner, creative team credits, chapter/volume stepper, art rating, favorite arc, and modal editor.
  - Clickable native date picker dialogs for start and finish dates.
- **Update & Delete Endpoints:**
  - Progress updates with automatic status transition to `COMPLETED` when chapters/volumes match total.

---

## 3. Definition of Done
1. `comics` Django app created, registered in `INSTALLED_APPS`, and mapped to `/comics/` in `utrack/urls.py`.
2. Navigation link in `dashboard/templates/dashboard/sidebar.html` points to `{% url 'comic_list' %}`.
3. Provider integration working with AniList and Comic Vine API with fallbacks.
4. Model migrations generated and applied.
5. All views, templates, modals, and quick progress steppers operational.
6. 100% automated test coverage in `comics/tests.py`.
7. Full project test suite passes with 0 regressions.
