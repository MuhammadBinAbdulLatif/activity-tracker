from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from services.recommendation_engine import RecommendationEngine
from movies.models import MovieEntry, MovieStatus
from books.models import BookEntry, BookStatus

User = get_user_model()

class RecommendationEngineTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="recuser", password="password123")
        # Create an existing movie in user's library
        self.existing_movie = MovieEntry.objects.create(
            user=self.user,
            title="Inception",
            tmdb_id=27205,
            status=MovieStatus.COMPLETED
        )
        # Create an existing book in user's library
        self.existing_book = BookEntry.objects.create(
            user=self.user,
            title="Dune",
            author="Frank Herbert",
            status=BookStatus.COMPLETED
        )

    @patch("services.tmdb.tmdb_service.get_movie_recommendations")
    def test_movie_recommendations_and_deduplication(self, mock_tmdb_recs):
        # Return Inception (already tracked) and Interstellar (new)
        mock_tmdb_recs.return_value = [
            {"id": 27205, "title": "Inception", "release_date": "2010-07-16", "poster_path": "/path1.jpg", "vote_average": 8.4},
            {"id": 157336, "title": "Interstellar", "release_date": "2014-11-07", "poster_path": "/path2.jpg", "vote_average": 8.6},
        ]

        recs = RecommendationEngine.get_movie_recommendations(tmdb_id=99999, user=self.user, limit=5)
        
        # Verify deduplication: Inception is excluded because user already has it
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["title"], "Interstellar")
        self.assertEqual(recs[0]["year"], "2014")
        self.assertEqual(recs[0]["external_id"], "157336")

    @patch("services.openlibrary.openlibrary_service.get_recommendations_for_book")
    def test_book_recommendations_and_deduplication(self, mock_book_recs):
        # Return Dune (already tracked) and Dune Messiah (new)
        mock_book_recs.return_value = [
            {"title": "Dune", "author": "Frank Herbert", "openlibrary_key": "/works/OL1", "publish_year": 1965, "cover_url": ""},
            {"title": "Dune Messiah", "author": "Frank Herbert", "openlibrary_key": "/works/OL2", "publish_year": 1969, "cover_url": ""},
        ]

        recs = RecommendationEngine.get_book_recommendations(
            author="Frank Herbert",
            current_title="Children of Dune",
            user=self.user,
            limit=5
        )

        # Dune should be filtered out because the user already tracks Dune
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["title"], "Dune Messiah")
        self.assertEqual(recs[0]["year"], 1969)

    def test_empty_graceful_handling(self):
        # Graceful empty return on none or zero
        recs = RecommendationEngine.get_movie_recommendations(tmdb_id=None, user=self.user)
        self.assertEqual(recs, [])

        recs_game = RecommendationEngine.get_game_recommendations(game_title="", genres="", user=self.user)
        self.assertEqual(recs_game, [])
