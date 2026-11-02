import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Simple in-memory cache with TTL (seconds)
_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 600


class BoardGameService:
    """
    Service client for BoardGameGeek (BGG) XML API2.
    Provides live title search and deep metadata enrichment
    (player counts, playing times, designers, mechanics, BGG community rating, and rankings).
    """

    BASE_URL = "https://boardgamegeek.com/xmlapi2"

    @classmethod
    def search(cls, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search BGG for board games matching the query.
        Returns a list of dicts with basic metadata: external_id, title, year_published.
        """
        if not query or not query.strip():
            return []

        query_str = query.strip()
        cache_key = f"bgg_search_{query_str.lower()}"
        cached = cls._get_from_cache(cache_key)
        if cached is not None:
            return cached[:limit]

        url = f"{cls.BASE_URL}/search?query={urllib.parse.quote(query_str)}&type=boardgame"
        xml_content = cls._fetch_xml(url)
        if not xml_content:
            return []

        results: List[Dict[str, Any]] = []
        try:
            root = ET.fromstring(xml_content)
            for item in root.findall("item"):
                bgg_id = item.get("id")
                if not bgg_id:
                    continue

                # Primary name
                name_elem = item.find("name")
                title = name_elem.get("value") if name_elem is not None else "Untitled Game"

                # Year published
                year_elem = item.find("yearpublished")
                year_published: Optional[int] = None
                if year_elem is not None and year_elem.get("value"):
                    try:
                        year_published = int(year_elem.get("value"))
                    except (ValueError, TypeError):
                        year_published = None

                results.append({
                    "external_id": f"bgg-{bgg_id}",
                    "id": bgg_id,
                    "title": title,
                    "year_published": year_published,
                })

                if len(results) >= limit:
                    break
        except ET.ParseError as e:
            logger.warning("Failed to parse BGG search XML: %s", e)
            return []

        cls._set_cache(cache_key, results)
        return results

    @classmethod
    def get_details(cls, bgg_id: str) -> Dict[str, Any]:
        """
        Fetch rich metadata for a single board game from BGG XML API2.
        Accepts either 'bgg-174430' or '174430'.
        Handles HTTP 202 queued response with a single retry.
        """
        raw_id = bgg_id.replace("bgg-", "").strip()
        if not raw_id:
            return {}

        cache_key = f"bgg_details_{raw_id}"
        cached = cls._get_from_cache(cache_key)
        if cached is not None:
            return cached

        url = f"{cls.BASE_URL}/thing?id={urllib.parse.quote(raw_id)}&stats=1"
        xml_content = cls._fetch_xml(url, allow_retry_on_202=True)
        if not xml_content:
            return {}

        try:
            root = ET.fromstring(xml_content)
            item = root.find("item")
            if item is None:
                return {}

            # Primary Title
            title = "Untitled Game"
            for name in item.findall("name"):
                if name.get("type") == "primary":
                    title = name.get("value") or title
                    break
            else:
                first_name = item.find("name")
                if first_name is not None and first_name.get("value"):
                    title = first_name.get("value")

            # Cover Image & Thumbnail
            image_elem = item.find("image")
            thumb_elem = item.find("thumbnail")
            cover_url = (image_elem.text if image_elem is not None and image_elem.text else "") or \
                        (thumb_elem.text if thumb_elem is not None and thumb_elem.text else "")

            # Description (BGG wraps description with HTML encoded entities or raw text)
            desc_elem = item.find("description")
            description = desc_elem.text if desc_elem is not None and desc_elem.text else ""

            # Year published
            year_elem = item.find("yearpublished")
            year_published = None
            if year_elem is not None and year_elem.get("value"):
                try:
                    year_published = int(year_elem.get("value"))
                except (ValueError, TypeError):
                    pass

            # Min / Max Players
            min_players_elem = item.find("minplayers")
            max_players_elem = item.find("maxplayers")
            min_players = int(min_players_elem.get("value")) if min_players_elem is not None and min_players_elem.get("value") else None
            max_players = int(max_players_elem.get("value")) if max_players_elem is not None and max_players_elem.get("value") else None

            # Min / Max Playtime
            min_play_elem = item.find("minplaytime")
            max_play_elem = item.find("maxplaytime")
            playtime_elem = item.find("playingtime")

            min_playtime = int(min_play_elem.get("value")) if min_play_elem is not None and min_play_elem.get("value") else None
            max_playtime = int(max_play_elem.get("value")) if max_play_elem is not None and max_play_elem.get("value") else None
            if min_playtime is None and playtime_elem is not None and playtime_elem.get("value"):
                try:
                    min_playtime = int(playtime_elem.get("value"))
                except (ValueError, TypeError):
                    pass
            if max_playtime is None:
                max_playtime = min_playtime

            # Links: designers, publishers, categories, mechanics
            designers = []
            publishers = []
            categories = []
            mechanics = []

            for link in item.findall("link"):
                link_type = link.get("type")
                value = link.get("value", "")
                if not value:
                    continue

                if link_type == "boardgamedesigner":
                    designers.append(value)
                elif link_type == "boardgamepublisher":
                    publishers.append(value)
                elif link_type == "boardgamecategory":
                    categories.append(value)
                elif link_type == "boardgamemechanic":
                    mechanics.append(value)

            # Statistics: Rating & Rank
            bgg_rating = None
            bgg_rank = None
            stats = item.find("statistics")
            if stats is not None:
                ratings = stats.find("ratings")
                if ratings is not None:
                    avg_elem = ratings.find("average")
                    if avg_elem is not None and avg_elem.get("value"):
                        try:
                            bgg_rating = round(float(avg_elem.get("value")), 2)
                        except (ValueError, TypeError):
                            pass

                    ranks = ratings.find("ranks")
                    if ranks is not None:
                        for r in ranks.findall("rank"):
                            if r.get("name") == "boardgame":
                                rank_val = r.get("value")
                                if rank_val and rank_val.isdigit():
                                    bgg_rank = int(rank_val)
                                break

            details = {
                "external_id": f"bgg-{raw_id}",
                "title": title,
                "cover_url": cover_url,
                "description": description,
                "year_published": year_published,
                "min_players": min_players,
                "max_players": max_players,
                "min_playtime": min_playtime,
                "max_playtime": max_playtime,
                "designers": ", ".join(designers[:5]),
                "publishers": ", ".join(publishers[:3]),
                "categories": ", ".join(categories[:5]),
                "mechanics": ", ".join(mechanics[:5]),
                "bgg_rating": bgg_rating,
                "bgg_rank": bgg_rank,
            }

            cls._set_cache(cache_key, details)
            return details

        except ET.ParseError as e:
            logger.warning("Failed to parse BGG thing XML for ID %s: %s", raw_id, e)
            return {}

    # ------------------------------------------------------------------ #
    # Internal HTTP and Cache Utilities
    # ------------------------------------------------------------------ #

    @classmethod
    def _fetch_xml(cls, url: str, allow_retry_on_202: bool = False) -> Optional[str]:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "uTrack/1.0 (Life & Media Chronicle; Python/urllib)",
                "Accept": "application/xml, text/xml",
            }
        )

        for attempt in range(2 if allow_retry_on_202 else 1):
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    status = getattr(resp, "status", 200)
                    if status == 202:
                        if allow_retry_on_202 and attempt == 0:
                            time.sleep(2)
                            continue
                        return None
                    return resp.read().decode("utf-8", errors="replace")
            except Exception as e:
                logger.warning("BGG API request failed for %s: %s", url, e)
                return None
        return None

    @classmethod
    def _get_from_cache(cls, key: str) -> Optional[Any]:
        if key in _CACHE:
            entry = _CACHE[key]
            if time.time() - entry["timestamp"] < CACHE_TTL:
                return entry["data"]
            del _CACHE[key]
        return None

    @classmethod
    def _set_cache(cls, key: str, data: Any):
        _CACHE[key] = {
            "timestamp": time.time(),
            "data": data,
        }
