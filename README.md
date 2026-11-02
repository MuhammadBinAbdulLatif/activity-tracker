# uTrack — Life & Media Chronicle

> **"Help the user remember what they did, understand how they spend their life, and reclaim a sense of personal accomplishment."**

**uTrack** is a modern, unified life and media tracking web application designed to turn fragmented daily consumption into a coherent personal chronicle. Instead of scattering your media across dozens of disconnected platforms (Goodreads, Trakt, Steam, Letterboxd, Spotify, Audible, AniList), uTrack brings cinema, serialized television, books, audiobooks, comics, manga, video games, and tabletop gaming into a single, cohesive dashboard with automated open-metadata enrichment and high-contrast temporal insights.

---

## 🌟 Key Features

### 🎬 Movies & Television
* **TMDB Integration:** Live search with instant retrieval of official posters, synopses, directors, casts, runtimes, and genres.
* **Watch Tracking:** One-click transition between *Currently Watching*, *Watchlist*, and *Completed / Watched History*.
* **Custom Titles:** Support for custom indie films, unlisted titles, or home videos with custom poster uploads.

### 📚 Books & Literature
* **Open Library & Google Books API:** Effortless lookup by title, author, or ISBN.
* **Reading Progress:** Real-time page progression, percent tracking, reading speed estimates, and start/finish dates.

### 🎧 Audiobooks
* **Multi-catalog Lookup:** Integration with Open Library, iTunes Search, and LibriVox.
* **Audio Session Logs:** Track listening sessions, narrator details, speed multiplier preferences, and total duration.

### 💥 Comics & Manga
* **Multi-type Categorization:** Track Western Comics, Japanese Manga, and Light Novels.
* **Dual Steppers:** Direct quick-steppers for both chapter increments (`+1 Ch`) and volume increments (`+1 Vol`).

### 🎮 Video Games
* **RAWG & IGDB Metadata:** Auto-fills cover art, platforms, developers, genres, and release years.
* **Daily Playtime Logging:** Clean, prominent **`+30m`** and **`-30m`** stepper buttons designed for effortless daily tracking.
* **Milestone Announcer:** One-click **"Mark as Completed"** action without arbitrary percentage friction.
* **Custom Game Creator:** Add custom games with live drag-and-drop cover preview support.

### 📊 Retrospectives & Life Heatmap
* **GitHub-Style Contribution Heatmap:** 52-week activity calendar grid with calibrated emerald intensity tiers reflecting daily engagement.
* **At-a-Glance Metrics:** Track your active streaks, total hours logged, items completed, and category distributions.

---

## 🎨 Design Philosophy

uTrack follows the modern minimalist **shadcn/ui** aesthetic:
* **Dark High-Tech Foundation:** Deep blacks (`#09090b`), subtle zinc slate surfaces (`#18181b`), and clean hairline borders (`#27272a`).
* **Controlled Semantic Accents:** Vivid emerald green (`#10b981`) for active accomplishments and streaks; bright cyan for gaming sessions; warm amber for films and ratings.
* **Zero-Friction UX:** Direct inline actions, live image upload previews, HTMX search indicators, and Sonner-style floating bottom-right toasts.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Framework** | Python 3.12+ / [Django 5.x](https://www.djangoproject.com/) |
| **Frontend & UI** | [Tailwind CSS](https://tailwindcss.com/) (CDN), [HTMX](https://htmx.org/) |
| **Database** | SQLite (Development) / PostgreSQL (Production) |
| **External APIs** | TMDB, RAWG, IGDB (Twitch OAuth2), Open Library, BoardGameGeek XML API2 |
| **Media & Assets** | Django Storages / Local Media Storage with ImageField handlers |

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.12+ installed
* Git

### 2. Clone the Repository
```bash
git clone https://github.com/MuhammadBinAbdulLatif/activity-tracker.git
cd activity-tracker
```

### 3. Create & Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
pip install python-dotenv requests pillow
```

### 5. Configure Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secure-django-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost

# External API Keys (Optional but recommended for auto-enrichment)
RAWG_API_KEY=your_rawg_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here
```

### 6. Run Migrations & Start the Development Server
```bash
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Tests

The test suite includes comprehensive tests for models, services, and view layers:

```bash
# Run all tests across the application
python manage.py test

# Run tests for a specific app (e.g. video games)
python manage.py test games --verbosity=2
```

---

## 📂 Project Architecture

```text
utrack/
├── accounts/          # User authentication, registration, recovery, & profiles
├── dashboard/         # Main chronicle dashboard, activity heatmap, sidebar shell
├── movies/            # Film tracking, TMDB integration, watchlist & history
├── series/            # Serialized television, seasons, & episode logs
├── books/             # Literature, Open Library lookup, page tracking
├── audiobooks/        # Audiobook sessions, duration, & narrator metadata
├── comics/            # Manga, graphic novels, light novels, chapter/volume steppers
├── games/             # Video games tracking, RAWG/IGDB service, daily playtime steppers
├── boardgames/        # Tabletop & board games engine (BoardGameGeek API2)
├── services/          # Third-party metadata adapters (TMDB, RAWG, OpenLibrary, BGG)
├── specs/             # Living design system, architecture blueprints, & roadmaps
├── utrack/            # Core Django project settings and root routing
└── manage.py          # Django management script
```

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
