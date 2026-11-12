import logging
from typing import List, Dict, Any
from django.core.cache import cache

from services.tmdb import tmdb_service
from services.openlibrary import openlibrary_service
from services.videogame_service import VideoGameService

logger = logging.getLogger(__name__)

CACHE_TTL = 86400  # 24 hours

class RecommendationEngine:
    """
    Unified Cross-Media Recommendation Engine.
    Provides standard recommendation outputs across all media categories,
    with built-in deduplication against user's library and resilient caching.
    """

    @classmethod
    def get_movie_recommendations(cls, tmdb_id: str | int, user=None, limit: int = 6) -> List[Dict[str, Any]]:
        if not tmdb_id:
            return []

        cache_key = f"rec:movie:{tmdb_id}:{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cls._filter_user_library(cached, user, "movie")

        try:
            raw_results = tmdb_service.get_movie_recommendations(tmdb_id)
        except Exception as e:
            logger.warning("Error fetching movie recommendations for %s: %s", tmdb_id, e)
            raw_results = []

        recommendations = []
        for item in raw_results[:limit + 6]:
            poster_path = item.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
            release_date = item.get("release_date") or ""
            year = release_date[:4] if len(release_date) >= 4 else ""

            recommendations.append({
                "category": "movie",
                "external_id": str(item.get("id")),
                "title": item.get("title") or item.get("original_title") or "Untitled",
                "subtitle": f"Movie • {year}" if year else "Movie",
                "year": year,
                "poster_url": poster_url,
                "rating": round(float(item.get("vote_average", 0)), 1) if item.get("vote_average") else None,
                "overview": item.get("overview", ""),
            })

        cache.set(cache_key, recommendations, CACHE_TTL)
        return cls._filter_user_library(recommendations, user, "movie")[:limit]

    @classmethod
    def get_series_recommendations(cls, tmdb_id: str | int, user=None, limit: int = 6) -> List[Dict[str, Any]]:
        if not tmdb_id:
            return []

        cache_key = f"rec:series:{tmdb_id}:{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cls._filter_user_library(cached, user, "series")

        try:
            raw_results = tmdb_service.get_series_recommendations(tmdb_id)
        except Exception as e:
            logger.warning("Error fetching series recommendations for %s: %s", tmdb_id, e)
            raw_results = []

        recommendations = []
        for item in raw_results[:limit + 6]:
            poster_path = item.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
            air_date = item.get("first_air_date") or ""
            year = air_date[:4] if len(air_date) >= 4 else ""

            recommendations.append({
                "category": "series",
                "external_id": str(item.get("id")),
                "title": item.get("name") or item.get("original_name") or "Untitled",
                "subtitle": f"Series • {year}" if year else "Series",
                "year": year,
                "poster_url": poster_url,
                "rating": round(float(item.get("vote_average", 0)), 1) if item.get("vote_average") else None,
                "overview": item.get("overview", ""),
            })

        cache.set(cache_key, recommendations, CACHE_TTL)
        return cls._filter_user_library(recommendations, user, "series")[:limit]

    @classmethod
    def get_book_recommendations(cls, author: str = None, subject: str = None, current_title: str = None, user=None, limit: int = 6) -> List[Dict[str, Any]]:
        import hashlib
        clean_author = author.strip() if author else ""
        raw_key = f"{clean_author}:{current_title}:{limit}"
        hashed_key = hashlib.md5(raw_key.encode("utf-8")).hexdigest()
        cache_key = f"rec:book:{hashed_key}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cls._filter_user_library(cached, user, "book")

        try:
            raw_results = openlibrary_service.get_recommendations_for_book(
                author=clean_author,
                subject=subject,
                current_title=current_title,
                limit=limit + 6
            )
        except Exception as e:
            logger.warning("Error fetching book recommendations: %s", e)
            raw_results = []

        recommendations = []
        for item in raw_results:
            recommendations.append({
                "category": "book",
                "external_id": item.get("openlibrary_key", ""),
                "title": item.get("title", "Untitled"),
                "subtitle": item.get("author", "Book"),
                "year": item.get("publish_year") or "",
                "poster_url": item.get("cover_url", ""),
                "rating": None,
                "overview": f"Pages: {item.get('page_count', 'N/A')}" if item.get("page_count") else "",
            })

        cache.set(cache_key, recommendations, CACHE_TTL)
        return cls._filter_user_library(recommendations, user, "book")[:limit]

    @classmethod
    def get_game_recommendations(cls, game_title: str = None, genres: str = None, user=None, limit: int = 6) -> List[Dict[str, Any]]:
        """
        Discovers related games using fallback search for primary genre/keyword or developer.
        Safe against RAWG downtime with fast empty return or cached fallback.
        """
        if not game_title and not genres:
            return []

        cache_key = f"rec:game:{game_title}:{genres}:{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cls._filter_user_library(cached, user, "game")

        # In case external video game API is unavailable, return gracefully empty list
        recommendations = []
        try:
            first_genre = genres.split(",")[0].strip() if genres else ""
            query = first_genre if first_genre else (game_title or "")
            # Only search if query exists
            if query:
                results = VideoGameService.search(query, limit=limit + 6)
                for item in results:
                    t = item.get("title", "")
                    if game_title and t.lower() == game_title.lower():
                        continue
                    recommendations.append({
                        "category": "game",
                        "external_id": item.get("external_id", ""),
                        "title": t,
                        "subtitle": item.get("platforms") or "Game",
                        "year": item.get("release_year") or "",
                        "poster_url": item.get("cover_url", ""),
                        "rating": None,
                        "overview": item.get("genres", ""),
                    })
        except Exception as e:
            logger.warning("Video game recommendation fallback error: %s", e)

        cache.set(cache_key, recommendations, CACHE_TTL)
        return cls._filter_user_library(recommendations, user, "game")[:limit]

    @classmethod
    def _filter_user_library(cls, items: List[Dict[str, Any]], user, category: str) -> List[Dict[str, Any]]:
        """
        Excludes items that are already in the user's personal tracked library.
        """
        if not user or not user.is_authenticated:
            return items

        try:
            existing_ids = set()
            existing_titles = set()

            if category == "movie":
                from movies.models import MovieEntry
                qs = MovieEntry.objects.filter(user=user)
                existing_ids = set(qs.exclude(tmdb_id__isnull=True).values_list("tmdb_id", flat=True))
                existing_titles = {t.lower() for t in qs.values_list("title", flat=True) if t}
            elif category == "series":
                from series.models import SeriesEntry
                qs = SeriesEntry.objects.filter(user=user)
                existing_ids = set(qs.exclude(tmdb_id__isnull=True).values_list("tmdb_id", flat=True))
                existing_titles = {t.lower() for t in qs.values_list("title", flat=True) if t}
            elif category == "book":
                from books.models import BookEntry
                qs = BookEntry.objects.filter(user=user)
                existing_titles = {t.lower() for t in qs.values_list("title", flat=True) if t}
            elif category == "game":
                from games.models import UserVideoGame
                qs = UserVideoGame.objects.filter(user=user).select_related("game")
                existing_titles = {uvg.game.title.lower() for uvg in qs if uvg.game and uvg.game.title}

            filtered = []
            for item in items:
                ext_id = item.get("external_id")
                # Normalize tmdb_id comparison
                if ext_id and (ext_id in existing_ids or (ext_id.isdigit() and int(ext_id) in existing_ids)):
                    continue
                if item.get("title", "").strip().lower() in existing_titles:
                    continue
                filtered.append(item)
            return filtered
        except Exception as e:
            logger.error("Error filtering library recommendations: %s", e)
            return items

recommendation_engine = RecommendationEngine()
