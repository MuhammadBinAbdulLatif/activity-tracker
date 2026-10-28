# Requirements: Tool Gathering & Environment Configuration

> **Feature Directory:** `specs/tool_gathering/requirements.md`  
> **Status:** Draft / Active  

---

## 1. Overview & Objectives

Before building out external provider clients, search engines, and media sync pipelines, we must establish a complete registry of external database providers, services, credentials, and environment variables.

This specification serves as the authoritative inventory of:
1. All backing database and caching credentials (PostgreSQL and Redis).
2. All external open database providers for Movies, Series, Books, Audiobooks, Comics, and Anime/Manga.
3. The comprehensive `.env` template required for local and production deployment.

---

## 2. Infrastructure & Provider Catalog

### 2.1 Core Infrastructure
- **PostgreSQL Database:** Primary persistent store.
  - Required variables: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- **Redis In-Memory Cache:** Required for caching external API search queries and entity payloads to prevent rate limits and ensure sub-second UI search speeds.
  - Required variable: `REDIS_URL`.

### 2.2 Category-by-Category Open Providers

1. **Movies & TV Series:**
   - **Primary Provider:** The Movie Database (TMDB) API v3/v4.
   - **Data Provided:** Posters, backdrops, release date, runtime, cast, director, season/episode counts, overview.
   - **Auth Required:** Free Developer API Key & Read Access Token.
   - **Variables:** `TMDB_API_KEY`, `TMDB_READ_ACCESS_TOKEN`.

2. **Books & Literature:**
   - **Primary Provider:** Open Library REST API (Internet Archive) + Google Books API fallback.
   - **Data Provided:** ISBN, cover art, author name, page count, publication year, genres, description.
   - **Auth Required:** Open Library is open (no key required). Google Books optional API key for increased quotas.
   - **Variables:** `GOOGLE_BOOKS_API_KEY` (optional).

3. **Audiobooks:**
   - **Primary Provider:** iTunes Search API (Audiobook media type) + Open Library / LibriVox.
   - **Data Provided:** Narrator, author, high-res artwork, duration (milliseconds/minutes), release date.
   - **Auth Required:** iTunes Search API is open and public (no API key required). LibriVox is open public domain.
   - **Variables:** Optional Audnexus/Audible public endpoints.

4. **Comics & Graphic Novels:**
   - **Primary Provider:** Comic Vine API (by Gamespot) / Grand Comics Database (GCD).
   - **Data Provided:** Issue numbers, volume titles, cover art, publisher (Marvel, DC, Image, etc.), writers, illustrators.
   - **Auth Required:** Free Comic Vine API Key.
   - **Variables:** `COMIC_VINE_API_KEY`.

5. **Anime & Manga:**
   - **Primary Provider:** AniList GraphQL API v2 / Jikan (MyAnimeList open REST API).
   - **Data Provided:** Episodes, chapters, volumes, studio, cover image, banner image, airing status.
   - **Auth Required:** AniList GraphQL & Jikan are open and free (no API key required).
   - **Variables:** `ANILIST_API_ENDPOINT` (defaults to `https://graphql.anilist.co`).

6. **Video Games:**
   - **Primary Provider:** IGDB (Internet Game Database via Twitch Developer OAuth) / RAWG Video Games Database API.
   - **Data Provided:** Cover art, release dates, platforms (PC, PlayStation, Xbox, Switch), developers, genres, storyline, game modes.
   - **Auth Required:** Free Twitch Developer Client ID & Client Secret (for IGDB) or free RAWG API Key.
   - **Variables:** `IGDB_CLIENT_ID`, `IGDB_CLIENT_SECRET`, `RAWG_API_KEY`.

7. **Board Games:**
   - **Primary Provider:** BoardGameGeek (BGG) XML API2 (`https://boardgamegeek.com/xmlapi2/`).
   - **Data Provided:** Box thumbnail/cover art, player counts (min/max), playing time, age ratings, designers, mechanics, BGG community rank.
   - **Auth Required:** BGG XML API2 Bearer Token / Free Developer App Registration.
   - **Variables:** `BGG_API_TOKEN`, `BGG_API_URL` (defaults to `https://boardgamegeek.com/xmlapi2`).

---

## 3. Comprehensive `.env` Deliverable Requirements

A `.env` file must be generated at the project root containing:
- Full Django settings (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`).
- PostgreSQL configuration block.
- Redis configuration block.
- All provider keys, read tokens, and endpoint URLs grouped with descriptive comments.

---

## 4. Definition of Done (Acceptance Criteria)

- [x] Complete `.env` file created in workspace root with all required variables cleanly formatted.
- [x] Provider catalog and authentication requirements documented in `plan.md`.
- [x] Validation suite in `validation.md` specifies verification checks for reading the `.env` settings and testing service availability.
- [x] `.env` confirmed safely excluded by `.gitignore`.
