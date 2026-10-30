# Technical Implementation Plan: Audiobooks Tracking

> **Feature Directory:** `specs/audiobooks_tracking/plan.md`  
> **Status:** Completed / Closed  

---

## 1. Architecture & Components

### 1.1 Provider Service (`services/audiobook_service.py`)
- Class `AudiobookService`:
  - `search_audiobooks(query, limit=10)`:
    - Queries `https://itunes.apple.com/search?term={query}&media=audiobook&limit={limit}`
    - Upgrades artwork from `100x100bb.jpg` to `600x600bb.jpg` for high-resolution rendering.
    - Extracts narrator from title patterns (e.g. `(Narrated by Wil Wheaton)`) or parsed description `read by ...`.
    - Returns structured metadata dictionary.
  - In-memory/redis caching with error handling.

### 1.2 Data Model (`audiobooks/models.py`)
- `AudiobookStatus`: `PLAN_TO_LISTEN`, `LISTENING`, `COMPLETED`, `DROPPED`.
- `AudiobookEntry`:
  - Fields: `user`, `external_id`, `title`, `author`, `narrator`, `duration_minutes`, `current_progress_minutes`, `cover_url`, `custom_cover`, `preview_audio_url`, `genre`, `description`, `release_year`, `status`, `playback_speed`, `rating`, `narrator_rating`, `review`, `mind_changing_takeaways`, `favorite_quotes`, `start_date`, `finish_date`, `relive_count`.
  - Properties: `display_cover`, `progress_percentage`, `duration_display`, `current_progress_display`, `time_remaining_display`.

### 1.3 Views & Endpoints (`audiobooks/views.py` & `audiobooks/urls.py`)
- `audiobook_list_view`: `GET /audiobooks/`
- `search_audiobooks_view`: `GET /audiobooks/search/` (HTMX & JSON, excludes DROPPED)
- `add_audiobook_view`: `POST /audiobooks/add/`
- `audiobook_detail_view`: `GET /audiobooks/<id>/`
- `update_audiobook_details_view`: `POST /audiobooks/<id>/update-details/`
- `update_audiobook_progress_view`: `POST /audiobooks/<id>/update-progress/`
- `delete_audiobook_view`: `POST /audiobooks/<id>/delete/`

### 1.4 Templates
- `audiobooks/templates/audiobooks/list.html`
- `audiobooks/templates/audiobooks/detail.html`
- `audiobooks/templates/audiobooks/partials/search_results.html`

### 1.5 System Integration
- Register `audiobooks` in `utrack/settings.py` `INSTALLED_APPS`.
- Include `audiobooks.urls` in `utrack/urls.py`.
- Update `dashboard/templates/dashboard/sidebar.html` navigation item for Audiobooks.
