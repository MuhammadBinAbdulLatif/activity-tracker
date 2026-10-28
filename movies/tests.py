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
    def test_add_movie_from_tmdb(self, mock_get_details):
        mock_get_details.return_value = {
            "id": 693134,
            "title": "Dune: Part Two",
            "original_title": "Dune: Part Two",
            "release_date": "2024-03-01",
            "runtime": 166,
            "poster_path": "/czembW0Rk1Ke7lCJGhk4TGmm54v.jpg",
            "overview": "Paul Atreides unites with Chani and the Fremen...",
            "genres": [{"id": 878, "name": "Sci-Fi"}],
            "credits": {"crew": [{"job": "Director", "name": "Denis Villeneuve"}]}
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

    def test_add_custom_movie_with_image_upload(self):
        test_image = self._generate_test_image()
        res = self.client.post(reverse("movie_add"), {
            "title": "My S3 Custom Movie",
            "director": "Christopher Nolan",
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
        self.assertIsNotNone(movie.custom_poster)
        self.assertTrue(movie.poster_url.endswith(".jpg"))

    def test_update_movie_status(self):
        movie = MovieEntry.objects.create(
            user=self.user,
            title="Oppenheimer",
            status=MovieStatus.PLAN_TO_WATCH
        )
        res = self.client.post(reverse("movie_update_status", args=[movie.id]), {
            "status": "COMPLETED"
        })
        self.assertEqual(res.status_code, 302)
        movie.refresh_from_db()
        self.assertEqual(movie.status, MovieStatus.COMPLETED)
        self.assertIsNotNone(movie.watch_date)

    def test_rewatch_movie(self):
        movie = MovieEntry.objects.create(
            user=self.user,
            title="Interstellar",
            status=MovieStatus.COMPLETED,
            rewatch_count=1
        )
        res = self.client.post(reverse("movie_rewatch", args=[movie.id]))
        self.assertEqual(res.status_code, 302)
        movie.refresh_from_db()
        self.assertEqual(movie.rewatch_count, 2)
