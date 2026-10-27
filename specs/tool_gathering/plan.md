# Technical Implementation Plan: Tool Gathering & Environment Setup

> **Feature Directory:** `specs/tool_gathering/plan.md`  
> **Status:** Completed & Closed  

---

## 1. Architectural Strategy

To make environment management clean, maintainable, and type-safe across both SQLite (current development fallback) and PostgreSQL/Redis (production & configured local):

1. **Environment Parser Library:**
   - Use `python-dotenv` or `environ` (or standard `os.environ` / `.env` loader) in `utrack/settings.py` so variables are loaded transparently.
2. **Graceful Database Fallback:**
   - If `DB_NAME` or PostgreSQL credentials are empty, cleanly fallback to SQLite (`db.sqlite3`) so local developer runs are never broken while keys are being gathered.
   - If PostgreSQL credentials are provided, activate the `django.db.backends.postgresql` connection.
3. **Graceful Cache Fallback:**
   - If `REDIS_URL` is set, configure `django_redis.cache.RedisCache` or `django.core.cache.backends.redis.RedisCache`.
   - If not set, fallback to `django.core.cache.backends.locmem.LocMemCache` for effortless offline development.
4. **Unified Provider Registry Config:**
   - Centralize provider API base URLs and API keys in a dedicated dictionary in `utrack/settings.py` (e.g. `MEDIA_PROVIDERS = {...}`).

---

## 2. Step-by-Step Execution Plan

### Step 1: Environment Template Generation
- Create root `.env` with comprehensive sections for Django Core, PostgreSQL, Redis, and External Providers.

### Step 2: Settings Integration
- Update `utrack/settings.py` to read from `.env` using standard Python `os.getenv()` with safe defaults and graceful SQLite/PostgreSQL switching.

### Step 3: Documentation
- Cross-reference with `specs/techstack.md` to ensure all dependencies (`psycopg2-binary`, `redis`, etc.) are documented.

### Step 4: Verification
- Execute environment verification tests to confirm that all required variables are recognized and validated.
