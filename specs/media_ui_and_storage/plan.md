# Technical Implementation Plan: Media UI Overhaul & Cloud S3 Poster Storage

> **Feature Directory:** `specs/media_ui_and_storage/plan.md`  
> **Status:** Completed & Closed  

---

## 1. Architectural Strategy

### 1.1 Storage Architecture
1. **Dynamic Storage Backend:**
   - Configured `STORAGES` in `utrack/settings.py` with `boto3` and `django-storages`.
   - Checks if `AWS_STORAGE_BUCKET_NAME` is configured:
     - If yes: Uses `storages.backends.s3boto3.S3Boto3Storage` for `default` storage backend.
     - If no: Uses `django.core.files.storage.FileSystemStorage` pointing to `BASE_DIR / 'media'`.
   - Added `MEDIA_URL = '/media/'` and `MEDIA_ROOT = BASE_DIR / 'media'`.
   - Wired `MEDIA_URL` static serving in `utrack/urls.py` in debug mode.

2. **Model Schema Updates:**
   - `movies.models.MovieEntry`: Added `custom_poster = models.ImageField(upload_to="posters/movies/%Y/%m/", blank=True, null=True)`.
   - `series.models.SeriesEntry`: Added `custom_poster = models.ImageField(upload_to="posters/series/%Y/%m/", blank=True, null=True)`.
   - Updated `poster_url` property in both models to prioritize uploaded posters.

### 1.2 UI & Component Redesign
1. **Button Styling Transformation:**
   - Replaced flat text buttons with prominent, high-contrast action pills:
     - Primary: `px-4 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-bold text-xs rounded-xl shadow-md active:scale-95 transition-all`.
     - Secondary / Watchlist: `px-3.5 py-2 bg-zinc-800 hover:bg-zinc-700 text-white font-semibold text-xs rounded-xl border border-zinc-700 shadow-sm`.
     - Stepper (+1 Ep): `px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-md`.
2. **Card Scale & Typography Elevation:**
   - Replaced small thumbnails with bold vertical / horizontal hero artwork (`w-24 h-36` and `w-full h-56`).
   - Increased titles to `text-base sm:text-lg font-bold text-white`.

### 1.3 Form & View Updates
1. Added `enctype="multipart/form-data"` to creation forms.
2. In `movies/views.py` and `series/views.py`:
   - Handles `request.FILES.get("poster_file")`.
   - Supports full status choices (`status`, `rating`, `review`, `watch_date`, `total_seasons`, `total_episodes`).

---

## 2. Step-by-Step Execution Plan

### Step 1: Specs Definition [COMPLETED]
- Authored `requirements.md`, `plan.md`, `validation.md`.

### Step 2: Storage Configuration in `settings.py` & `.env` [COMPLETED]
- Installed `boto3`, `django-storages`, and `pillow`.
- Added AWS S3 template variables to `.env`.
- Added `storages` to `INSTALLED_APPS` and configured dynamic S3 / local fallback in `utrack/settings.py`.

### Step 3: Model Schema Migrations [COMPLETED]
- Added `custom_poster` field to `MovieEntry` and `SeriesEntry`.
- Migrated database schema.

### Step 4: Redesign Views & Templates [COMPLETED]
- Re-crafted `movies/templates/movies/list.html` and `series/templates/series/list.html`.
- Upgraded search partials with distinct, high-contrast action buttons.
- Expanded custom creation modals to accept file uploads and full status choices.

### Step 5: Automated Testing [COMPLETED]
- Authored tests for custom image uploads, fallback URLs, and prominent button selectors in `movies/tests.py` and `series/tests.py`.
- Ran full test suite with 31/31 tests passing.

### Step 6: Documentation & Git Commit/Push [COMPLETED]
- Closed specifications and pushed to GitHub.
