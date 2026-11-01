import os
import json
import hashlib
import time
import logging
import urllib.request
import urllib.parse

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Simple module-level in-memory cache: {key: (timestamp, data)}
# --------------------------------------------------------------------------- #
_cache: dict = {}
_CACHE_TTL = 300  # seconds


def _cache_get(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry[0]) < _CACHE_TTL:
        return entry[1]
    return None


def _cache_set(key: str, value) -> None:
    _cache[key] = (time.time(), value)


def _cache_key(prefix: str, query: str) -> str:
    digest = hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]
    return f"{prefix}_{digest}"


class VideoGameService:
    """
    Unified provider client for Video Game metadata.

    Primary source  : RAWG Video Games Database (https://rawg.io/apidocs)
    Fallback source : IGDB API via Twitch OAuth2  (https://api.igdb.com)

    Both API keys are read from environment variables. If keys are absent the
    respective provider is silently skipped.  All network errors return []
    and are never re-raised to the view layer.
    """

    RAWG_BASE = "https://api.rawg.io/api"
    IGDB_BASE = "https://api.igdb.com/v4"
    TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    USER_AGENT = "uTrack-MediaTracker/1.0"
    TIMEOUT = 8

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    @classmethod
    def search(cls, query: str, limit: int = 10) -> list[dict]:
        """
        Search for video games by title.
        Returns a list of normalized game dicts (up to `limit`).
        """
        if not query or not query.strip():
            return []

        cache_key = _cache_key("vg_search", f"{query}_{limit}")
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached

        results = cls._search_rawg(query, limit)
        if not results:
            results = cls._search_igdb(query, limit)

        _cache_set(cache_key, results)
        return results

    # ------------------------------------------------------------------ #
    # RAWG Provider
    # ------------------------------------------------------------------ #

    @classmethod
    def _rawg_key(cls) -> str:
        return os.getenv("RAWG_API_KEY", "").strip()

    @classmethod
    def _search_rawg(cls, query: str, limit: int) -> list[dict]:
        key = cls._rawg_key()
        if not key:
            logger.info("RAWG_API_KEY not set; skipping RAWG provider.")
            return []

        params = urllib.parse.urlencode({
            "search": query.strip(),
            "key": key,
            "page_size": limit,
            "search_exact": False,
        })
        url = f"{cls.RAWG_BASE}/games?{params}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": cls.USER_AGENT})
            with urllib.request.urlopen(req, timeout=cls.TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                games = data.get("results", [])
                return [cls._normalize_rawg(g) for g in games if g.get("name")]
        except Exception as exc:
            logger.warning("RAWG search failed for %r: %s", query, exc)
            return []

    @classmethod
    def _normalize_rawg(cls, g: dict) -> dict:
        platforms = g.get("platforms") or []
        platform_names = ", ".join(
            p["platform"]["name"] for p in platforms if p.get("platform", {}).get("name")
        )

        genres = g.get("genres") or []
        genre_names = ", ".join(gen["name"] for gen in genres if gen.get("name"))

        # Release year from released date string "YYYY-MM-DD"
        released = g.get("released") or ""
        release_year = int(released[:4]) if released and len(released) >= 4 else None

        # Cover image
        cover_url = g.get("background_image") or ""

        return {
            "external_id": f"rawg-{g.get('id', '')}",
            "source": "rawg",
            "title": g.get("name", ""),
            "cover_url": cover_url,
            "description": "",          # not available in list endpoint; fetched on detail
            "release_year": release_year,
            "developers": "",           # not available in list endpoint
            "publishers": "",
            "genres": genre_names,
            "platforms": platform_names,
            "metacritic_score": g.get("metacritic"),
        }

    @classmethod
    def get_details_rawg(cls, rawg_id: str) -> dict:
        """
        Fetch full game detail from RAWG by numeric id or slug.
        Returns normalized dict or {} on failure.
        """
        key = cls._rawg_key()
        if not key:
            return {}

        cache_key = _cache_key("vg_detail_rawg", rawg_id)
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached

        url = f"{cls.RAWG_BASE}/games/{rawg_id}?key={key}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": cls.USER_AGENT})
            with urllib.request.urlopen(req, timeout=cls.TIMEOUT) as resp:
                g = json.loads(resp.read().decode("utf-8"))

            platforms = g.get("platforms") or []
            platform_names = ", ".join(
                p["platform"]["name"] for p in platforms if p.get("platform", {}).get("name")
            )

            genres = g.get("genres") or []
            genre_names = ", ".join(gen["name"] for gen in genres if gen.get("name"))

            developers_list = g.get("developers") or []
            developers = ", ".join(d["name"] for d in developers_list if d.get("name"))

            publishers_list = g.get("publishers") or []
            publishers = ", ".join(p["name"] for p in publishers_list if p.get("name"))

            released = g.get("released") or ""
            release_year = int(released[:4]) if released and len(released) >= 4 else None

            # Strip HTML tags from description_raw
            description = g.get("description_raw") or g.get("description") or ""
            if "<" in description:
                import re
                description = re.sub(r"<[^>]+>", "", description)

            result = {
                "external_id": f"rawg-{g.get('id', '')}",
                "source": "rawg",
                "title": g.get("name", ""),
                "cover_url": g.get("background_image") or "",
                "description": description.strip(),
                "release_year": release_year,
                "developers": developers,
                "publishers": publishers,
                "genres": genre_names,
                "platforms": platform_names,
                "metacritic_score": g.get("metacritic"),
            }
            _cache_set(cache_key, result)
            return result
        except Exception as exc:
            logger.warning("RAWG detail fetch failed for %r: %s", rawg_id, exc)
            return {}

    # ------------------------------------------------------------------ #
    # IGDB Provider (Twitch OAuth2)
    # ------------------------------------------------------------------ #

    _igdb_token: str | None = None
    _igdb_token_expiry: float = 0.0

    @classmethod
    def _igdb_client_id(cls) -> str:
        return os.getenv("IGDB_CLIENT_ID", "").strip()

    @classmethod
    def _igdb_client_secret(cls) -> str:
        return os.getenv("IGDB_CLIENT_SECRET", "").strip()

    @classmethod
    def _get_igdb_token(cls) -> str:
        """Fetch or return cached Twitch OAuth2 Bearer token for IGDB."""
        if cls._igdb_token and time.time() < cls._igdb_token_expiry:
            return cls._igdb_token

        client_id = cls._igdb_client_id()
        client_secret = cls._igdb_client_secret()
        if not client_id or not client_secret:
            return ""

        params = urllib.parse.urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        })
        url = f"{cls.TWITCH_TOKEN_URL}?{params}"

        try:
            req = urllib.request.Request(url, method="POST", headers={"User-Agent": cls.USER_AGENT})
            with urllib.request.urlopen(req, timeout=cls.TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cls._igdb_token = data.get("access_token", "")
                expires_in = data.get("expires_in", 3600)
                cls._igdb_token_expiry = time.time() + expires_in - 60  # 60s safety margin
                return cls._igdb_token
        except Exception as exc:
            logger.warning("IGDB token fetch failed: %s", exc)
            return ""

    @classmethod
    def _search_igdb(cls, query: str, limit: int) -> list[dict]:
        client_id = cls._igdb_client_id()
        token = cls._get_igdb_token()
        if not client_id or not token:
            logger.info("IGDB credentials not set; skipping IGDB provider.")
            return []

        body = (
            f'search "{query.strip()}"; '
            f"fields name,cover.url,first_release_date,genres.name,"
            f"platforms.name,involved_companies.company.name,involved_companies.developer,"
            f"involved_companies.publisher,summary; "
            f"limit {limit};"
        ).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{cls.IGDB_BASE}/games",
                data=body,
                headers={
                    "Client-ID": client_id,
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "text/plain",
                    "User-Agent": cls.USER_AGENT,
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=cls.TIMEOUT) as resp:
                games = json.loads(resp.read().decode("utf-8"))
                return [cls._normalize_igdb(g) for g in games if g.get("name")]
        except Exception as exc:
            logger.warning("IGDB search failed for %r: %s", query, exc)
            return []

    @classmethod
    def _normalize_igdb(cls, g: dict) -> dict:
        # Timestamp → year
        release_ts = g.get("first_release_date")
        release_year = None
        if release_ts:
            import datetime
            try:
                release_year = datetime.datetime.utcfromtimestamp(release_ts).year
            except Exception:
                pass

        genres = g.get("genres") or []
        genre_names = ", ".join(gen["name"] for gen in genres if gen.get("name"))

        platforms = g.get("platforms") or []
        platform_names = ", ".join(p["name"] for p in platforms if p.get("name"))

        involved = g.get("involved_companies") or []
        developers = ", ".join(
            ic["company"]["name"] for ic in involved
            if ic.get("developer") and ic.get("company", {}).get("name")
        )
        publishers = ", ".join(
            ic["company"]["name"] for ic in involved
            if ic.get("publisher") and ic.get("company", {}).get("name")
        )

        cover = g.get("cover") or {}
        cover_url = cover.get("url", "")
        if cover_url.startswith("//"):
            cover_url = "https:" + cover_url
        # Upgrade to high-res
        cover_url = cover_url.replace("t_thumb", "t_cover_big")

        return {
            "external_id": f"igdb-{g.get('id', '')}",
            "source": "igdb",
            "title": g.get("name", ""),
            "cover_url": cover_url,
            "description": g.get("summary", ""),
            "release_year": release_year,
            "developers": developers,
            "publishers": publishers,
            "genres": genre_names,
            "platforms": platform_names,
            "metacritic_score": None,
        }
