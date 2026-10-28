# Technology Stack & Infrastructure Specification

> **Target Directory:** `specs/techstack.md`  
> **Audience:** Development Agent & Engineering Team  
> **Status:** Active Reference  

---

## 1. Backend Core

- **Language:** Python 3.11+
- **Web Framework:** Django (LTS)
- **Data Access / ORM:** Django ORM
- **Authentication:** Standard Django Authentication (`django.contrib.auth`), clean baseline session-based auth (registration, login, logout, password management).

---

## 2. Presentation & Frontend

- **Template Engine:** Django Native HTML Templates (`DTL` - Django Template Language)
- **Styling & UI (Recommended Additions):**
  - **Tailwind CSS** or modern clean CSS utility classes for lightweight, responsive, elegant styling without heavy JS framework overhead.
  - **HTMX** (Recommended for dynamic UI interactions): Enables smooth searching, auto-complete provider lookups, and instant timeline updates without full page reloads, preserving Django template simplicity.
  - **Alpine.js** (Optional/Lightweight): For minimal client-side interactivity (modals, dropdowns, tabs).

---

## 3. Database & Caching Layer

- **Primary Database:** PostgreSQL
  - Driver: `psycopg` (v3) / `psycopg2-binary`
- **Cache & In-Memory Store:** Redis
  - Usage: Caching provider API responses (TMDB, Open Library, etc.) to prevent rate-limiting, session storage, and background task queues if needed.
  - Client / Backend: `django-redis`

---

## 4. Background Processing & External API Clients

- **HTTP Client for External APIs:** `requests` or `httpx` (with connection pooling, timeouts, and error handling).
- **Asynchronous / Scheduled Tasks (Recommended):**
  - Celery or Django-Q with Redis as broker (for periodic syncs, heavy metadata imports, or scheduled monthly summaries).

---

## 5. Environment Variables Configuration (Specification)

The application relies on `.env` for secrets and configuration. When environment setup begins, the following variables will be defined in `.env.example` / `.env`:

```ini
# --- Django Core ---
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# --- PostgreSQL Database ---
DB_NAME=utrack
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# --- Redis Cache ---
REDIS_URL=redis://127.0.0.1:6379/1

# --- External Provider API Keys ---
TMDB_API_KEY=
TMDB_READ_ACCESS_TOKEN=
GOOGLE_BOOKS_API_KEY=
COMIC_VINE_API_KEY=
IGDB_CLIENT_ID=
IGDB_CLIENT_SECRET=
RAWG_API_KEY=
BGG_API_TOKEN=
```

---

## 6. Testing & Quality Assurance

- **Test Runner:** Django `test` / `pytest-django`
- **Linting & Formatting:** `ruff` or `flake8` + `black`
