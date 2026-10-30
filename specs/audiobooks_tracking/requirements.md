# Requirements Specification: Audiobooks Tracking & Listening Sanctuary

> **Feature Directory:** `specs/audiobooks_tracking/requirements.md`  
> **Status:** Completed / Closed  

---

## 1. Persona & Purpose

Audiobook enthusiasts are unique in the reading world:
- They track **audio duration** (hours and minutes), not page counts.
- The **narrator** is as celebrated (or scrutinized) as the author.
- They listen at variable **playback speeds** (e.g. 1.0x, 1.25x, 1.5x, 1.75x, 2.0x), which changes their actual listening time versus raw audio runtime.
- Audiobooks come with rich square format artwork and audio samples/previews.

**uTrack's Goal for Audiobooks:**
Provide an audio-first chronicle designed specifically for audiobook listeners with search enrichment via Apple Books / iTunes Audiobook API and LibriVox / Internet Archive, narrator tracking, duration tracking, playback speed management, audio preview player, and thought-provoking listening takeaways.

---

## 2. Functional Requirements

### 2.1 Provider Client (`services/audiobook_service.py`)
- Seamless search across iTunes Audiobooks API (`media=audiobook`).
- Auto-extract:
  - Title & Subtitle
  - Author (`artistName`)
  - Narrator (extracted from title, subtitle, or parsed description)
  - Cover artwork (high-resolution square 600x600 px)
  - Release date & year
  - Primary genre
  - Audio sample preview URL (`.m4a` audio stream)
  - Publisher / Studio / Collection
- Multi-tier caching to prevent rate-limits and optimize search latency.

### 2.2 Data Model (`audiobooks/models.py`)
- Model `AudiobookEntry`:
  - `user`: ForeignKey to User
  - `external_id`: iTunes collectionId or LibriVox identifier
  - `title`: CharField
  - `author`: CharField
  - `narrator`: CharField (prominently tracked)
  - `duration_minutes`: PositiveIntegerField (total audio length in minutes)
  - `current_progress_minutes`: PositiveIntegerField (minutes listened)
  - `cover_url`: CharField (high-res square cover)
  - `custom_cover`: ImageField (S3/local storage upload support)
  - `preview_audio_url`: CharField (for built-in audio sample player)
  - `genre`: CharField
  - `description`: TextField
  - `release_year`: PositiveIntegerField
  - `status`: Choices (`PLAN_TO_LISTEN`, `LISTENING`, `COMPLETED`, `DROPPED`)
  - `playback_speed`: DecimalField (default `1.0`, e.g., 1.25, 1.5, 2.0)
  - `rating`: DecimalField (1 to 10 with star rating)
  - `narrator_rating`: DecimalField (1 to 10 for narration quality)
  - `review`: TextField
  - `mind_changing_takeaways`: TextField
  - `favorite_quotes`: TextField
  - `start_date`: DateField (null=True)
  - `finish_date`: DateField (null=True)
  - `relive_count`: PositiveIntegerField (number of times re-listened)
  - Properties:
    - `progress_percentage`: computed percentage `(current_progress / duration) * 100`
    - `duration_formatted`: converts minutes into `Xh Ym`
    - `effective_time_spent_minutes`: adjusts listened minutes for playback speed

### 2.3 User Interface & Experience
- **List Page (`GET /audiobooks/`)**:
  - Consistent header matching Movies, Series, and Books.
  - Quick action to open "Add Audiobook" modal.
  - Categorized into:
    1. **Currently Listening**: Card layout with square cover, audio progress bar, `Xh Ym / Total`, quick `+15 min` / `+30 min` stepper, and audio preview player.
    2. **Listening Wishlist (Plan to Listen)**: Queue of upcoming audiobooks with instant "Start Listening" action.
    3. **Completed Audiobooks & Archive**: Star rating, narration rating, review and mind-changing insight highlights.
- **Search Modal (`GET /audiobooks/search/`)**:
  - Live HTMX search of iTunes Audiobooks.
  - Square cover previews, duration, author, narrator.
  - Excludes `DROPPED` and deleted audiobooks from `is_tracked`.
  - Immediate `+ Wishlist` and `Start Listening` one-click actions.
- **Manual Audiobook Fallback**:
  - Add title, author, narrator, duration (hours and minutes), and upload custom square cover.
- **Deep Listening Hub / Detail View (`GET /audiobooks/<id>/`)**:
  - Rich square artwork, audio preview player, narration performance score, listening notes, mind-changing insights, playback speed setting, and full editing modal with clickable native date dialogs.

---

## 3. Definition of Done
1. `audiobooks` app registered in `settings.py` and included in `utrack/urls.py`.
2. Navigation link in `dashboard/templates/dashboard/sidebar.html` points to `audiobooks_list`.
3. Search and manual creation flows operational.
4. Dropped and deleted items properly show as untracked in search.
5. All date inputs use native clickable picker dialogs.
6. 100% automated test coverage in `audiobooks/tests.py`.
