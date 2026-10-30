# Validation & Verification Checklist: Books Tracking

> **Feature Directory:** `specs/books_tracking/validation.md`  
> **Status:** Active / In Progress  

---

## 1. Test Verification Strategy

Every feature must be verified through automated tests (`python manage.py test books`) and regression checks across the entire platform (`python manage.py test`).

### 1.1 Automated Test Suite Matrix (`books/tests.py`)
1. **Model Tests (`BookModelTest`):**
   - Test default values (status, format, reread_count, pages).
   - Test `progress_percentage` calculation (0%, 50%, 100%, clamped when exceeding page_count).
   - Test `display_cover_url` fallback hierarchy (custom poster -> Open Library cover URL -> fallback placeholder).
   - Test `authors_list` parsing.
2. **Open Library Service Mocking Tests (`BookServiceTest`):**
   - Test mock search query parsing and returned dictionary format.
   - Test error handling when network fails or returns non-200.
3. **View & Route Tests (`BookViewsTest`):**
   - Test login requirement for `/books/`, `/books/<id>/`, `/books/add/`.
   - Test `book_list_view` renders separate buckets for reading, watchlist, completed.
   - Test `add_book_view` via automated Open Library payload.
   - Test `add_book_view` via manual custom entry with custom details and format.
   - Test `book_detail_view` renders title, author, mind-changing takeaways, quotes, and progress.
   - Test `update_book_details_view` updates status, rating, mind-changing takeaways, and quotes.
   - Test status transition (e.g. Setting `current_page == page_count` auto-promotes to COMPLETED).
   - Test `update_book_progress_view` quick page stepper.
   - Test `delete_book_view` deletes record and enforces user ownership isolation.
4. **Integration & Navigation Tests:**
   - Verify sidebar Books link points to `/books/` and resolves without template errors.
   - Verify overall test suite passes without regressions.

---

## 2. Test Execution Command
```bash
python manage.py test books
python manage.py test
```

## 3. Assertions Checklist
- [ ] Model migrations execute cleanly (`python manage.py makemigrations books` & `migrate`).
- [ ] No syntax errors or broken imports in `services/openlibrary.py` and `books/`.
- [ ] All 10+ new automated tests in `books/tests.py` pass.
- [ ] Entire test suite passes with 0 failures or errors.
- [ ] Git commit and push completed upon all assertions passing.
