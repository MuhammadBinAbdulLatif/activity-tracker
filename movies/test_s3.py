import io
import os
from PIL import Image
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from movies.models import MovieEntry, MovieStatus
from series.models import SeriesEntry, SeriesUserStatus

class S3CloudStorageLiveTests(TestCase):
    """
    Automated integration test verifying S3 storage backend operations:
    saving, URL generation, reading, file deletion, and model image attachment.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="s3_tester", password="testpassword123")

    def _generate_test_image(self, filename="poster_test.jpg"):
        file = io.BytesIO()
        image = Image.new("RGB", (120, 120), color=(34, 197, 94))
        image.save(file, "jpeg")
        file.seek(0)
        return SimpleUploadedFile(filename, file.read(), content_type="image/jpeg")

    def test_s3_storage_save_read_delete(self):
        """Tests low-level default_storage round-trip on S3"""
        content = b"uTrack S3 Live Cloud Storage Verification Byte Payload"
        filename = "s3_tests/verification_file.txt"

        saved_path = default_storage.save(filename, ContentFile(content))
        self.assertTrue(default_storage.exists(saved_path))

        # Check URL generation
        file_url = default_storage.url(saved_path)
        self.assertIn("utrack", file_url)
        self.assertIn("verification_file", file_url)

        # Read back content
        with default_storage.open(saved_path) as f:
            read_bytes = f.read()
        self.assertEqual(read_bytes, content)

        # Cleanup
        default_storage.delete(saved_path)
        self.assertFalse(default_storage.exists(saved_path))

    def test_movie_model_custom_poster_s3_lifecycle(self):
        """Tests MovieEntry model saving custom poster file to S3 and resolving URL"""
        test_img = self._generate_test_image("movie_s3_poster.jpg")
        movie = MovieEntry.objects.create(
            user=self.user,
            title="S3 Cloud Movie Test",
            status=MovieStatus.WATCHING,
            custom_poster=test_img,
            is_custom=True
        )

        self.assertIsNotNone(movie.custom_poster)
        self.assertTrue(default_storage.exists(movie.custom_poster.name))
        
        # Verify poster_url property returns the live S3 URL
        poster_url = movie.poster_url
        self.assertIn("192.168.2.103:3900", poster_url)
        self.assertIn("utrack", poster_url)
        self.assertTrue(poster_url.endswith(".jpg"))

        # Cleanup
        storage_path = movie.custom_poster.name
        movie.delete()
        default_storage.delete(storage_path)

    def test_series_model_custom_poster_s3_lifecycle(self):
        """Tests SeriesEntry model saving custom poster file to S3 and resolving URL"""
        test_img = self._generate_test_image("series_s3_poster.jpg")
        series = SeriesEntry.objects.create(
            user=self.user,
            title="S3 Cloud Series Test",
            user_status=SeriesUserStatus.WATCHING,
            custom_poster=test_img,
            is_custom=True
        )

        self.assertIsNotNone(series.custom_poster)
        self.assertTrue(default_storage.exists(series.custom_poster.name))

        poster_url = series.poster_url
        self.assertIn("192.168.2.103:3900", poster_url)
        self.assertIn("utrack", poster_url)

        # Cleanup
        storage_path = series.custom_poster.name
        series.delete()
        default_storage.delete(storage_path)
