import io
from PIL import Image
from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from audiobooks.models import AudiobookEntry, AudiobookStatus

class AudiobookTrackingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="audio_listener", password="testpassword123")
        self.client.login(username="audio_listener", password="testpassword123")

    def _generate_test_image(self):
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color=(180, 120, 60))
        image.save(file, "jpeg")
        file.seek(0)
        return SimpleUploadedFile("test_audio_cover.jpg", file.read(), content_type="image/jpeg")

    def test_audiobook_list_requires_login(self):
        self.client.logout()
        res = self.client.get(reverse("audiobook_list"))
        self.assertEqual(res.status_code, 302)
        self.assertIn("/accounts/login/", res.url)

    def test_audiobook_list_renders_empty(self):
        res = self.client.get(reverse("audiobook_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Audiobooks")
        self.assertContains(res, "Add Audiobook")

    @patch("services.audiobook_service.audiobook_service.search_audiobooks")
    def test_search_audiobooks_excludes_dropped_and_deleted(self, mock_search):
        mock_search.return_value = {
            "results": [
                {"external_id": "1001", "title": "Active Audio", "author": "Author A", "narrator": "Narrator A"},
                {"external_id": "1002", "title": "Dropped Audio", "author": "Author B", "narrator": "Narrator B"},
                {"external_id": "1003", "title": "Deleted Audio", "author": "Author C", "narrator": "Narrator C"},
            ]
        }
        # 1001 is actively listening
        AudiobookEntry.objects.create(user=self.user, external_id="1001", title="Active Audio", status=AudiobookStatus.LISTENING)
        # 1002 is dropped
        AudiobookEntry.objects.create(user=self.user, external_id="1002", title="Dropped Audio", status=AudiobookStatus.DROPPED)
        # 1003 is not in DB / deleted

        res = self.client.get(reverse("audiobook_search") + "?q=Audio")
        self.assertEqual(res.status_code, 200)
        data = res.json()["results"]
        result_map = {item["external_id"]: item["is_tracked"] for item in data}
        self.assertTrue(result_map["1001"])
        self.assertFalse(result_map["1002"])
        self.assertFalse(result_map["1003"])

    def test_add_custom_audiobook(self):
        image = self._generate_test_image()
        res = self.client.post(reverse("audiobook_add"), {
            "title": "Project Hail Mary",
            "author": "Andy Weir",
            "narrator": "Ray Porter",
            "duration_hours": "16",
            "duration_mins": "10",
            "status": AudiobookStatus.LISTENING,
            "playback_speed": "1.25",
            "cover_file": image,
        })
        self.assertEqual(res.status_code, 302)
        ab = AudiobookEntry.objects.filter(user=self.user, title="Project Hail Mary").first()
        self.assertIsNotNone(ab)
        self.assertEqual(ab.narrator, "Ray Porter")
        self.assertEqual(ab.duration_minutes, 970)
        self.assertEqual(ab.duration_display, "16h 10m")
        self.assertEqual(float(ab.playback_speed), 1.25)
        self.assertTrue(ab.is_custom)
        self.assertTrue(ab.custom_cover.name.startswith("posters/audiobooks/"))

    def test_update_audiobook_details(self):
        ab = AudiobookEntry.objects.create(
            user=self.user,
            title="Born a Crime",
            author="Trevor Noah",
            narrator="Trevor Noah",
            duration_minutes=530,
            status=AudiobookStatus.PLAN_TO_LISTEN
        )

        res = self.client.post(reverse("audiobook_update_details", args=[ab.id]), {
            "status": AudiobookStatus.COMPLETED,
            "rating": "9.5",
            "narrator_rating": "10.0",
            "duration_minutes": "530",
            "current_progress_minutes": "530",
            "playback_speed": "1.50",
            "review": "Trevor Noah's voice acting and accents are phenomenal.",
            "mind_changing_takeaways": "Humor can be the greatest survival mechanism through racial segregation.",
            "favorite_quotes": "We spend so much time being afraid of failure...",
            "finish_date": "2026-10-28",
        })
        self.assertEqual(res.status_code, 302)
        ab.refresh_from_db()
        self.assertEqual(ab.status, AudiobookStatus.COMPLETED)
        self.assertEqual(float(ab.rating), 9.5)
        self.assertEqual(float(ab.narrator_rating), 10.0)
        self.assertEqual(float(ab.playback_speed), 1.50)
        self.assertEqual(ab.progress_percentage, 100)
        self.assertIn("Trevor Noah", ab.review)
        self.assertIn("survival mechanism", ab.mind_changing_takeaways)

    def test_update_audiobook_progress_stepper(self):
        ab = AudiobookEntry.objects.create(
            user=self.user,
            title="Dune Audio",
            narrator="Scott Brick & Cast",
            duration_minutes=1260,
            current_progress_minutes=60,
            status=AudiobookStatus.LISTENING
        )

        # Step +30 minutes
        self.client.post(reverse("audiobook_update_progress", args=[ab.id]), {"step": "30"})
        ab.refresh_from_db()
        self.assertEqual(ab.current_progress_minutes, 90)

        # Step to completion
        self.client.post(reverse("audiobook_update_progress", args=[ab.id]), {"progress_minutes": "1260"})
        ab.refresh_from_db()
        self.assertEqual(ab.current_progress_minutes, 1260)
        self.assertEqual(ab.status, AudiobookStatus.COMPLETED)
        self.assertIsNotNone(ab.finish_date)

    def test_delete_audiobook(self):
        ab = AudiobookEntry.objects.create(
            user=self.user,
            title="Audiobook to Delete",
            status=AudiobookStatus.PLAN_TO_LISTEN
        )
        res = self.client.post(reverse("audiobook_delete", args=[ab.id]))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse("audiobook_list"), res.url)
        self.assertFalse(AudiobookEntry.objects.filter(id=ab.id).exists())
