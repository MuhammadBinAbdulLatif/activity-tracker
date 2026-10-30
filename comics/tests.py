from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from .models import ComicMangaEntry, ComicMangaType, ComicMangaStatus


class ComicMangaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="otaku_reader", password="password123")
        self.client = Client()
        self.client.login(username="otaku_reader", password="password123")

        self.manga = ComicMangaEntry.objects.create(
            user=self.user,
            external_id="anilist-30002",
            item_type=ComicMangaType.MANGA,
            title="Berserk",
            original_title="ベルセルク",
            creator_author="Kentaro Miura",
            artist="Kentaro Miura",
            publisher="Hakusensha",
            total_chapters=364,
            total_volumes=41,
            current_chapter=100,
            current_volume=14,
            status=ComicMangaStatus.READING,
            rating=10.0,
            art_rating=10.0,
            favorite_arc_or_issue="Golden Age Arc"
        )

        self.comic = ComicMangaEntry.objects.create(
            user=self.user,
            external_id="comicvine-4050-1234",
            item_type=ComicMangaType.COMIC,
            title="Watchmen",
            creator_author="Alan Moore",
            artist="Dave Gibbons",
            publisher="DC Comics",
            total_chapters=12,
            total_volumes=1,
            current_chapter=0,
            current_volume=0,
            status=ComicMangaStatus.PLAN_TO_READ,
        )

    def test_comic_list_view(self):
        response = self.client.get(reverse("comic_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Berserk")
        self.assertContains(response, "Watchmen")
        self.assertContains(response, "Currently Reading")
        self.assertContains(response, "Plan to Read")

    def test_comic_type_filter(self):
        # Filter for Manga
        res_manga = self.client.get(reverse("comic_list") + "?type=MANGA")
        self.assertEqual(res_manga.status_code, 200)
        self.assertContains(res_manga, "Berserk")
        self.assertNotContains(res_manga, "Watchmen")

        # Filter for Comics
        res_comic = self.client.get(reverse("comic_list") + "?type=COMIC")
        self.assertEqual(res_comic.status_code, 200)
        self.assertContains(res_comic, "Watchmen")
        self.assertNotContains(res_comic, "Berserk")

    def test_comic_detail_view(self):
        response = self.client.get(reverse("comic_detail", args=[self.manga.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kentaro Miura")
        self.assertContains(response, "Golden Age Arc")
        self.assertContains(response, "10.0")

    def test_update_comic_progress(self):
        url = reverse("comic_update_progress", args=[self.manga.id])
        response = self.client.post(url, {"delta_chapter": "5"})
        self.assertEqual(response.status_code, 302)
        self.manga.refresh_from_db()
        self.assertEqual(self.manga.current_chapter, 105)

    def test_progress_auto_complete(self):
        url = reverse("comic_update_progress", args=[self.comic.id])
        # Increment to total chapters (12)
        response = self.client.post(url, {"delta_chapter": "12"})
        self.assertEqual(response.status_code, 302)
        self.comic.refresh_from_db()
        self.assertEqual(self.comic.current_chapter, 12)
        self.assertEqual(self.comic.status, ComicMangaStatus.COMPLETED)
        self.assertIsNotNone(self.comic.finish_date)

    def test_add_comic_manual(self):
        url = reverse("comic_add")
        payload = {
            "title": "Saga",
            "item_type": "COMIC",
            "creator_author": "Brian K. Vaughan",
            "artist": "Fiona Staples",
            "publisher": "Image Comics",
            "total_chapters": "60",
            "status": "PLAN_TO_READ"
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ComicMangaEntry.objects.filter(title="Saga", user=self.user).exists())

    @patch("services.comic_manga_service.ComicMangaService.search_all")
    def test_search_comics_excludes_dropped(self, mock_search):
        mock_search.return_value = [
            {
                "external_id": "anilist-30002",
                "title": "Berserk",
                "item_type": "MANGA",
                "creator_author": "Kentaro Miura",
                "source": "AniList"
            },
            {
                "external_id": "anilist-99999",
                "title": "Chainsaw Man",
                "item_type": "MANGA",
                "creator_author": "Tatsuki Fujimoto",
                "source": "AniList"
            }
        ]

        response = self.client.get(reverse("comic_search") + "?q=test")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data["results"]
        # Berserk is tracked and active (status READING), so is_tracked should be True
        berserk_res = next(r for r in results if r["external_id"] == "anilist-30002")
        self.assertTrue(berserk_res["is_tracked"])

        # Chainsaw Man is not tracked
        csm_res = next(r for r in results if r["external_id"] == "anilist-99999")
        self.assertFalse(csm_res["is_tracked"])

        # If Berserk is dropped, is_tracked becomes False
        self.manga.status = ComicMangaStatus.DROPPED
        self.manga.save()

        response2 = self.client.get(reverse("comic_search") + "?q=test")
        results2 = response2.json()["results"]
        berserk_res2 = next(r for r in results2 if r["external_id"] == "anilist-30002")
        self.assertFalse(berserk_res2["is_tracked"])

    def test_delete_comic(self):
        url = reverse("comic_delete", args=[self.manga.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ComicMangaEntry.objects.filter(id=self.manga.id).exists())
