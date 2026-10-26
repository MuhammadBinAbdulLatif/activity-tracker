from django.db import models

# Create your models here.


class Sources(models.TextChoices):
    """Choices that a user has for the source of whatever he is going to add"""

    TMDB = "tmdb", "The Movie Database"
    MAL = "mal", "MyAnimeList"
    MANGAUPDATES = "mangaupdates", "MangaUpdates"
    IGDB = "igdb", "Internet Game Database"
    OPENLIBRARY = "openlibrary", "Open Library"
    HARDCOVER = "hardcover", "Hardcover"  # if not apparent by the name, discover books
