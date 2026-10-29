# Validation & Quality Assurance: Movie Detail & Status Management

> **Feature Directory:** `specs/movie_detail_and_management/validation.md`  
> **Status:** Draft / Active Specification  

---

## 1. Test Verification Strategy

Automated tests will be created and executed in `movies/tests.py` to verify:
- Navigation from list to detail page.
- Rendering of movie metadata, cast, director, and overview on detail page.
- Status switching and reversion (from `COMPLETED` back to `PLAN_TO_WATCH` or `WATCHING`).
- Updating personal ratings, review notes, and watch date.
- Deleting a movie entry.

### 1.1 Test Matrix

| Test Case | Scenario / Condition | Expected Result |
| :--- | :--- | :--- |
| `test_movie_detail_requires_login` | Unauthenticated GET `/movies/<id>/` | Redirects to `/accounts/login/` |
| `test_movie_detail_renders_for_owner` | Authenticated owner GET `/movies/<id>/` | Status `200 OK`, renders `movies/detail.html`, contains title, director, overview |
| `test_movie_detail_renders_cast` | Movie with cast data viewed on detail page | Cast/actors displayed |
| `test_movie_status_reversion` | Movie with status `COMPLETED` changed back to `PLAN_TO_WATCH` | Status changes to `PLAN_TO_WATCH`; watch date can be cleared |
| `test_movie_update_personal_log` | POST to update rating, review, rewatch_count | Values successfully saved to database |
| `test_movie_delete` | POST to delete movie entry | Entry deleted from database; redirected to `/movies/` |
| `test_list_cards_link_to_detail` | Inspect `/movies/` HTML | Cards and titles contain links to `/movies/<id>/` |

---

## 2. Test Execution Command
```bash
python manage.py test movies
python manage.py test
```

---

## 3. Pass Criteria & Gates
- [ ] All test cases pass with 100% success.
- [ ] No regression across existing tests.
- [ ] Clean semantic UI aligned with `specs/styles.md`.
