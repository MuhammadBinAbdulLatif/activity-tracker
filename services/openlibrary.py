import json
import urllib.parse
import urllib.request
import logging

logger = logging.getLogger(__name__)

class OpenLibraryService:
    BASE_URL = "https://openlibrary.org"
    COVERS_BASE_URL = "https://covers.openlibrary.org/b/id"

    def __init__(self, timeout=6):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "uTrack/1.0 (Personal Media & Reading Tracker; contact: support@utrack.local)"
        }

    def search_books(self, query, limit=10):
        """
        Searches Open Library for books matching the given title, author, or ISBN.
        Returns a list of clean normalized book dictionaries.
        """
        if not query or not query.strip():
            return {"results": []}

        encoded_query = urllib.parse.quote_plus(query.strip())
        url = (
            f"{self.BASE_URL}/search.json?q={encoded_query}"
            f"&limit={limit}&fields=key,title,author_name,first_publish_year,cover_i,number_of_pages_median,isbn,subject"
        )

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status != 200:
                    logger.warning(f"Open Library search failed with status {resp.status}")
                    return {"results": []}
                data = json.loads(resp.read().decode("utf-8"))

            raw_docs = data.get("docs", [])
            formatted = []

            for doc in raw_docs:
                work_key = doc.get("key", "")
                title = doc.get("title", "Untitled")
                authors = doc.get("author_name", [])
                author_str = ", ".join(authors) if authors else "Unknown Author"
                publish_year = doc.get("first_publish_year")
                page_count = doc.get("number_of_pages_median") or 0
                cover_id = doc.get("cover_i")
                cover_url = f"{self.COVERS_BASE_URL}/{cover_id}-L.jpg" if cover_id else ""
                
                isbns = doc.get("isbn", [])
                primary_isbn = isbns[0] if isbns else ""

                subjects = doc.get("subject", [])
                genres = ", ".join(subjects[:4]) if subjects else ""

                formatted.append({
                    "openlibrary_key": work_key,
                    "title": title,
                    "author": author_str,
                    "publish_year": publish_year,
                    "page_count": page_count,
                    "cover_url": cover_url,
                    "isbn": primary_isbn,
                    "genres": genres,
                })

            return {"results": formatted}

        except Exception as e:
            logger.error(f"Error fetching books from Open Library: {e}")
            return {"results": []}

    def get_book_details(self, work_key):
        """
        Fetches detailed work metadata from Open Library, including synopsis/description.
        """
        if not work_key:
            return None

        # Clean work_key if passed without leading slash
        clean_key = work_key if work_key.startswith("/") else f"/{work_key}"
        if not clean_key.startswith("/works/"):
            clean_key = f"/works/{clean_key.lstrip('/')}"

        url = f"{self.BASE_URL}{clean_key}.json"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status != 200:
                    return None
                data = json.loads(resp.read().decode("utf-8"))

            # Description can be either string or dict {'value': '...'}
            desc_raw = data.get("description", "")
            if isinstance(desc_raw, dict):
                description = desc_raw.get("value", "")
            else:
                description = str(desc_raw) if desc_raw else ""

            subjects = data.get("subjects", [])
            genres = ", ".join(subjects[:5]) if subjects else ""

            return {
                "openlibrary_key": clean_key,
                "title": data.get("title", ""),
                "description": description.strip(),
                "genres": genres,
            }
        except Exception as e:
            logger.error(f"Error fetching work details for {work_key}: {e}")
            return None

openlibrary_service = OpenLibraryService()
