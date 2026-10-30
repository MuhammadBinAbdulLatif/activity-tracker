# Requirements Specification: Books Tracking & Management

> **Target Directory:** `specs/books_tracking/requirements.md`  
> **Status:** Active / In Progress  

---

## 1. Problem Statement & Mission Alignment
In accordance with `specs/mission.md` and `specs/roadmap.md` (Phase 5, Step 5.2), users need a comprehensive tracking engine for books and literature.
Unlike passive watch tracking, books demand dynamic reading progress metrics (pages read vs total pages, reading percentage), reflective journaling (what was mind-changing / key insights, memorable quotes, key takeaways), reading format (Hardcover, Paperback, E-Book, Audiobook), and status lifecycles (Want to Read, Currently Reading, Completed, Dropped).

The feature must provide:
1. Automated search and enrichment via Open Library (title, author, publish year, page count, cover artwork, Open Library work ID, synopsis).
2. Custom/manual fallback creation for unlisted, rare, or personal books.
3. Reading session & progress tracking (current page, total pages, progress percentage calculation, completion state transition).
4. Mind-expansion & reflective journaling:
   - Mind-changing insights / key lessons ("What was so mind-changing about it?").
   - Favorite quotes.
   - Comprehensive review & personal rating (1-10 or 1-5 decimal scale).
   - Format selector (Physical Hardcover, Paperback, Kindle / E-Book, PDF, Other).
5. Fast quick-actions from list view (update progress, move to completed/reading, delete).
6. Dedicated rich detail view (`/books/<int:book_id>/`) with status switching, progress slider/counter, deep note editing, and book cover display.
7. Seamless dashboard integration with sidebar active count/percentage and activity stats.

---

## 2. Functional Requirements

### 2.1 Data Model (`books.models.BookEntry`)
- **User Ownership:** ForeignKey to `django.contrib.auth.models.User` (cascade delete).
- **Metadata Fields:**
  - `openlibrary_key`: `CharField(max_length=100, blank=True, db_index=True)` (e.g. `/works/OL17930368W`).
  - `isbn`: `CharField(max_length=50, blank=True)`.
  - `title`: `CharField(max_length=255)`.
  - `author`: `CharField(max_length=255, blank=True)` (comma-separated or single primary author).
  - `publish_year`: `PositiveIntegerField(null=True, blank=True)`.
  - `page_count`: `PositiveIntegerField(default=0, help_text="Total pages in book")`.
  - `cover_url`: `CharField(max_length=500, blank=True)`.
  - `description`: `TextField(blank=True)`.
  - `genres`: `CharField(max_length=255, blank=True)`.
- **Personal Tracking & Progress Fields:**
  - `status`: Choices `PLAN_TO_READ` ("Want to Read"), `READING` ("Currently Reading"), `COMPLETED` ("Completed"), `DROPPED` ("Dropped"). Default `PLAN_TO_READ`.
  - `current_page`: `PositiveIntegerField(default=0, help_text="Current page read")`.
  - `book_format`: Choices `HARDCOVER` ("Hardcover"), `PAPERBACK` ("Paperback"), `EBOOK` ("E-Book / Kindle"), `AUDIOBOOK` ("Audiobook"), `OTHER` ("Other"). Default `PAPERBACK`.
  - `start_date`: `DateField(null=True, blank=True)`.
  - `finish_date`: `DateField(null=True, blank=True)`.
  - `rating`: `DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)`.
  - `review`: `TextField(blank=True, help_text="General review and personal verdict")`.
  - `mind_changing_takeaways`: `TextField(blank=True, help_text="What was mind-changing, perspective-shifting, or impactful")`.
  - `favorite_quotes`: `TextField(blank=True, help_text="Memorable quotes or excerpts")`.
  - `reread_count`: `PositiveIntegerField(default=0)`.
  - `is_custom`: `BooleanField(default=False)`.
  - `custom_cover`: `ImageField(upload_to="posters/books/%Y/%m/", blank=True, null=True)`.
  - `created_at` & `updated_at`: `DateTimeField`.

### 2.2 Computed Properties & Helpers
- `progress_percentage`: Computes `int((current_page / page_count) * 100)` when `page_count > 0`, clamped between 0 and 100. If `status == COMPLETED`, returns 100%.
- `display_cover_url`: Returns custom cover url if uploaded, else Open Library cover URL, else an aesthetic book cover placeholder.
- `authors_list`: List of author names parsed from `author`.

### 2.3 Provider Service (`services/openlibrary.py`)
- Standardized search via `https://openlibrary.org/search.json?q={query}&limit=10&fields=key,title,author_name,first_publish_year,cover_i,number_of_pages_median,isbn`.
- Standardized work details via `https://openlibrary.org{key}.json`.
- Cover image URL generation: `https://covers.openlibrary.org/b/id/{cover_i}-L.jpg`.
- Proper error handling and timeouts to prevent UI blocking.

### 2.4 User Interface & Views
- **List Page (`/books/`):**
  - Section tabs or categorized groups: "Currently Reading" (with active progress bar and page quick-increment button), "Want to Read" (Reading Wishlist), and "Completed & Library" (with star ratings and mind-changing snippet badges).
  - Search & Add modal: live search against Open Library with instant add button.
  - Manual book creation tab/modal for books not found online or custom notes.
- **Detail Page (`/books/<int:book_id>/`):**
  - Hero header with cover artwork, title, author badge, publication year, total pages, and reading format.
  - Interactive Reading Progress meter: Page stepper (`-10`, `+10`, direct input) and progress bar.
  - Status switcher (Reading, Completed, Want to Read, Dropped).
  - Mind-Expansion & Reflection section:
    - Mind-Changing Lessons & Takeaways textarea.
    - Favorite Quotes & Excerpts.
    - Personal Rating (1-10) and Review.
    - Reading Dates (Start Date, Finish Date).
    - Reread counter button.
  - Delete action with confirmation modal.
- **Quick Actions:**
  - Quick page update POST endpoint `/books/<int:book_id>/update-progress/`.
  - Quick status toggle endpoint `/books/<int:book_id>/toggle-status/`.

---

## 3. Definition of Done
1. Dedicated Django app `books` created and registered in `INSTALLED_APPS` and `utrack/urls.py`.
2. Model `BookEntry` created and migrated with clean indexes and constraints.
3. Open Library integration service `services/openlibrary.py` fully working with graceful fallbacks.
4. UI matches modern aesthetic (shadcn-inspired, emerald accent matching the sidebar book icon, zinc-900 glass cards).
5. Sidebar link for Books updated to link to `{% url 'book_list' %}`.
6. Comprehensive unit and integration test suite passing with 100% pass rate.
