import hashlib
import json
import logging
import os
import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

class TMDBService:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY", "")
        self.access_token = os.getenv("TMDB_READ_ACCESS_TOKEN", "")

    def _get_headers(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json;charset=utf-8",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _build_params(self, extra_params=None):
        params = {}
        if self.api_key and not self.access_token:
            params["api_key"] = self.api_key
        if extra_params:
            params.update(extra_params)
        return params

    def _request(self, endpoint, params=None, cache_ttl=21600):
        """
        Executes a cached GET request to TMDB API.
        Default cache TTL is 6 hours (21600 seconds).
        """
        param_str = json.dumps(params or {}, sort_keys=True)
        cache_key = f"tmdb:{endpoint}:{hashlib.md5(param_str.encode()).hexdigest()}"
        
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        url = f"{TMDB_BASE_URL}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        req_params = self._build_params(params)

        try:
            resp = requests.get(url, headers=headers, params=req_params, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                cache.set(cache_key, data, cache_ttl)
                return data
            else:
                logger.warning("TMDB request to %s returned %s: %s", url, resp.status_code, resp.text)
                return None
        except Exception as e:
            logger.error("Error connecting to TMDB: %s", e)
            return None

    # --------------------------------------------------------------------------
    # Movie Endpoints
    # --------------------------------------------------------------------------
    def search_movies(self, query, year=None, page=1):
        if not query:
            return {"results": []}
        params = {"query": query, "page": page, "include_adult": False}
        if year:
            params["primary_release_year"] = year
        data = self._request("search/movie", params=params, cache_ttl=7200)
        return data or {"results": []}

    def get_movie_details(self, tmdb_id):
        params = {"append_to_response": "credits"}
        data = self._request(f"movie/{tmdb_id}", params=params, cache_ttl=86400)
        return data

    # --------------------------------------------------------------------------
    # TV Series Endpoints
    # --------------------------------------------------------------------------
    def search_series(self, query, year=None, page=1):
        if not query:
            return {"results": []}
        params = {"query": query, "page": page, "include_adult": False}
        if year:
            params["first_air_date_year"] = year
        data = self._request("search/tv", params=params, cache_ttl=7200)
        return data or {"results": []}

    def get_series_details(self, tmdb_id):
        params = {"append_to_response": "credits"}
        data = self._request(f"tv/{tmdb_id}", params=params, cache_ttl=86400)
        return data

    def get_season_details(self, tmdb_id, season_number):
        data = self._request(f"tv/{tmdb_id}/season/{season_number}", cache_ttl=86400)
        return data

# Singleton client instance
tmdb_service = TMDBService()
