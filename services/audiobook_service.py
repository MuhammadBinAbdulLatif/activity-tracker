import urllib.request
import urllib.parse
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AudiobookService:
    """
    Client for querying the Audible Catalog API for authentic audiobook metadata,
    including exact narrator credits, exact audio runtime (in minutes),
    high-resolution product cover artwork, and audio sample streams.
    Falls back gracefully to iTunes API if Audible is unreachable.
    """
    AUDIBLE_BASE_URL = "https://api.audible.com/1.0/catalog/products"
    ITUNES_BASE_URL = "https://itunes.apple.com/search"

    def search_audiobooks(self, query: str, limit: int = 10) -> Dict[str, Any]:
        if not query or not query.strip():
            return {"results": []}

        # 1. Primary: Query Audible Catalog API
        audible_results = self._search_audible(query.strip(), limit=limit)
        if audible_results:
            return {"results": audible_results}

        # 2. Secondary Fallback: Query iTunes Search API
        itunes_results = self._search_itunes(query.strip(), limit=limit)
        return {"results": itunes_results}

    def _search_audible(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        params = {
            "keywords": query,
            "num_results": max(limit * 2, 10),
            "response_groups": "contributors,media,product_attrs,product_desc,sample",
        }
        url = f"{self.AUDIBLE_BASE_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/json",
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=7) as response:
                if response.status != 200:
                    return []
                data = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            logger.warning("Audible API search error: %s", e)
            return []

        results = []
        for p in data.get("products", []):
            asin = p.get("asin")
            title = p.get("title") or "Untitled Audiobook"
            
            # Authors list
            authors = [a.get("name") for a in p.get("authors", []) if a.get("name")]
            author_str = ", ".join(authors) if authors else "Author Unlisted"

            # Narrators list
            narrators = [n.get("name") for n in p.get("narrators", []) if n.get("name")]
            narrator_str = ", ".join(narrators) if narrators else "Narrator Unlisted"

            # Runtime in minutes
            runtime_mins = p.get("runtime_length_min") or 0

            # High-res image
            images = p.get("product_images", {}) or {}
            cover_url = images.get("500") or images.get("1024") or images.get("256") or ""

            # Release year
            release_date = p.get("release_date") or p.get("publication_datetime") or ""
            release_year = int(release_date[:4]) if len(release_date) >= 4 and release_date[:4].isdigit() else None

            sample_url = p.get("sample_url") or ""
            desc = p.get("publisher_summary") or p.get("merchandising_summary") or ""

            results.append({
                "external_id": str(asin) if asin else "",
                "title": title,
                "author": author_str,
                "narrator": narrator_str,
                "duration_minutes": runtime_mins,
                "cover_url": cover_url,
                "preview_audio_url": sample_url,
                "release_year": release_year,
                "genre": "Audiobook",
                "description": desc,
            })

        return results

    def _search_itunes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        params = {
            "term": query,
            "media": "audiobook",
            "limit": limit,
        }
        url = f"{self.ITUNES_BASE_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "uTrack/1.0 (AudiobookChronicle)"}
        )

        try:
            with urllib.request.urlopen(req, timeout=7) as response:
                if response.status != 200:
                    return []
                data = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            logger.warning("iTunes search error: %s", e)
            return []

        results = []
        for item in data.get("results", []):
            collection_id = item.get("collectionId")
            raw_title = item.get("collectionName") or "Untitled Audiobook"
            author = item.get("artistName") or "Unknown Author"
            desc = item.get("description", "")
            
            artwork_100 = item.get("artworkUrl100") or item.get("artworkUrl60") or ""
            artwork_high_res = artwork_100.replace("100x100bb.jpg", "600x600bb.jpg")

            release_date = item.get("releaseDate") or ""
            release_year = int(release_date[:4]) if len(release_date) >= 4 and release_date[:4].isdigit() else None

            results.append({
                "external_id": str(collection_id) if collection_id else "",
                "title": raw_title,
                "author": author,
                "narrator": "Narrator Unlisted",
                "duration_minutes": 0,
                "cover_url": artwork_high_res,
                "preview_audio_url": item.get("previewUrl") or "",
                "release_year": release_year,
                "genre": item.get("primaryGenreName") or "Audiobook",
                "description": desc,
            })

        return results

audiobook_service = AudiobookService()
