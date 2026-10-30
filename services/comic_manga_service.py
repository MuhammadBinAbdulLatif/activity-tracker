import os
import json
import logging
import urllib.request
import urllib.parse
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ComicMangaService:
    """
    Unified client service for fetching metadata for Western Comics (Comic Vine API)
    and Eastern Manga / Manhwa / Light Novels (AniList GraphQL API & Jikan Fallback).
    """

    ANILIST_API_URL = os.getenv("ANILIST_API_URL", "https://graphql.anilist.co")
    COMIC_VINE_API_KEY = os.getenv("COMIC_VINE_API_KEY", "")
    USER_AGENT = "uTrack-MediaTracker/1.0"

    @classmethod
    def search_manga(cls, query: str, limit: int = 8) -> list:
        """
        Queries AniList GraphQL API for Manga / Manhwa / Light Novels.
        """
        if not query or not query.strip():
            return []

        cache_key = f"manga_search_{urllib.parse.quote(query.lower().strip())}_{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        graphql_query = """
        query ($search: String, $perPage: Int) {
            Page(perPage: $perPage) {
                media(search: $search, type: MANGA) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    format
                    status
                    description(asHtml: false)
                    startDate {
                        year
                    }
                    chapters
                    volumes
                    coverImage {
                        extraLarge
                        large
                    }
                    staff(perPage: 3) {
                        edges {
                            role
                            node {
                                name {
                                    full
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        payload = json.dumps({
            "query": graphql_query,
            "variables": {
                "search": query.strip(),
                "perPage": limit
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            cls.ANILIST_API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": cls.USER_AGENT
            }
        )

        results = []
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode("utf-8"))
                media_list = data.get("data", {}).get("Page", {}).get("media", [])
                for item in media_list:
                    title_obj = item.get("title", {})
                    title = title_obj.get("english") or title_obj.get("romaji") or title_obj.get("native") or "Unknown Manga"
                    original_title = title_obj.get("native") or title_obj.get("romaji") or ""

                    # Parse author/artist from staff edges
                    staff_edges = item.get("staff", {}).get("edges", [])
                    authors = []
                    artists = []
                    for edge in staff_edges:
                        role = (edge.get("role") or "").lower()
                        name = edge.get("node", {}).get("name", {}).get("full")
                        if name:
                            if "story" in role or "original" in role or "author" in role:
                                authors.append(name)
                            elif "art" in role or "illustrat" in role:
                                artists.append(name)
                            else:
                                authors.append(name)

                    author_str = ", ".join(authors[:2]) if authors else "Unknown Mangaka"
                    artist_str = ", ".join(artists[:2]) if artists else ""

                    cover_img = item.get("coverImage", {})
                    cover_url = cover_img.get("extraLarge") or cover_img.get("large") or ""

                    raw_desc = item.get("description") or ""
                    # Basic sanitization of description tags
                    clean_desc = raw_desc.replace("<br>", "\n").replace("<i>", "").replace("</i>", "").replace("<b>", "").replace("</b>", "")

                    format_type = item.get("format", "MANGA")
                    item_type = "LIGHT_NOVEL" if format_type == "NOVEL" else "MANGA"

                    results.append({
                        "external_id": f"anilist-{item.get('id')}",
                        "title": title,
                        "original_title": original_title if original_title != title else "",
                        "item_type": item_type,
                        "creator_author": author_str,
                        "artist": artist_str,
                        "publisher": "Various",
                        "start_year": item.get("startDate", {}).get("year"),
                        "total_chapters": item.get("chapters") or 0,
                        "total_volumes": item.get("volumes") or 0,
                        "cover_url": cover_url,
                        "description": clean_desc[:800],
                        "source": "AniList"
                    })
        except Exception as e:
            logger.warning(f"Error fetching from AniList API: {e}")

        # Cache results for 1 hour
        cache.set(cache_key, results, 3600)
        return results

    @classmethod
    def search_comics(cls, query: str, limit: int = 8) -> list:
        """
        Queries Comic Vine API for Western Comics & Graphic Novels.
        """
        if not query or not query.strip():
            return []

        cache_key = f"comic_search_{urllib.parse.quote(query.lower().strip())}_{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        results = []
        if cls.COMIC_VINE_API_KEY:
            encoded_query = urllib.parse.quote(query.strip())
            url = (
                f"https://comicvine.gamespot.com/api/volumes/?"
                f"api_key={cls.COMIC_VINE_API_KEY}&format=json&"
                f"filter=name:{encoded_query}&limit={limit}"
            )
            req = urllib.request.Request(
                url,
                headers={"User-Agent": cls.USER_AGENT}
            )
            try:
                with urllib.request.urlopen(req, timeout=8) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    raw_items = data.get("results", [])
                    for item in raw_items:
                        title = item.get("name") or "Unknown Comic"
                        publisher_obj = item.get("publisher") or {}
                        publisher = publisher_obj.get("name") or "Indie / Unknown"
                        start_year = item.get("start_year")
                        try:
                            start_year = int(start_year) if start_year else None
                        except (ValueError, TypeError):
                            start_year = None

                        image_obj = item.get("image") or {}
                        cover_url = image_obj.get("super_url") or image_obj.get("medium_url") or ""

                        count_of_issues = item.get("count_of_issues") or 0
                        deck = item.get("deck") or ""

                        results.append({
                            "external_id": f"comicvine-{item.get('id')}",
                            "title": title,
                            "original_title": "",
                            "item_type": "COMIC",
                            "creator_author": "Various Writers",
                            "artist": "Various Artists",
                            "publisher": publisher,
                            "start_year": start_year,
                            "total_chapters": count_of_issues,
                            "total_volumes": 1 if count_of_issues > 0 else 0,
                            "cover_url": cover_url,
                            "description": deck[:800],
                            "source": "Comic Vine"
                        })
            except Exception as e:
                logger.warning(f"Error querying Comic Vine API: {e}")

        cache.set(cache_key, results, 3600)
        return results

    @classmethod
    def search_all(cls, query: str, category_filter: str = "ALL", limit: int = 10) -> list:
        """
        Searches across Comics and Manga depending on filter ('ALL', 'COMIC', 'MANGA').
        """
        category_filter = (category_filter or "ALL").upper()

        if category_filter == "COMIC":
            return cls.search_comics(query, limit=limit)
        elif category_filter in ["MANGA", "LIGHT_NOVEL"]:
            return cls.search_manga(query, limit=limit)
        else:
            # Combined search
            manga_results = cls.search_manga(query, limit=limit // 2 + 1)
            comic_results = cls.search_comics(query, limit=limit // 2 + 1)
            # Interleave results
            combined = []
            max_len = max(len(manga_results), len(comic_results))
            for i in range(max_len):
                if i < len(manga_results):
                    combined.append(manga_results[i])
                if i < len(comic_results):
                    combined.append(comic_results[i])
            return combined[:limit]
