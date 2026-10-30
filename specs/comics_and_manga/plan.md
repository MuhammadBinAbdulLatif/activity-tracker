# Technical Implementation Plan: Comics & Manga Tracking Engine

> **Feature Directory:** `specs/comics_and_manga/plan.md`  
> **Status:** Completed / Closed  

---

## 1. Architecture & Components Overview

### 1.1 Provider Client Service (`services/comic_manga_service.py`)
Class `ComicMangaService`:
- Unified facade supporting two distinct media streams:
  1. **Comics & Western Graphic Novels:**
     - Primary API: **Comic Vine API** (`/volumes/` query filter with API key).
     - Captures: Volume/Series title, publisher (DC, Marvel, Image, Dark Horse, etc.), start year, total issue count, cover image URL (`super_url` / `medium_url`), synopsis/deck.
  2. **Manga, Manhwa & Light Novels:**
     - Primary API: **AniList GraphQL API** (`type: MANGA`).
     - Secondary Fallback: **Jikan API v4** (`https://api.jikan.moe/v4/manga`).
     - Captures: Romaji & English titles, author/artist (`staff`), format (`MANGA`, `NOVEL`, `ONE_SHOT`), chapters, volumes, publishing status (`RELEASING`, `FINISHED`), high-res cover image (`extraLarge` / `large`), synopsis.
- Robust query router:
  - `search(query, media_type='all', limit=10)`:
    - If `media_type == 'comic'`: queries Comic Vine.
    - If `media_type == 'manga'`: queries AniList (fallback Jikan).
    - If `media_type == 'all'`: combines and interleaves top results.
- In-memory/Redis caching with key hashing and graceful timeout fallbacks.

---

### 1.2 Data Model (`comics/models.py`)
- **`ComicMangaType`**:
  - `COMIC` ("Western Comic / Graphic Novel")
  - `MANGA` ("Manga / Manhwa / Manhua")
  - `LIGHT_NOVEL` ("Light Novel")
- **`ComicMangaStatus`**:
  - `PLAN_TO_READ` ("Plan to Read")
  - `READING` ("Currently Reading")
  - `COMPLETED` ("Completed")
  - `ON_HOLD` ("On Hold")
  - `DROPPED` ("Dropped")
- **`ComicMangaEntry` Model**:
  - `user`: ForeignKey to User
  - `item_type`: CharField with choices from `ComicMangaType`
  - `external_id`: CharField (e.g. `cv-4050-12345` or `anilist-30002`)
  - `title`: CharField(max_length=255)
  - `original_title`: CharField(max_length=255, blank=True) (for Japanese Kanji/Romaji)
  - `creator_author`: CharField(max_length=255, blank=True) (Writer/Mangaka)
  - `artist`: CharField(max_length=255, blank=True) (Illustrator/Colorist)
  - `publisher`: CharField(max_length=255, blank=True) (e.g. Marvel, Shueisha, Kodansha)
  - `cover_url`: CharField(max_length=1000, blank=True)
  - `custom_cover`: ImageField(upload_to="comics/covers/", null=True, blank=True)
  - `description`: TextField(blank=True)
  - `start_year`: PositiveIntegerField(null=True, blank=True)
  - `total_chapters`: PositiveIntegerField(null=True, blank=True)
  - `total_volumes`: PositiveIntegerField(null=True, blank=True)
  - `current_chapter`: PositiveIntegerField(default=0)
  - `current_volume`: PositiveIntegerField(default=0)
  - `status`: CharField with choices from `ComicMangaStatus`
  - `rating`: DecimalField(max_digits=3, decimal_places=1, null=True, blank=True) (1.0 to 10.0 scale)
  - `art_rating`: DecimalField(max_digits=3, decimal_places=1, null=True, blank=True) (dedicated artwork score)
  - `review`: TextField(blank=True)
  - `favorite_arc_or_issue`: CharField(max_length=255, blank=True)
  - `notes`: TextField(blank=True)
  - `start_date`: DateField(null=True, blank=True)
  - `finish_date`: DateField(null=True, blank=True)
  - `reread_count`: PositiveIntegerField(default=0)
  - `created_at`: DateTimeField(auto_now_add=True)
  - `updated_at`: DateTimeField(auto_now=True)

#### Computed Properties:
- `display_cover`: Returns uploaded image URL or external `cover_url` fallback.
- `progress_percentage`: Calculates completion based on `current_chapter / total_chapters` or `current_volume / total_volumes`.
- `progress_display`: Formatted as `Ch. {current} / {total}` or `Vol. {current} / {total}`.

---

### 1.3 Routing & Endpoints (`comics/urls.py` & `comics/views.py`)
- `GET /comics/` (`comic_list_view`):
  - Category dashboard grouped by Reading, Plan to Read, Completed, and On Hold/Dropped.
  - Type filters (All, Comics, Manga).
- `GET /comics/search/` (`search_comics_view`):
  - Dynamic HTMX search querying Comic Vine and AniList with live preview cards.
  - Automatically identifies whether an item is already tracked in the user's library (excluding `DROPPED`/deleted).
- `POST /comics/add/` (`add_comic_view`):
  - Adds from search result or manual creation fallback.
- `GET /comics/<id>/` (`comic_detail_view`):
  - Deep reading hub with cover artwork, artwork quality rating, chapter/volume tracker, favorite arc, and modal editor.
- `POST /comics/<id>/update-progress/` (`update_comic_progress_view`):
  - Increment/decrement chapter/volume via inline HTMX or JSON endpoints.
- `POST /comics/<id>/update-details/` (`update_comic_details_view`):
  - Full modal update including start/finish dates (with native picker), ratings, arc, and notes.
- `POST /comics/<id>/delete/` (`delete_comic_view`):
  - Removes entry and redirects to `/comics/`.

---

### 1.4 Frontend Templates & Components
- `comics/templates/comics/list.html`:
  - Consistent layout matching Books and Movies.
  - Type toggle badge filter (All / Comics / Manga).
  - "Currently Reading" showcase cards with stepper controls (`+1 Ch`, `+1 Vol`).
  - Search & Manual addition modal.
- `comics/templates/comics/detail.html`:
  - Rich comic/manga presentation banner with artwork badge, writer/illustrator credits, publisher, reading meter, and editable review notes.
- `comics/templates/comics/partials/search_results.html`:
  - Instant live search results with item type pills (`COMIC` vs `MANGA`), publisher/mangaka, total chapters/volumes, and one-click quick add.

---

### 1.5 System Integration
- Register `comics` app in `utrack/settings.py` `INSTALLED_APPS`.
- Include `comics.urls` in `utrack/urls.py`.
- Update `dashboard/templates/dashboard/sidebar.html` navigation item for Comics & Manga to point to `{% url 'comic_list' %}`.
