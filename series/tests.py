import io
from PIL import Image
from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import SeriesEntry, SeasonEntry, EpisodeLog, SeriesUserStatus, SeriesShowStatus
from .engine import SeriesProgressionEngine

class SeriesTrackingAndEngineTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="series_binger", password="testpassword123")
        self.client.login(username="series_binger", password="testpassword123")

    def _generate_test_image(self):
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color=(120, 80, 160))
        image.save(file, "jpeg")
        file.seek(0)
        return SimpleUploadedFile("test_series_poster.jpg", file.read(), content_type="image/jpeg")

    def test_series_list_requires_login(self):
        self.client.logout()
        res = self.client.get(reverse("series_list"))
        self.assertEqual(res.status_code, 302)
        self.assertIn("/accounts/login/", res.url)

    def test_advance_single_episode(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Severance",
            current_season_number=1,
            current_episode_number=3,
            user_status=SeriesUserStatus.WATCHING
        )
        SeasonEntry.objects.create(
            series=series,
            season_number=1,
            episode_count=9
        )

        res = self.client.post(reverse("series_advance_episode", args=[series.id]))
        self.assertEqual(res.status_code, 302)

        series.refresh_from_db()
        self.assertEqual(series.current_episode_number, 4)
        self.assertEqual(series.current_season_number, 1)

        # Confirm EpisodeLog created for heatmap
        log = EpisodeLog.objects.filter(series=series, season_number=1, episode_number=4).first()
        self.assertIsNotNone(log)

    def test_automatic_next_season_rollover(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="House of the Dragon",
            current_season_number=1,
            current_episode_number=9,
            user_status=SeriesUserStatus.WATCHING
        )
        SeasonEntry.objects.create(series=series, season_number=1, episode_count=10)
        SeasonEntry.objects.create(series=series, season_number=2, episode_count=8)

        result = SeriesProgressionEngine.advance_episode(series)
        series.refresh_from_db()

        self.assertEqual(series.current_season_number, 2)
        self.assertEqual(series.current_episode_number, 0)
        self.assertEqual(series.user_status, SeriesUserStatus.WATCHING)
        self.assertIn("Advanced automatically to Season 2", result["message"])

        s1 = SeasonEntry.objects.get(series=series, season_number=1)
        self.assertTrue(s1.is_completed)

    def test_upcoming_season_waiting_state(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Stranger Things",
            current_season_number=4,
            current_episode_number=8,
            show_status=SeriesShowStatus.RETURNING,
            user_status=SeriesUserStatus.WATCHING
        )
        SeasonEntry.objects.create(series=series, season_number=4, episode_count=9)
        next_year = timezone.now().date() + timedelta(days=200)
        SeasonEntry.objects.create(series=series, season_number=5, episode_count=8, air_date=next_year)

        result = SeriesProgressionEngine.advance_episode(series)
        series.refresh_from_db()

        self.assertEqual(series.user_status, SeriesUserStatus.WAITING_FOR_NEXT_SEASON)
        self.assertIn("Waiting for Season 5", result["message"])

    def test_ended_series_full_completion(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Breaking Bad",
            current_season_number=5,
            current_episode_number=15,
            show_status=SeriesShowStatus.ENDED,
            user_status=SeriesUserStatus.WATCHING
        )
        SeasonEntry.objects.create(series=series, season_number=5, episode_count=16)

        result = SeriesProgressionEngine.advance_episode(series)
        series.refresh_from_db()

        self.assertEqual(series.user_status, SeriesUserStatus.COMPLETED)
        self.assertIn("Entire series of Breaking Bad completed", result["message"])

    def test_add_custom_series_with_image_upload(self):
        test_image = self._generate_test_image()
        res = self.client.post(reverse("series_add"), {
            "title": "Custom Web Series",
            "total_seasons": "2",
            "total_episodes": "12",
            "current_season_number": "1",
            "current_episode_number": "3",
            "status": "WATCHING",
            "rating": "8.8",
            "poster_file": test_image,
        })
        self.assertEqual(res.status_code, 302)

        series = SeriesEntry.objects.filter(user=self.user, title="Custom Web Series").first()
        self.assertIsNotNone(series)
        self.assertTrue(series.is_custom)
        self.assertEqual(series.current_season_number, 1)
        self.assertEqual(series.current_episode_number, 3)
        self.assertEqual(series.user_status, SeriesUserStatus.WATCHING)
        self.assertIsNotNone(series.custom_poster)
        self.assertTrue(series.poster_url.endswith(".jpg"))

    def test_series_detail_view_rendering(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Succession",
            cast="Brian Cox, Jeremy Strong, Sarah Snook",
            genres="Drama",
            overview="The Roy family is known for controlling the biggest media and entertainment company in the world.",
            current_season_number=2,
            current_episode_number=4,
            total_seasons=4,
            total_episodes=39,
            user_status=SeriesUserStatus.WATCHING,
        )
        SeasonEntry.objects.create(series=series, season_number=1, episode_count=10, is_completed=True)
        SeasonEntry.objects.create(series=series, season_number=2, episode_count=10, is_completed=False)

        res = self.client.get(reverse("series_detail", args=[series.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Succession")
        self.assertContains(res, "Brian Cox")
        self.assertContains(res, "Jeremy Strong")
        self.assertContains(res, "Season 2")
        self.assertContains(res, "Ep 4")

    def test_series_detail_view_isolation(self):
        other_user = User.objects.create_user(username="other_series_user", password="password123")
        series = SeriesEntry.objects.create(
            user=other_user,
            title="Secret Show",
            user_status=SeriesUserStatus.WATCHING,
        )
        res = self.client.get(reverse("series_detail", args=[series.id]))
        self.assertEqual(res.status_code, 404)

    def test_series_status_reversion_completed_to_watching(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Dark",
            current_season_number=3,
            current_episode_number=8,
            user_status=SeriesUserStatus.COMPLETED,
        )
        SeasonEntry.objects.create(series=series, season_number=1, episode_count=10, is_completed=True)
        SeasonEntry.objects.create(series=series, season_number=2, episode_count=8, is_completed=True)
        SeasonEntry.objects.create(series=series, season_number=3, episode_count=8, is_completed=True)

        res = self.client.post(reverse("series_update_details", args=[series.id]), {
            "status": "WATCHING",
        })
        self.assertEqual(res.status_code, 302)

        series.refresh_from_db()
        self.assertEqual(series.user_status, SeriesUserStatus.WATCHING)

    def test_series_status_reversion_completed_to_plan_to_watch(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="The Wire",
            current_season_number=5,
            current_episode_number=10,
            user_status=SeriesUserStatus.COMPLETED,
        )
        SeasonEntry.objects.create(series=series, season_number=1, episode_count=13, is_completed=True)

        res = self.client.post(reverse("series_update_details", args=[series.id]), {
            "status": "PLAN_TO_WATCH",
        })
        self.assertEqual(res.status_code, 302)

        series.refresh_from_db()
        self.assertEqual(series.user_status, SeriesUserStatus.PLAN_TO_WATCH)
        self.assertEqual(series.current_season_number, 1)
        self.assertEqual(series.current_episode_number, 0)
        s1 = SeasonEntry.objects.get(series=series, season_number=1)
        self.assertFalse(s1.is_completed)

    def test_series_update_personal_log_and_progress(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Fargo",
            current_season_number=1,
            current_episode_number=2,
            user_status=SeriesUserStatus.WATCHING,
        )

        res = self.client.post(reverse("series_update_details", args=[series.id]), {
            "current_season_number": 2,
            "current_episode_number": 5,
            "rating": "9.4",
            "review": "Season 2 was a masterpiece.",
        })
        self.assertEqual(res.status_code, 302)

        series.refresh_from_db()
        self.assertEqual(series.current_season_number, 2)
        self.assertEqual(series.current_episode_number, 5)
        self.assertEqual(float(series.rating), 9.4)
        self.assertEqual(series.review, "Season 2 was a masterpiece.")

    def test_series_custom_metadata_update(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Original SciFi Show",
            is_custom=True,
            total_seasons=1,
            total_episodes=6,
            user_status=SeriesUserStatus.WATCHING,
        )

        res = self.client.post(reverse("series_update_details", args=[series.id]), {
            "title": "Cosmic Chronicles",
            "overview": "Deep space odyssey.",
            "genres": "Sci-Fi, Adventure",
            "cast": "John Doe, Jane Doe",
            "total_seasons": 3,
            "total_episodes": 24,
        })
        self.assertEqual(res.status_code, 302)

        series.refresh_from_db()
        self.assertEqual(series.title, "Cosmic Chronicles")
        self.assertEqual(series.overview, "Deep space odyssey.")
        self.assertEqual(series.genres, "Sci-Fi, Adventure")
        self.assertEqual(series.cast, "John Doe, Jane Doe")
        self.assertEqual(series.total_seasons, 3)
        self.assertEqual(series.total_episodes, 24)

    def test_series_delete(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Show to delete",
            user_status=SeriesUserStatus.DROPPED,
        )
        SeasonEntry.objects.create(series=series, season_number=1, episode_count=8)

        res = self.client.post(reverse("series_delete", args=[series.id]))
        self.assertEqual(res.status_code, 302)
        self.assertFalse(SeriesEntry.objects.filter(id=series.id).exists())
        self.assertFalse(SeasonEntry.objects.filter(series_id=series.id).exists())

    def test_list_cards_link_to_detail(self):
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Severance Check",
            current_season_number=1,
            current_episode_number=1,
            user_status=SeriesUserStatus.WATCHING,
        )
        res = self.client.get(reverse("series_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, reverse("series_detail", args=[series.id]))
