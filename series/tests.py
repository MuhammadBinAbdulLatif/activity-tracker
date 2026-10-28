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
