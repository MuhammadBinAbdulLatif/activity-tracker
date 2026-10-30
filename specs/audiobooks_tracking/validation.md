# Quality Assurance & Test Gates: Audiobooks Tracking

> **Feature Directory:** `specs/audiobooks_tracking/validation.md`  
> **Status:** Completed / Closed  

---

## 1. Test Gates & Verification Commands

1. **Commands to Run**:
   - `python manage.py makemigrations audiobooks` (Completed)
   - `python manage.py migrate audiobooks` (Completed)
   - `python manage.py test audiobooks` (Passed: 7/7)
   - `python manage.py test` (Passed: 63/63)

2. **Assertions Checklist**:
   - [x] `audiobook_list_view` renders list of Listening, Plan to Listen, Completed, and Dropped entries.
   - [x] Search endpoint queries provider and excludes `DROPPED` / deleted audiobooks from `is_tracked`.
   - [x] Progress updater properly calculates percentage and auto-completes when progress reaches total duration.
   - [x] Custom cover upload works properly (local or S3).
   - [x] Detail page renders square cover, audio preview player, narrator rating, and date dialogs.
   - [x] All automated tests pass with 0 failures.
