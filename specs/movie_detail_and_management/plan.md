# Technical Implementation Plan: Dedicated Movie Detail Page & Status Management

> **Feature Directory:** `specs/movie_detail_and_management/plan.md`  
> **Status:** Draft / Active  

---

## 1. Architectural Strategy

### 1.1 Data Model Enhancements (`movies.models.MovieEntry`)
1. Add `cast` field:
   - `cast = models.TextField(blank=True, help_text="Comma-separated or formatted list of actors/characters")`
2. Add `tagline` field (optional from TMDB):
   - `tagline = models.CharField(max_length=500, blank=True)`
3. Add helper method `actors_list`:
   - Returns a list of actor names for clean template rendering.
4. Add property `backdrop_url`:
   - Returns `https://image.tmdb.org/t/p/w1280{self.backdrop_path}` if present, else fallback.

### 1.2 TMDB Client Sync & Enrichment
- When a movie is added from TMDB in `movies/views.py`:
  - Extract top 8 cast members (`credits.cast`) and save to `cast`.
  - Save `tagline` and `backdrop_path`.

### 1.3 View & Routing Architecture (`movies/urls.py` & `movies/views.py`)
1. **Route `/movies/<int:movie_id>/` $\rightarrow$ `movie_detail_view`**:
   - Renders `movies/detail.html`.
   - If TMDB details are missing cast/actors, dynamically fetch and backfill from TMDB (cached).
2. **Route `/movies/<int:movie_id>/update-details/` $\rightarrow$ `movie_update_details_view`**:
   - Handles full POST update for status (including status reversion), rating, watch_date, review, rewatch_count, and custom attributes.
3. **Route `/movies/<int:movie_id>/delete/` $\rightarrow$ `movie_delete_view`**:
   - Deletes entry and redirects back to `/movies/`.

### 1.4 Templates & UI
1. **`movies/templates/movies/detail.html`**:
   - Full-width hero banner with backdrop image, dark radial vignette, and back button (`← Back to Movies`).
   - 2-Column layout:
     - Left: Large poster card, quick status switcher pills, and danger zone (delete).
     - Right: Title, release year, runtime, director badge, genres, synopsis, cast grid/pills, and interactive personal log form (rating, watch date, rewatch count, review).
2. **Update `movies/templates/movies/list.html`**:
   - Wrap movie titles, posters, and card containers with links to `{% url 'movie_detail' movie.id %}`.

---

## 2. Step-by-Step Execution Plan

### Step 1: Specifications Authoring [IN PROGRESS]
- Complete `requirements.md`, `plan.md`, `validation.md`.

### Step 2: Schema Migration
- Add `cast` and `tagline` to `MovieEntry`.
- Run `makemigrations` and `migrate`.

### Step 3: Implement Views & Routing
- Author `movie_detail_view`, `movie_update_details_view`, and `movie_delete_view` in `movies/views.py`.
- Register routes in `movies/urls.py`.

### Step 4: Build Detail Template & Update List Template
- Create `movies/templates/movies/detail.html`.
- Update `movies/templates/movies/list.html` so all cards and titles link to the detail page.

### Step 5: Automated Testing
- Author test cases in `movies/tests.py` testing detail view rendering, cast display, status reversion, and personal notes editing.
- Run `python manage.py test`.

### Step 6: Git Lifecycle
- Mark specifications Completed.
- Commit and push to GitHub.
