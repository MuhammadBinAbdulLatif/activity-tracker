from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
from decimal import Decimal

from .models import GameEntry, GameStatus


# =========================================================================== #
# Model Tests
# =========================================================================== #

class GameModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="gamer", password="password123")

    def _make_entry(self, **kwargs):
        defaults = dict(user=self.user, title="Test Game", status=GameStatus.BACKLOG)
        defaults.update(kwargs)
        return GameEntry.objects.create(**defaults)

    def test_create_with_required_fields_only(self):
        entry = self._make_entry()
        self.assertEqual(entry.title, "Test Game")
        self.assertEqual(entry.status, GameStatus.BACKLOG)
        self.assertEqual(entry.hours_played, Decimal("0.0"))
        self.assertEqual(entry.completion_percentage, 0)
        self.assertIsNone(entry.rating)

    def test_default_status_is_backlog(self):
        entry = GameEntry(user=self.user, title="Another Game")
        self.assertEqual(entry.status, GameStatus.BACKLOG)

    def test_display_cover_returns_custom_cover_url_when_set(self):
        entry = self._make_entry(cover_url="http://example.com/cover.jpg")
        # Without a real file upload in tests, we test the cover_url fallback
        self.assertEqual(entry.display_cover, "http://example.com/cover.jpg")

    def test_display_cover_returns_cover_url_fallback(self):
        entry = self._make_entry(cover_url="http://cdn.rawg.io/game.png")
        self.assertEqual(entry.display_cover, "http://cdn.rawg.io/game.png")

    def test_display_cover_returns_empty_string_when_neither_set(self):
        entry = self._make_entry()
        self.assertEqual(entry.display_cover, "")

    def test_hours_display(self):
        entry = self._make_entry(hours_played=Decimal("12.5"))
        self.assertEqual(entry.hours_display, "12.5h")

    def test_hours_display_zero(self):
        entry = self._make_entry()
        self.assertEqual(entry.hours_display, "0.0h")

    def test_completion_display(self):
        entry = self._make_entry(completion_percentage=75)
        self.assertEqual(entry.completion_display, "75%")

    def test_completion_display_zero(self):
        entry = self._make_entry()
        self.assertEqual(entry.completion_display, "0%")

    def test_status_badge_class_playing(self):
        entry = self._make_entry(status=GameStatus.PLAYING)
        self.assertIn("emerald", entry.status_badge_class)

    def test_status_badge_class_backlog(self):
        entry = self._make_entry(status=GameStatus.BACKLOG)
        self.assertIn("blue", entry.status_badge_class)

    def test_status_badge_class_dropped(self):
        entry = self._make_entry(status=GameStatus.DROPPED)
        self.assertIn("red", entry.status_badge_class)

    def test_str_representation(self):
        entry = self._make_entry()
        self.assertIn("Test Game", str(entry))
        self.assertIn("gamer", str(entry))


# =========================================================================== #
# Service Tests
# =========================================================================== #

class GameServiceTests(TestCase):

    @patch("services.videogame_service.urllib.request.urlopen")
    def test_search_returns_normalized_results(self, mock_urlopen):
        """Search returns a list of normalized dicts on a mocked RAWG response."""
        import json, os
        os.environ["RAWG_API_KEY"] = "test-key"

        mock_response = MagicMock()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = json.dumps({
            "results": [
                {
                    "id": 3498,
                    "name": "The Witcher 3: Wild Hunt",
                    "background_image": "https://cdn.rawg.io/witcher3.jpg",
                    "released": "2015-05-18",
                    "metacritic": 92,
                    "genres": [{"name": "RPG"}, {"name": "Action"}],
                    "platforms": [
                        {"platform": {"name": "PC"}},
                        {"platform": {"name": "PlayStation 4"}},
                    ],
                }
            ]
        }).encode("utf-8")
        mock_urlopen.return_value = mock_response

        from services.videogame_service import VideoGameService, _cache
        _cache.clear()

        results = VideoGameService.search("witcher")

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        game = results[0]
        self.assertIn("external_id", game)
        self.assertIn("title", game)
        self.assertIn("cover_url", game)
        self.assertIn("release_year", game)
        self.assertIn("genres", game)
        self.assertIn("platforms", game)
        self.assertIn("developers", game)
        self.assertEqual(game["title"], "The Witcher 3: Wild Hunt")
        self.assertEqual(game["release_year"], 2015)
        self.assertEqual(game["external_id"], "rawg-3498")
        self.assertIn("RPG", game["genres"])

        # Clean up
        del os.environ["RAWG_API_KEY"]

    @patch("services.videogame_service.urllib.request.urlopen")
    def test_search_returns_empty_list_on_http_error(self, mock_urlopen):
        """Search returns [] on any network failure."""
        import os, urllib.error
        os.environ["RAWG_API_KEY"] = "test-key"
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        from services.videogame_service import VideoGameService, _cache
        _cache.clear()

        results = VideoGameService.search("anything")
        self.assertEqual(results, [])

        del os.environ["RAWG_API_KEY"]

    def test_search_returns_empty_list_when_key_missing(self):
        """Search returns [] when RAWG_API_KEY is not set."""
        import os
        os.environ.pop("RAWG_API_KEY", None)

        from services.videogame_service import VideoGameService, _cache
        _cache.clear()

        results = VideoGameService.search("test query")
        self.assertEqual(results, [])

    @patch("services.videogame_service.urllib.request.urlopen")
    def test_search_results_are_cached(self, mock_urlopen):
        """A second search with the same query uses cache instead of network."""
        import json, os
        os.environ["RAWG_API_KEY"] = "test-key"

        mock_response = MagicMock()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = json.dumps({"results": []}).encode("utf-8")
        mock_urlopen.return_value = mock_response

        from services.videogame_service import VideoGameService, _cache
        _cache.clear()

        VideoGameService.search("cached-query")
        VideoGameService.search("cached-query")

        # urlopen should have been called only once (second was from cache)
        self.assertEqual(mock_urlopen.call_count, 1)

        del os.environ["RAWG_API_KEY"]


# =========================================================================== #
# View Tests
# =========================================================================== #

class GameViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="player1", password="pass123")
        self.other_user = User.objects.create_user(username="other_player", password="pass456")
        self.client.login(username="player1", password="pass123")

        self.playing_game = GameEntry.objects.create(
            user=self.user,
            title="Elden Ring",
            status=GameStatus.PLAYING,
            hours_played=Decimal("35.5"),
            completion_percentage=60,
            platform_played="PC",
            genres="Action RPG, Open World",
            developers="FromSoftware",
        )
        self.backlog_game = GameEntry.objects.create(
            user=self.user,
            title="Cyberpunk 2077",
            status=GameStatus.BACKLOG,
        )
        self.completed_game = GameEntry.objects.create(
            user=self.user,
            title="Hollow Knight",
            status=GameStatus.COMPLETED,
            hours_played=Decimal("42.0"),
            completion_percentage=100,
            rating=Decimal("9.5"),
        )

    # --- List View ---

    def test_list_view_returns_200_for_authenticated_user(self):
        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/list.html")

    def test_list_view_redirects_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_list_view_context_has_status_shelves(self):
        response = self.client.get(reverse("game_list"))
        self.assertIn("playing", response.context)
        self.assertIn("backlog", response.context)
        self.assertIn("completed", response.context)
        self.assertIn("on_hold", response.context)
        self.assertIn("dropped", response.context)

    def test_list_view_shows_game_titles(self):
        response = self.client.get(reverse("game_list"))
        self.assertContains(response, "Elden Ring")
        self.assertContains(response, "Cyberpunk 2077")
        self.assertContains(response, "Hollow Knight")

    # --- Search View ---

    @patch("games.views.VideoGameService.search")
    def test_search_view_returns_partial_html(self, mock_search):
        mock_search.return_value = [
            {
                "external_id": "rawg-1234",
                "title": "God of War",
                "cover_url": "",
                "release_year": 2018,
                "genres": "Action",
                "platforms": "PS4, PC",
                "developers": "Santa Monica Studio",
                "publishers": "Sony",
                "metacritic_score": 94,
            }
        ]
        response = self.client.get(reverse("search_games") + "?q=god+of+war")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/partials/search_results.html")
        self.assertContains(response, "God of War")

    @patch("games.views.VideoGameService.search")
    def test_search_marks_tracked_games(self, mock_search):
        """Games already tracked by the user get is_tracked=True."""
        # Create a matching entry in the DB
        tracked = GameEntry.objects.create(
            user=self.user, title="Elden Ring", status=GameStatus.PLAYING,
            external_id="rawg-9999",
        )
        mock_search.return_value = [
            {
                "external_id": "rawg-9999",
                "title": "Elden Ring",
                "cover_url": "", "release_year": 2022,
                "genres": "Action", "platforms": "PC",
                "developers": "FromSoftware", "publishers": "Bandai",
                "metacritic_score": 96,
            }
        ]
        response = self.client.get(reverse("search_games") + "?q=elden+ring")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tracked")

    # --- Add Game ---

    def test_add_game_quick_add_creates_entry_and_redirects(self):
        response = self.client.post(reverse("add_game"), {
            "external_id": "rawg-5555",
            "title": "Hades",
            "cover_url": "https://cdn.rawg.io/hades.jpg",
            "release_year": "2020",
            "genres": "Roguelike",
            "platforms": "PC, Switch",
            "developers": "Supergiant Games",
            "publishers": "Supergiant Games",
            "status": "PLAYING",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GameEntry.objects.filter(user=self.user, title="Hades").exists())
        entry = GameEntry.objects.get(user=self.user, title="Hades")
        self.assertIn("/games/", response["Location"])

    def test_add_game_manual_form_creates_entry(self):
        response = self.client.post(reverse("add_game"), {
            "title": "My Custom Game",
            "status": "BACKLOG",
            "hours_played": "0.0",
            "completion_percentage": "0",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GameEntry.objects.filter(user=self.user, title="My Custom Game").exists())

    def test_add_game_missing_title_returns_form_error(self):
        response = self.client.post(reverse("add_game"), {
            "status": "BACKLOG",
            "hours_played": "0.0",
            "completion_percentage": "0",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(GameEntry.objects.filter(user=self.user, title="").exists())

    # --- Detail View ---

    def test_detail_view_returns_200(self):
        response = self.client.get(reverse("game_detail", args=[self.playing_game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/detail.html")
        self.assertContains(response, "Elden Ring")
        self.assertContains(response, "FromSoftware")

    def test_detail_view_returns_404_for_other_users_game(self):
        other_game = GameEntry.objects.create(
            user=self.other_user, title="Private Game", status=GameStatus.PLAYING
        )
        response = self.client.get(reverse("game_detail", args=[other_game.pk]))
        self.assertEqual(response.status_code, 404)

    # --- Update Details ---

    def test_update_details_saves_changes_and_redirects(self):
        response = self.client.post(
            reverse("update_game_details", args=[self.playing_game.pk]),
            {
                "title": "Elden Ring",
                "status": "COMPLETED",
                "hours_played": "80.0",
                "completion_percentage": "100",
                "rating": "9.8",
                "review": "Masterpiece.",
                "notes": "",
                "platform_played": "PC",
            }
        )
        self.assertEqual(response.status_code, 302)
        self.playing_game.refresh_from_db()
        self.assertEqual(self.playing_game.status, GameStatus.COMPLETED)
        self.assertEqual(self.playing_game.hours_played, Decimal("80.0"))
        self.assertEqual(self.playing_game.completion_percentage, 100)
        self.assertEqual(self.playing_game.review, "Masterpiece.")

    # --- Delete ---

    def test_delete_game_removes_entry_and_redirects(self):
        pk = self.backlog_game.pk
        response = self.client.post(reverse("delete_game", args=[pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(GameEntry.objects.filter(pk=pk).exists())
        self.assertRedirects(response, reverse("game_list"))

    def test_delete_game_returns_404_for_other_users_game(self):
        other_game = GameEntry.objects.create(
            user=self.other_user, title="Not Mine", status=GameStatus.BACKLOG
        )
        response = self.client.post(reverse("delete_game", args=[other_game.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(GameEntry.objects.filter(pk=other_game.pk).exists())
