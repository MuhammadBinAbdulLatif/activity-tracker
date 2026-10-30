# Validation & Verification Checklist: Date Picker UX & Tracking Status

> **Feature Directory:** `specs/datepicker_and_tracking_status/validation.md`  
> **Status:** Completed / Closed  

---

## 1. Test Gates & Verification Commands

1. **Automated Unit Tests**:
   - Run `python manage.py test movies` (Pass: 16/16)
   - Run `python manage.py test series` (Pass: 11/11)
   - Run `python manage.py test books` (Pass: 10/10)
   - Run entire test suite `python manage.py test` (Pass: 56/56)

2. **Assertions Checklist**:
   - [x] Dropped movie does not show `is_tracked=True` when searched via TMDB search endpoint.
   - [x] Deleted movie does not show `is_tracked=True` when searched via TMDB search endpoint.
   - [x] Dropped series does not show `is_tracked=True` when searched via TMDB search endpoint.
   - [x] Dropped book does not show `is_tracked=True` when searched via OpenLibrary search endpoint.
   - [x] Date inputs feature `color-scheme: dark`, inverted calendar icons, and click-to-invoke picker triggers.
