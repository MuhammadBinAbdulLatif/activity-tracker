# Technical Implementation Plan: Books Tracking & Mind Expansion

> **Feature Directory:** `specs/books_tracking/plan.md`  
> **Status:** Active / In Progress  

---

## 1. Architecture & Component Structure

### 1.1 Provider Service (`services/openlibrary.py`)
- Author class `OpenLibraryService`:
  - `search_books(query, limit=10)`: queries Open Library search API with fields `key,title,author_name,first_publish_year,cover_i,number_of_pages_median,isbn`. Formats clean dictionary with cover URL (`https://covers.openlibrary.org/b/id/{cover_i}-L.jpg`).
  - `get_book_details(work_key)`: queries Open Library work details to retrieve long synopsis/description and subjects.
- Add singleton instance `openlibrary_service = OpenLibraryService()`.

### 1.2 Django App `books`
- Create new Django application: `python manage.py startapp books`.
- Register `'books'` in `INSTALLED_APPS` (`utrack/settings.py`).
- Include `path('books/', include('books.urls'))` in `utrack/urls.py`.

### 1.3 Data Model (`books/models.py`)
- Define `BookStatus` (PLAN_TO_READ, READING, COMPLETED, DROPPED).
- Define `BookFormat` (HARDCOVER, PAPERBACK, EBOOK, AUDIOBOOK, OTHER).
- Define `BookEntry` with:
  - User FK
  - Open Library work key, isbn, title, author, publish_year, page_count, cover_url, description, genres.
  - Tracking state: status, current_page, book_format, start_date, finish_date, rating, review.
  - Mind-expanding reflections: `mind_changing_takeaways`, `favorite_quotes`, `reread_count`.
  - Custom flag and image field `custom_cover`.
  - Properties: `progress_percentage`, `display_cover_url`, `authors_list`.

### 1.4 Views & Endpoints (`books/views.py`)
1. `book_list_view` (`GET /books/`):
   - Categorized by Currently Reading, Want to Read, Completed, Dropped.
   - Calculates aggregate metrics: total books read, total pages read, currently reading count.
2. `search_books_view` (`GET /books/search/`):
   - Searches Open Library, flags which books are already tracked by the user.
   - Returns HTMX partial or JSON.
3. `add_book_view` (`POST /books/add/`):
   - Handles automated addition from Open Library or manual creation.
   - Redirects to `book_detail` upon creation.
4. `book_detail_view` (`GET /books/<int:book_id>/`):
   - Renders deep reading hub, progress meter, reflection journal, and edit controls.
5. `update_book_details_view` (`POST /books/<int:book_id>/update-details/`):
   - Updates progress, rating, review, mind-changing takeaways, favorite quotes, status, format, dates.
6. `update_book_progress_view` (`POST /books/<int:book_id>/update-progress/`):
   - Quick AJAX/POST stepper or input for current page from list or detail.
   - Auto-marks completed if current_page >= page_count.
7. `delete_book_view` (`POST /books/<int:book_id>/delete/`):
   - Removes entry and redirects to `/books/`.

### 1.5 Templates & Styling
- Follow dark emerald theme (`emerald-500` accent matching book icon in sidebar).
- `books/templates/books/list.html`:
  - Emerald progress bars, search modal with live preview, quick add and manual add tabs.
- `books/templates/books/detail.html`:
  - 2-Column layout: Book cover + status + progress widget on left, reading reflections + mind-changing takeaways + quotes + review on right.
- `books/templates/books/partials/search_results.html`:
  - Instant search result cards with cover thumbnail, author, year, page count, and Add button.
- Update `dashboard/templates/dashboard/sidebar.html` to link to `{% url 'book_list' %}`.

---

## 2. Execution Steps
1. Create `specs/books_tracking/` specs (`requirements.md`, `plan.md`, `validation.md`).
2. Implement `services/openlibrary.py`.
3. Scaffold `books` app, create models, and run migrations.
4. Implement views and URLs in `books/`.
5. Create templates matching the high-end dark UI design.
6. Connect sidebar navigation to `book_list`.
7. Author comprehensive automated tests in `books/tests.py`.
8. Run full test suite to guarantee 100% pass rate.
9. Commit and push changes.
