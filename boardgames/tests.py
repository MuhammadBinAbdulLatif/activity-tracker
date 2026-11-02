from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from datetime import date

from .models import BoardGameEntry, BoardGameStatus
from services.boardgame_service import BoardGameService, _CACHE


class BoardGameModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tabletop_fan", password="password123")

    def test_create_minimal_entry(self):
        entry = BoardGameEntry.objects.create(
            user=self.user,
            title="Catan",
        )
        self.assertEqual(entry.status, BoardGameStatus.WANT_TO_PLAY)
        self.assertEqual(entry.play_count, 0)
        self.assertIn("Catan", str(entry))
        self.assertIn("tabletop_fan", str(entry))

    def test_display_cover_fallback(self):
        entry = BoardGameEntry.objects.create(
            user=self.user,
            title="Wingspan",
            cover_url="https://cf.geekdo-images.com/wingspan.jpg",
        )
        self.assertEqual(entry.display_cover, "https://cf.geekdo-images.com/wingspan.jpg")

    def test_player_count_display(self):
        e1 = BoardGameEntry.objects.create(user=self.user, title="Gloomhaven", min_players=1, max_players=4)
        self.assertEqual(e1.player_count_display, "1–4 players")

        e2 = BoardGameEntry.objects.create(user=self.user, title="Chess", min_players=2, max_players=2)
        self.assertEqual(e2.player_count_display, "2 players")

        e3 = BoardGameEntry.objects.create(user=self.user, title="Solitaire", min_players=1, max_players=1)
        self.assertEqual(e3.player_count_display, "1 player")

    def test_playtime_display(self):
        e1 = BoardGameEntry.objects.create(user=self.user, title="Twilight Imperium", min_playtime=240, max_playtime=480)
        self.assertEqual(e1.playtime_display, "240–480 min")

        e2 = BoardGameEntry.objects.create(user=self.user, title="Love Letter", min_playtime=20, max_playtime=20)
        self.assertEqual(e2.playtime_display, "20 min")

    def test_status_badge_class(self):
        e = BoardGameEntry.objects.create(user=self.user, title="Concordia", status=BoardGameStatus.PLAYED)
        self.assertIn("text-emerald-400", e.status_badge_class)

    def test_total_hours_played(self):
        e = BoardGameEntry.objects.create(
            user=self.user,
            title="Dune: Imperium",
            play_count=4,
            avg_session_minutes=90,
        )
        self.assertEqual(e.total_hours_played, "6.0h")


class BoardGameServiceTests(TestCase):
    def setUp(self):
        _CACHE.clear()

    @patch("services.boardgame_service.BoardGameService._fetch_xml")
    def test_search_returns_normalized_list(self, mock_fetch):
        mock_fetch.return_value = """<?xml version="1.0" encoding="utf-8"?>
        <items total="1" termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
            <item type="boardgame" id="13">
                <name type="primary" value="Catan"/>
                <yearpublished value="1995"/>
            </item>
        </items>
        """
        results = BoardGameService.search("Catan")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["external_id"], "bgg-13")
        self.assertEqual(results[0]["title"], "Catan")
        self.assertEqual(results[0]["year_published"], 1995)

    @patch("services.boardgame_service.BoardGameService._fetch_xml")
    def test_search_handles_network_failure(self, mock_fetch):
        mock_fetch.return_value = None
        results = BoardGameService.search("Catan")
        self.assertEqual(results, [])

    def test_search_empty_query(self):
        self.assertEqual(BoardGameService.search(""), [])

    @patch("services.boardgame_service.BoardGameService._fetch_xml")
    def test_get_details_normalized(self, mock_fetch):
        mock_fetch.return_value = """<?xml version="1.0" encoding="utf-8"?>
        <items termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
            <item type="boardgame" id="13">
                <thumbnail>https://cf.geekdo-images.com/thumb.jpg</thumbnail>
                <image>https://cf.geekdo-images.com/full.jpg</image>
                <name type="primary" sortindex="1" value="Catan"/>
                <description>In Catan, players try to be the dominant force on the island of Catan.</description>
                <yearpublished value="1995"/>
                <minplayers value="3"/>
                <maxplayers value="4"/>
                <playingtime value="120"/>
                <minplaytime value="60"/>
                <maxplaytime value="120"/>
                <link type="boardgamedesigner" id="1" value="Klaus Teuber"/>
                <link type="boardgamepublisher" id="1" value="KOSMOS"/>
                <link type="boardgamecategory" id="1" value="Economic"/>
                <link type="boardgamemechanic" id="1" value="Trading"/>
                <statistics page="1">
                    <ratings>
                        <average value="7.14231"/>
                        <ranks>
                            <rank type="subtype" id="1" name="boardgame" friendlyname="Board Game Rank" value="512"/>
                        </ranks>
                    </ratings>
                </statistics>
            </item>
        </items>
        """
        details = BoardGameService.get_details("bgg-13")
        self.assertEqual(details["external_id"], "bgg-13")
        self.assertEqual(details["title"], "Catan")
        self.assertEqual(details["min_players"], 3)
        self.assertEqual(details["max_players"], 4)
        self.assertEqual(details["min_playtime"], 60)
        self.assertEqual(details["max_playtime"], 120)
        self.assertEqual(details["designers"], "Klaus Teuber")
        self.assertEqual(details["bgg_rating"], 7.14)
        self.assertEqual(details["bgg_rank"], 512)

    @patch("services.boardgame_service.BoardGameService._fetch_xml")
    def test_get_details_caching(self, mock_fetch):
        mock_fetch.return_value = """<?xml version="1.0" encoding="utf-8"?>
        <items><item type="boardgame" id="99"><name type="primary" value="Cached Game"/></item></items>
        """
        # Call 1
        d1 = BoardGameService.get_details("99")
        self.assertEqual(d1["title"], "Cached Game")
        self.assertEqual(mock_fetch.call_count, 1)

        # Call 2 should hit cache
        d2 = BoardGameService.get_details("99")
        self.assertEqual(d2["title"], "Cached Game")
        self.assertEqual(mock_fetch.call_count, 1)


class BoardGameViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="gamer1", password="password123")
        self.other_user = User.objects.create_user(username="gamer2", password="password123")
        self.client.login(username="gamer1", password="password123")

    def test_list_view_login_required(self):
        self.client.logout()
        resp = self.client.get(reverse("boardgame_list"))
        self.assertEqual(resp.status_code, 302)

    def test_list_view_renders_correctly(self):
        BoardGameEntry.objects.create(user=self.user, title="Cascadia", status=BoardGameStatus.OWNED)
        BoardGameEntry.objects.create(user=self.user, title="Everdell", status=BoardGameStatus.PLAYED)

        resp = self.client.get(reverse("boardgame_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Cascadia")
        self.assertContains(resp, "Everdell")
        self.assertIn("played", resp.context)
        self.assertIn("owned", resp.context)

    @patch("services.boardgame_service.BoardGameService.search")
    def test_search_endpoint(self, mock_search):
        mock_search.return_value = [
            {"external_id": "bgg-1", "id": "1", "title": "Die Macher", "year_published": 1986}
        ]
        resp = self.client.get(reverse("search_boardgames"), {"q": "Die Macher"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Die Macher")

    @patch("services.boardgame_service.BoardGameService.get_details")
    def test_add_from_search(self, mock_details):
        mock_details.return_value = {
            "external_id": "bgg-13",
            "title": "Catan",
            "cover_url": "https://example.com/catan.jpg",
            "year_published": 1995,
            "min_players": 3,
            "max_players": 4,
            "min_playtime": 60,
            "max_playtime": 120,
            "designers": "Klaus Teuber",
            "publishers": "KOSMOS",
            "categories": "Trading",
            "mechanics": "Dice Rolling",
            "bgg_rating": 7.1,
            "bgg_rank": 500,
            "description": "Island trading game",
        }
        resp = self.client.post(reverse("add_boardgame"), {
            "external_id": "bgg-13",
            "title": "Catan",
            "status": "OWNED",
        })
        entry = BoardGameEntry.objects.get(title="Catan", user=self.user)
        self.assertEqual(entry.status, BoardGameStatus.OWNED)
        self.assertEqual(entry.designers, "Klaus Teuber")
        self.assertRedirects(resp, reverse("boardgame_detail", kwargs={"pk": entry.pk}))

    def test_manual_add(self):
        resp = self.client.post(reverse("add_boardgame"), {
            "title": "Custom Print and Play",
            "status": "PLAYED",
            "min_players": 2,
            "max_players": 2,
        })
        entry = BoardGameEntry.objects.get(title="Custom Print and Play", user=self.user)
        self.assertEqual(entry.status, BoardGameStatus.PLAYED)
        self.assertRedirects(resp, reverse("boardgame_detail", kwargs={"pk": entry.pk}))

    def test_detail_view_permissions(self):
        entry = BoardGameEntry.objects.create(user=self.other_user, title="Secret Game")
        resp = self.client.get(reverse("boardgame_detail", kwargs={"pk": entry.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_log_play_action(self):
        entry = BoardGameEntry.objects.create(
            user=self.user,
            title="Scout",
            status=BoardGameStatus.WANT_TO_PLAY,
            play_count=0,
        )
        resp = self.client.post(reverse("log_play", kwargs={"pk": entry.pk}))
        entry.refresh_from_db()
        self.assertEqual(entry.play_count, 1)
        self.assertEqual(entry.status, BoardGameStatus.PLAYED)
        self.assertEqual(entry.last_played, date.today())
        self.assertRedirects(resp, reverse("boardgame_detail", kwargs={"pk": entry.pk}))

    def test_update_details(self):
        entry = BoardGameEntry.objects.create(user=self.user, title="Wingspan")
        resp = self.client.post(reverse("update_boardgame_details", kwargs={"pk": entry.pk}), {
            "title": "Wingspan (Updated)",
            "status": "OWNED",
            "rating": "9.5",
            "review": "Remarkable engine building.",
        })
        entry.refresh_from_db()
        self.assertEqual(entry.title, "Wingspan (Updated)")
        self.assertEqual(entry.rating, 9.5)
        self.assertEqual(entry.review, "Remarkable engine building.")
        self.assertRedirects(resp, reverse("boardgame_detail", kwargs={"pk": entry.pk}))

    def test_delete_boardgame(self):
        entry = BoardGameEntry.objects.create(user=self.user, title="Monopoly")
        resp = self.client.post(reverse("delete_boardgame", kwargs={"pk": entry.pk}))
        self.assertFalse(BoardGameEntry.objects.filter(pk=entry.pk).exists())
        self.assertRedirects(resp, reverse("boardgame_list"))
