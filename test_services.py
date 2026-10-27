#!/usr/bin/env python
"""
Service & Open Provider Integration Health Checker for uTrack.

Tests all configured endpoints and API keys without leaking secrets.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path


def load_env(env_path: Path):
    """Loads .env into os.environ without third-party dependencies."""
    if not env_path.exists():
        print(f"[!] Warning: {env_path} not found.")
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()


def mask(val: str) -> str:
    if not val:
        return "<EMPTY>"
    if len(val) <= 8:
        return "***"
    return f"{val[:3]}...{val[-4:]}"


def test_tmdb():
    api_key = os.getenv("TMDB_API_KEY")
    token = os.getenv("TMDB_READ_ACCESS_TOKEN")
    print(f"\n[1/6] Testing Movies & Series (TMDB API)...")
    print(f"      API Key: {mask(api_key)} | Bearer Token: {mask(token)}")

    if not api_key and not token:
        print("      [-] SKIPPED: TMDB credentials not provided.")
        return False

    url = "https://api.themoviedb.org/3/search/movie?query=Inception&page=1"
    headers = {"User-Agent": "uTrack-HealthCheck/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif api_key:
        url += f"&api_key={api_key}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            results = data.get("results", [])
            if results:
                title = results[0].get("title")
                year = results[0].get("release_date", "")[:4]
                print(f"      [+] SUCCESS: Found '{title}' ({year}) | Total results: {data.get('total_results')}")
                return True
            else:
                print("      [!] Connected, but no results returned.")
                return True
    except Exception as e:
        print(f"      [-] FAILED: {e}")
        return False


def test_books():
    print(f"\n[2/6] Testing Books & Literature (Open Library & Google Books)...")
    google_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    print(f"      Google Books Key: {mask(google_key)}")

    # Test Open Library (Primary open book catalog)
    ol_url = "https://openlibrary.org/search.json?title=Dune&limit=1"
    ol_req = urllib.request.Request(ol_url, headers={"User-Agent": "uTrack-HealthCheck/1.0"})
    ol_ok = False
    try:
        with urllib.request.urlopen(ol_req, timeout=10) as response:
            data = json.loads(response.read().decode())
            docs = data.get("docs", [])
            if docs:
                title = docs[0].get("title")
                authors = ", ".join(docs[0].get("author_name", ["Unknown"]))
                print(f"      [+] Open Library: Found '{title}' by {authors}")
                ol_ok = True
    except Exception as e:
        print(f"      [-] Open Library note: {e}")

    # Test Google Books (Secondary fallback)
    gb_ok = False
    try:
        gb_url = "https://www.googleapis.com/books/v1/volumes?q=Dune"
        if google_key:
            gb_url += f"&key={google_key}"
        gb_req = urllib.request.Request(gb_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(gb_req, timeout=10) as response:
            data = json.loads(response.read().decode())
            items = data.get("items", [])
            if items:
                title = items[0]["volumeInfo"].get("title")
                print(f"      [+] Google Books API: Found '{title}'")
                gb_ok = True
    except Exception as e:
        print(f"      [!] Google Books API note: {e}")

    return ol_ok or gb_ok


def test_comic_vine():
    api_key = os.getenv("COMIC_VINE_API_KEY")
    print(f"\n[3/6] Testing Comics & Graphic Novels (Comic Vine API)...")
    print(f"      API Key: {mask(api_key)}")

    if not api_key:
        print("      [-] SKIPPED: Comic Vine API key not provided.")
        return False

    url = f"https://comicvine.gamespot.com/api/volumes/?api_key={api_key}&format=json&filter=name:Spider-Man&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "uTrack-App/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            status = data.get("error")
            results = data.get("results", [])
            if status == "OK" and results:
                name = results[0].get("name")
                year = results[0].get("start_year")
                print(f"      [+] SUCCESS: Found '{name}' ({year})")
                return True
            elif status == "OK":
                print("      [+] SUCCESS: Connected to Comic Vine.")
                return True
            else:
                print(f"      [-] Response Status: {status}")
                return False
    except Exception as e:
        print(f"      [-] FAILED: {e}")
        return False


def test_anilist():
    endpoint = os.getenv("ANILIST_API_URL", "https://graphql.anilist.co")
    print(f"\n[4/6] Testing Anime & Manga (AniList GraphQL API)...")
    print(f"      Endpoint: {endpoint}")

    query = """
    query {
        Media(search: "Attack on Titan", type: ANIME) {
            id
            title { english romaji }
            episodes
        }
    }
    """
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "uTrack-HealthCheck/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            media = data.get("data", {}).get("Media", {})
            title = media.get("title", {}).get("english") or media.get("title", {}).get("romaji")
            episodes = media.get("episodes")
            print(f"      [+] SUCCESS: Found '{title}' ({episodes} episodes)")
            return True
    except Exception as e:
        print(f"      [-] FAILED: {e}")
        return False


def test_itunes_audiobooks():
    endpoint = os.getenv("ITUNES_SEARCH_API_URL", "https://itunes.apple.com/search")
    print(f"\n[5/6] Testing Audiobooks (iTunes Search API)...")
    print(f"      Endpoint: {endpoint}")

    term = urllib.parse.quote("Atomic Habits")
    url = f"{endpoint}?term={term}&entity=audiobook&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            results = data.get("results", [])
            if results:
                book = results[0]
                name = book.get("collectionName") or book.get("trackName")
                author = book.get("artistName")
                print(f"      [+] SUCCESS: Found '{name}' by {author}")
                return True
            else:
                print("      [!] Connected, but no results found.")
                return True
    except Exception as e:
        print(f"      [-] FAILED: {e}")
        return False


def test_redis():
    redis_url = os.getenv("REDIS_URL")
    print(f"\n[6/6] Testing Redis Cache...")
    print(f"      REDIS_URL: {mask(redis_url)}")

    try:
        import redis
        client = redis.from_url(redis_url, socket_timeout=3)
        client.ping()
        print("      [+] SUCCESS: Redis server responded to PING!")
        return True
    except ImportError:
        print("      [!] Note: Python 'redis' library not installed in this environment; skipping socket ping.")
        return None
    except Exception as e:
        print(f"      [!] Note: Redis server ping failed ({e}). App will fall back to local LocMemCache.")
        return False


def main():
    print("=" * 70)
    print(" uTrack Service & External Provider Integration Health Check")
    print("=" * 70)

    env_path = Path(__file__).resolve().parent / ".env"
    load_env(env_path)

    results = {}
    results["TMDB (Movies/Series)"] = test_tmdb()
    results["Books & Literature (Open Library / Google Books)"] = test_books()
    results["Comic Vine (Comics)"] = test_comic_vine()
    results["AniList (Anime/Manga)"] = test_anilist()
    results["iTunes (Audiobooks)"] = test_itunes_audiobooks()
    results["Redis Cache"] = test_redis()

    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    for service, status in results.items():
        if status is True:
            badge = "[PASS]"
        elif status is None:
            badge = "[OPTIONAL / SKIPPED]"
        else:
            badge = "[OPTIONAL / FALLBACK]"
        print(f" {badge:<28} {service}")
    print("=" * 70)


if __name__ == "__main__":
    main()
