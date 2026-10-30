# Quality Assurance & Test Gates: Comics & Manga

> **Feature Directory:** `specs/comics_and_manga/validation.md`  
> **Status:** Completed / Closed  

---

## 1. Test Gates & Verification Commands

1. **Commands Run:**
   - `python manage.py makemigrations comics` (Passed: `0001_initial.py` created)
   - `python manage.py migrate comics` (Passed: applied successfully)
   - `python manage.py test comics` (Passed: 8/8 tests OK in 15.26s)
   - `python manage.py test` (Passed: 71/71 tests OK in 124.18s)

2. **Assertions Checklist:**
   - [x] `comic_list_view` renders list of Reading, Plan to Read, Completed, and Dropped entries.
   - [x] Type filters (`?type=MANGA`, `?type=COMIC`) properly filter entries.
   - [x] Search endpoint queries AniList and Comic Vine and excludes `DROPPED` / deleted entries from `is_tracked`.
   - [x] Progress updater increments chapter or volume and triggers auto-completion when reached.
   - [x] Custom cover upload works properly (local or S3).
   - [x] Detail page renders item type badge, art rating, favorite arc, and clickable native date dialogs.
   - [x] Sidebar navigation accurately links to `comic_list`.
   - [x] All automated tests pass with zero failures (71/71 passing).
