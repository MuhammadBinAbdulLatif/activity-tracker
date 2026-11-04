from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from decimal import Decimal

from movies.models import MovieEntry, MovieStatus
from series.models import SeriesEntry, SeriesUserStatus, EpisodeLog
from books.models import BookEntry, BookStatus
from games.models import GameEntry, GameStatus
from exercises.models import Exercise, UserExerciseTrack, ExerciseTrackingStatus, ExerciseLog


class DashboardRealDataTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="chronicle_user",
            email="chronicle@example.com",
            password="testpassword123"
        )
        self.client.login(username="chronicle_user", password="testpassword123")

    def test_dashboard_requires_login(self):
        anon_client = Client()
        response = anon_client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_empty_user_dashboard(self):
        """Newly created user with zero records gets clean 200 OK and zero metrics without crashing."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/home.html")
        self.assertEqual(response.context["metrics"]["active_streak_days"], 0)
        self.assertEqual(response.context["metrics"]["total_items_year"], 0)
        self.assertEqual(response.context["metrics"]["hours_consumed_month"], 0)
        self.assertEqual(len(response.context["in_progress"]), 0)
        self.assertEqual(len(response.context["planned_queue"]), 0)
        self.assertEqual(len(response.context["recently_finished"]), 0)

    def test_real_data_aggregation(self):
        """User with active movie, series, book, and exercise sees real data reflected."""
        # 1. Active Series
        series = SeriesEntry.objects.create(
            user=self.user,
            title="Severance",
            total_episodes=10,
            current_season_number=2,
            current_episode_number=5,
            user_status=SeriesUserStatus.WATCHING,
        )

        # 2. Completed Movie with Rating
        movie = MovieEntry.objects.create(
            user=self.user,
            title="Dune Part Two",
            status=MovieStatus.COMPLETED,
            watch_date=date.today(),
            rating=Decimal("4.5"),
            review="Phenomenal sci-fi masterpiece.",
            runtime=166,
        )

        # 3. Planned Book
        book = BookEntry.objects.create(
            user=self.user,
            title="Project Hail Mary",
            author="Andy Weir",
            status=BookStatus.PLAN_TO_READ,
        )

        # 4. In-progress Exercise Track & Log
        ex = Exercise.objects.get(name="Barbell Bench Press")
        track = UserExerciseTrack.objects.create(
            user=self.user,
            exercise=ex,
            status=ExerciseTrackingStatus.IN_PROGRESS,
            personal_goal="Hit 100kg",
        )
        ExerciseLog.objects.create(
            user=self.user,
            exercise=ex,
            logged_date=date.today(),
            sets=4,
            reps=8,
            weight_kg=Decimal("80.0"),
            duration_minutes=45,
        )

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        # Verify In-Progress contains Severance and Bench Press
        ip_titles = [item["title"] for item in response.context["in_progress"]]
        self.assertIn("Severance", ip_titles)
        self.assertIn("Barbell Bench Press", ip_titles)

        # Verify Planned contains Project Hail Mary
        pl_titles = [item["title"] for item in response.context["planned_queue"]]
        self.assertIn("Project Hail Mary", pl_titles)

        # Verify Recently Completed contains Dune Part Two
        rf_titles = [item["title"] for item in response.context["recently_finished"]]
        self.assertIn("Dune Part Two", rf_titles)

        # Verify Metrics
        self.assertGreaterEqual(response.context["metrics"]["active_streak_days"], 1)
        self.assertGreaterEqual(response.context["metrics"]["total_items_year"], 1)
        self.assertGreaterEqual(response.context["metrics"]["hours_consumed_month"], 2.0)

    def test_user_data_isolation(self):
        """User A cannot see User B's entries."""
        other_user = User.objects.create_user(
            username="other_person",
            password="secretpassword"
        )
        MovieEntry.objects.create(
            user=other_user,
            title="Secret Alien Movie",
            status=MovieStatus.WATCHING,
        )

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Secret Alien Movie")
