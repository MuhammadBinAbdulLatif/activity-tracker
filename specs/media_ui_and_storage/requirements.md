# Scope & Requirements: Media UI Overhaul & Cloud S3 Poster Storage

> **Feature Directory:** `specs/media_ui_and_storage/requirements.md`  
> **Status:** Completed & Closed  

---

## 1. Overview & Objectives

Addressed three critical enhancements for the **Movies** and **Series** modules:
1. **Interactive, Clickable UI Controls:** Replaced subtle/flat text triggers with prominent, high-contrast, clickable buttons (distinct hover effects, button affordance, clear primary/secondary variants) for actions like "Start Watching", "Mark as Watched", "+1 Episode", and "+ Watchlist".
2. **Card & Typography Visual Hierarchy Overhaul:** Enlarged posters, title typography, status badges, progress bars, and meta tags to give media items commanding, high-value visual presence.
3. **Comprehensive Custom Entry Creation with Amazon S3 Poster Storage:**
   - Allowed users creating custom movies or series to set full initial details: title, status (*Currently Watching*, *Completed*, *Plan to Watch*, *Waiting for Next Season*), initial season/episode counts, release dates, ratings, and reviews.
   - Supported file upload for custom poster artwork, safely streamed to **Amazon S3** (with local media storage fallback if S3 credentials are not yet configured).

---

## 2. Functional Requirements

### 2.1 Action Button Affordance & UI Redesign
- Buttons clearly look like interactive action triggers, not passive labels.
- **Primary Action (Start Watching / Resume):** High-contrast filled button (`bg-zinc-100 hover:bg-white text-zinc-950 font-bold rounded-xl shadow-md active:scale-95`).
- **Completion Action (Mark Watched / Complete):** Vibrant filled/bordered button (`bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-bold rounded-xl shadow-md`).
- **Watchlist Action (+ Watchlist):** Clear zinc action button (`bg-zinc-800 hover:bg-zinc-700 text-white font-semibold rounded-xl border border-zinc-700`).
- **Episodic Stepper (+1 Episode):** Prominent action pill (`bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-md`).

### 2.2 Visual Scale & Card Expansion
- **Poster Images:**
  - In list grids: Expanded to `w-24 h-36` and `w-full h-56` in vertical grids with rounded borders and deep drop-shadows.
- **Titles & Typography:**
  - Show/Movie titles: Increased to `text-base sm:text-lg font-bold text-white tracking-tight`.
  - Progress badges & metadata lines: Elevated to `text-xs font-semibold text-zinc-300`.

### 2.3 Custom Creation Flow & Amazon S3 Integration
1. **Full Status Selection:**
   - Movies: *Plan to Watch*, *Currently Watching*, *Completed*, *Dropped*.
   - Series: *Currently Watching*, *Plan to Watch*, *Waiting for Next Season*, *Completed*.
2. **Custom Poster Artwork Upload:**
   - File input field: `<input type="file" name="poster_file" accept="image/*">`.
   - Stored in a dedicated `custom_poster` field (`ImageField(upload_to="posters/movies/%Y/%m/")` and `upload_to="posters/series/%Y/%m/"`).
   - `poster_url` property dynamically returns the S3/Media URL if uploaded, falling back to TMDB or default artwork.
3. **Storage Configuration:**
   - Configured `STORAGES` backend in `utrack/settings.py` with `django-storages` and `boto3`.
   - If `AWS_ACCESS_KEY_ID` and `AWS_STORAGE_BUCKET_NAME` are set in `.env`, uploads automatically stream to Amazon S3.
   - If empty, seamlessly uses local `media/` file storage so developer workflows never break.

---

## 3. Definition of Done (Acceptance Criteria)
- [x] Specification files authored under `specs/media_ui_and_storage/`.
- [x] Buttons on `/movies/` and `/series/` upgraded with high visual affordance.
- [x] Cards, posters, and progress bars enlarged and redesigned for prominent presentation.
- [x] Custom movie and series modals support full status selection and image file upload.
- [x] `ImageField` added to `MovieEntry` and `SeriesEntry` with S3 / Media storage support.
- [x] Automated tests verify custom creation with files and button rendering.
- [x] All 31 tests pass with 100% success.
