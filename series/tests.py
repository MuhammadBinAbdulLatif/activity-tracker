from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import SeriesEntry, SeasonEntry, EpisodeLog, SeriesUserStatus, SeriesShowStatus
from .engine import SeriesProgressionEngine

class SeriesTrackingAndEngineTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="series_binger", password="testpassword123")
        self.client.login(username="series_binger", password="testpassword123")

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
        """
        When completing the final episode of Season 1, if Season 2 exists,
        advance automatically to Season 2 Episode 0 (ready for Ep 1).
        """
        series = SeriesEntry.objects.create(
            user=self.user,
            title="House of the Dragon",
            current_season_number=1,
            current_episode_number=9,
            user_status=SeriesUserStatus.WATCHING
        )
        # Season 1 has 10 episodes
        SeasonEntry.objects.create(series=series, season_number=1, episode_count=10)
        # Season 2 has 8 episodes
        SeasonEntry.objects.create(series=series, season_number=2, episode_count=8)

        # Advance to episode 10 (season finale)
        result = SeriesProgressionEngine.advance_episode(series)
        series.refresh_from_db()

        self.assertEqual(series.current_season_number, 2)
        self.assertEqual(series.current_episode_number, 0)
        self.assertEqual(series.user_status, SeriesUserStatus.WATCHING)
        self.assertIn("Advanced automatically to Season 2", result["message"])

        # Check season 1 marked completed
        s1 = SeasonEntry.objects.get(series=series, season_number=1)
        self.assertTrue(s1.is_completed)

    def test_upcoming_season_waiting_state(self):
        """
        When finishing current season and next season is announced but in the future,
        series transitions to WAITING_FOR_NEXT_SEASON.
        """
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Stranger Things",
            current_season_number=4,
            current_episode_number=8,
            show_status=SeriesShowStatus.RETURNING,
            user_status=SeriesUserStatus.WATCHING
        )
        SeasonEntry.objects.create(series=series, season_number=4, episode_count=9)
        # Season 5 announced with air date next year
        next_year = timezone.now().date() + timedelta(days=200)
        SeasonEntry.objects.create(series=series, season_number=5, episode_count=8, air_date=next_year)

        result = SeriesProgressionEngine.advance_episode(series)
        series.refresh_from_db()

        self.assertEqual(series.user_status, SeriesUserStatus.WAITING_FOR_NEXT_SEASON)
        self.assertIn("Waiting for Season 5", result["message"])

    def test_ended_series_full_completion(self):
        """
        When finishing final episode of final season of an Ended show,
        series transitions to COMPLETED.
        """
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

    def test_broadcast_airing_status_properties(self):
        """
        Verifies has_new_episode_aired and upcoming_episode_days_away logic.
        """
        today = timezone.now().date()
        series = SeriesEntry.objects.create(
            user=self.user,
            title="The Penguin",
            last_air_date=today - timedelta(days=2), # aired 2 days ago
            next_episode_air_date=today + timedelta(days=5), # airs in 5 days
            user_status=SeriesUserStatus.WATCHING
        )

        self.assertTrue(series.has_new_episode_aired)
        self.assertEqual(series.upcoming_episode_days_away, 5)
