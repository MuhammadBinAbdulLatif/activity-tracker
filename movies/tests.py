import io
from PIL import Image
from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import MovieEntry, MovieStatus

class MovieTrackingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="film_fan", password="testpassword123")
        self.client.login(username="film_fan", password="testpassword123")

    def _generate_test_image(self):
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color=(73, 109, 137))
        image.save(file, "jpeg")
        file.seek(0)
        return SimpleUploadedFile("test_poster.jpg", file.read(), content_type="image/jpeg")

    def test_movie_list_requires_login(self):
        self.client.logout()
        res = self.client.get(reverse("movie_list"))
        self.assertEqual(res.status_code, 302)
        self.assertIn("/accounts/login/", res.url)

    def test_movie_list_renders_empty_with_prominent_buttons(self):
        res = self.client.get(reverse("movie_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Movies")
        self.assertContains(res, "bg-emerald-500")

    @patch("services.tmdb.tmdb_service.get_movie_details")
    def test_add_movie_from_tmdb_and_redirect_to_detail(self, mock_get_details):
        mock_get_details.return_value = {
            "id": 693134,
            "title": "Dune: Part Two",
            "original_title": "Dune: Part Two",
            "release_date": "2024-03-01",
            "runtime": 166,
            "poster_path": "/czembW0Rk1Ke7lCJGhk4TGmm54v.jpg",
            "overview": "Paul Atreides unites with Chani and the Fremen...",
            "genres": [{"id": 878, "name": "Sci-Fi"}],
            "credits": {
                "crew": [{"job": "Director", "name": "Denis Villeneuve"}],
                "cast": [{"name": "Timothée Chalamet"}, {"name": "Zendaya"}]
            }
        }

        res = self.client.post(reverse("movie_add"), {
            "tmdb_id": "693134",
            "status": "WATCHING"
        })
        self.assertEqual(res.status_code, 302)
        
        movie = MovieEntry.objects.filter(user=self.user, tmdb_id=693134).first()
        self.assertIsNotNone(movie)
        self.assertEqual(movie.title, "Dune: Part Two")
        self.assertEqual(movie.director, "Denis Villeneuve")
        self.assertEqual(movie.runtime, 166)
        self.assertEqual(movie.status, MovieStatus.WATCHING)
        self.assertIn("Timothée Chalamet", movie.cast)
        self.assertIn(reverse("movie_detail", args=[movie.id]), res.url)

    def test_add_custom_movie_with_image_upload(self):
        test_image = self._generate_test_image()
        res = self.client.post(reverse("movie_add"), {
            "title": "My S3 Custom Movie",
            "director": "Christopher Nolan",
            "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt",
            "runtime": "150",
            "status": "COMPLETED",
            "rating": "9.5",
            "review": "A masterpiece of independent cinema.",
            "poster_file": test_image,
        })
        self.assertEqual(res.status_code, 302)

        movie = MovieEntry.objects.filter(user=self.user, title="My S3 Custom Movie").first()
        self.assertIsNotNone(movie)
        self.assertTrue(movie.is_custom)
        self.assertEqual(movie.runtime, 150)
        self.assertEqual(movie.status, MovieStatus.COMPLETED)
        self.assertIn("Leonardo DiCaprio", movie.cast)
        self.assertIsNotNone(movie.custom_poster)
        self.assertTrue(movie.poster_url.endswith(".jpg"))

    def test_movie_detail_view_rendering(self):
        movie = MovieEntry.objects.create(
            user=self.user,
            title="Inception",
            director="Christopher Nolan",
            cast="Leonardo DiCaprio, Marion Cotillard, Elliot Page",
            runtime=148,
            overview="A thief who steals corporate secrets through the use of dream-sharing technology...",
            status=MovieStatus.WATCHING,
            rating=9.0
        )
        res = self.client.get(reverse("movie_detail", args=[movie.id]))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "movies/detail.html")
        self.assertContains(res, "Inception")
        self.assertContains(res, "Christopher Nolan")
        self.assertContains(res, "Leonardo DiCaprio")
        self.assertContains(res, "Marion Cotillard")
        self.assertContains(res, "148 mins")

    def test_movie_status_reversion_completed_to_plan_to_watch(self):
        """Tests reverting from Completed back to Plan to Watch and clearing watch date"""
        movie = MovieEntry.objects.create(
            user=self.user,
            title="Accidentally Marked Watched",
            status=MovieStatus.COMPLETED,
            watch_date=timezone.now().date()
        )
        # User changes status back to Plan to Watch
        res = self.client.post(reverse("movie_update_details", args=[movie.id]), {
            "status": MovieStatus.PLAN_TO_WATCH,
            "rating": "",
            "review": "",
        })
        self.assertEqual(res.status_code, 302)
        movie.refresh_from_db()
        self.assertEqual(movie.status, MovieStatus.PLAN_TO_WATCH)
        self.assertIsNone(movie.watch_date)

    def test_movie_update_personal_log(self):
        movie = MovieEntry.objects.create(
            user=self.user,
            title="The Dark Knight",
            status=MovieStatus.PLAN_TO_WATCH
        )
        res = self.client.post(reverse("movie_update_details", args=[movie.id]), {
            "status": MovieStatus.COMPLETED,
            "rating": "9.8",
            "watch_date": "2026-10-25",
            "rewatch_count": "3",
            "review": "Heath Ledger's Joker is legendary.",
        })
        self.assertEqual(res.status_code, 302)
        movie.refresh_from_db()
        self.assertEqual(movie.status, MovieStatus.COMPLETED)
        self.assertEqual(float(movie.rating), 9.8)
        self.assertEqual(movie.rewatch_count, 3)
        self.assertIn("Heath Ledger", movie.review)

    def test_movie_delete(self):
        movie = MovieEntry.objects.create(
            user=self.user,
            title="Movie to Delete",
            status=MovieStatus.PLAN_TO_WATCH
        )
        res = self.client.post(reverse("movie_delete", args=[movie.id]))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse("movie_list"), res.url)
        self.assertFalse(MovieEntry.objects.filter(id=movie.id).exists())

    def test_list_cards_link_to_detail(self):
        movie = MovieEntry.objects.create(
            user=self.user,
            title="Interstellar",
            status=MovieStatus.PLAN_TO_WATCH
        )
        res = self.client.get(reverse("movie_list"))
        self.assertEqual(res.status_code, 200)
        detail_url = reverse("movie_detail", args=[movie.id])
        self.assertContains(res, f'href="{detail_url}"')
