from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from books.models import BookEntry, BookStatus, BookFormat
from unittest.mock import patch

class BookModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testreader", password="password123")

    def test_book_defaults_and_properties(self):
        book = BookEntry.objects.create(
            user=self.user,
            title="Atomic Habits",
            author="James Clear",
            page_count=320,
            current_page=160,
        )
        self.assertEqual(book.status, BookStatus.PLAN_TO_READ)
        self.assertEqual(book.book_format, BookFormat.PAPERBACK)
        self.assertEqual(book.progress_percentage, 50)
        self.assertEqual(book.authors_list, ["James Clear"])
        self.assertIn("Atomic Habits", str(book))

    def test_progress_percentage_bounds(self):
        book = BookEntry.objects.create(
            user=self.user,
            title="Zero Page Book",
            page_count=0,
            current_page=0,
        )
        self.assertEqual(book.progress_percentage, 0)

        book.page_count = 100
        book.current_page = 150
        self.assertEqual(book.progress_percentage, 100)

        book.status = BookStatus.COMPLETED
        book.current_page = 20
        self.assertEqual(book.progress_percentage, 100)

class BookServiceMockTest(TestCase):
    @patch("urllib.request.urlopen")
    def test_openlibrary_service_search(self, mock_urlopen):
        import json
        from io import BytesIO
        from services.openlibrary import openlibrary_service

        mock_payload = {
            "docs": [
                {
                    "key": "/works/OL12345W",
                    "title": "Mock Book",
                    "author_name": ["Author One", "Author Two"],
                    "first_publish_year": 2021,
                    "number_of_pages_median": 350,
                    "cover_i": 99999,
                    "isbn": ["1234567890"],
                    "subject": ["Psychology", "Self-Help"],
                }
            ]
        }
        
        class MockResponse:
            status = 200
            def read(self):
                return json.dumps(mock_payload).encode("utf-8")
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass

        mock_urlopen.return_value = MockResponse()

        res = openlibrary_service.search_books("Mock Query")
        self.assertEqual(len(res["results"]), 1)
        item = res["results"][0]
        self.assertEqual(item["title"], "Mock Book")
        self.assertEqual(item["author"], "Author One, Author Two")
        self.assertEqual(item["publish_year"], 2021)
        self.assertEqual(item["page_count"], 350)
        self.assertIn("99999", item["cover_url"])

class BookViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="booklover", password="secretpassword")
        self.client.login(username="booklover", password="secretpassword")

    def test_book_list_view(self):
        BookEntry.objects.create(user=self.user, title="Reading Book", status=BookStatus.READING, current_page=50, page_count=200)
        BookEntry.objects.create(user=self.user, title="Completed Book", status=BookStatus.COMPLETED, page_count=300, current_page=300)
        BookEntry.objects.create(user=self.user, title="Wishlist Book", status=BookStatus.PLAN_TO_READ)

        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reading Book")
        self.assertContains(response, "Completed Book")
        self.assertContains(response, "Wishlist Book")
        self.assertEqual(response.context["total_pages_read"], 350)
        self.assertEqual(response.context["total_books_read"], 1)

    def test_add_manual_book(self):
        response = self.client.post(reverse("add_book"), {
            "title": "Meditations",
            "author": "Marcus Aurelius",
            "status": BookStatus.READING,
            "book_format": BookFormat.HARDCOVER,
            "page_count": 250,
            "current_page": 25,
            "mind_changing_takeaways": "You have power over your mind - not outside events.",
            "favorite_quotes": "Waste no more time arguing about what a good man should be. Be one.",
        })
        book = BookEntry.objects.filter(user=self.user, title="Meditations").first()
        self.assertIsNotNone(book)
        self.assertEqual(book.author, "Marcus Aurelius")
        self.assertEqual(book.book_format, BookFormat.HARDCOVER)
        self.assertEqual(book.mind_changing_takeaways, "You have power over your mind - not outside events.")
        self.assertRedirects(response, reverse("book_detail", kwargs={"book_id": book.id}))

    def test_book_detail_and_update(self):
        book = BookEntry.objects.create(
            user=self.user,
            title="Deep Work",
            author="Cal Newport",
            page_count=300,
            current_page=100,
            status=BookStatus.READING
        )

        detail_response = self.client.get(reverse("book_detail", kwargs={"book_id": book.id}))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Deep Work")
        self.assertContains(detail_response, "Cal Newport")

        # Update details
        update_response = self.client.post(reverse("update_book_details", kwargs={"book_id": book.id}), {
            "status": BookStatus.COMPLETED,
            "book_format": BookFormat.EBOOK,
            "current_page": 300,
            "page_count": 300,
            "rating": "9.5",
            "mind_changing_takeaways": "Clarity about what matters provides clarity about what does not.",
            "favorite_quotes": "If you don't produce, you won't thrive.",
            "review": "Essential reading for high output knowledge work.",
            "reread_count": "1",
        })
        self.assertRedirects(update_response, reverse("book_detail", kwargs={"book_id": book.id}))

        book.refresh_from_db()
        self.assertEqual(book.status, BookStatus.COMPLETED)
        self.assertEqual(book.book_format, BookFormat.EBOOK)
        self.assertEqual(float(book.rating), 9.5)
        self.assertEqual(book.reread_count, 1)
        self.assertIsNotNone(book.finish_date)

    def test_update_book_progress_stepper(self):
        book = BookEntry.objects.create(
            user=self.user,
            title="Dune",
            page_count=600,
            current_page=50,
            status=BookStatus.READING
        )

        # Step +10
        self.client.post(reverse("update_book_progress", kwargs={"book_id": book.id}), {"step": "10"})
        book.refresh_from_db()
        self.assertEqual(book.current_page, 60)

        # Step beyond page count auto-completes
        self.client.post(reverse("update_book_progress", kwargs={"book_id": book.id}), {"page": "600"})
        book.refresh_from_db()
        self.assertEqual(book.current_page, 600)
        self.assertEqual(book.status, BookStatus.COMPLETED)

    def test_delete_book(self):
        book = BookEntry.objects.create(
            user=self.user,
            title="To Be Deleted",
        )
        response = self.client.post(reverse("delete_book", kwargs={"book_id": book.id}))
        self.assertRedirects(response, reverse("book_list"))
        self.assertFalse(BookEntry.objects.filter(id=book.id).exists())

    @patch("services.openlibrary.openlibrary_service.search_books")
    def test_search_books_excludes_dropped_and_deleted(self, mock_search):
        mock_search.return_value = {
            "results": [
                {"openlibrary_key": "/works/OL100W", "title": "Active Book", "author": "Author A"},
                {"openlibrary_key": "/works/OL200W", "title": "Dropped Book", "author": "Author B"},
                {"openlibrary_key": "/works/OL300W", "title": "Deleted Book", "author": "Author C"},
            ]
        }
        # OL100W is active
        BookEntry.objects.create(user=self.user, openlibrary_key="/works/OL100W", title="Active Book", status=BookStatus.READING)
        # OL200W is dropped
        BookEntry.objects.create(user=self.user, openlibrary_key="/works/OL200W", title="Dropped Book", status=BookStatus.DROPPED)
        # OL300W is not tracked / deleted

        res = self.client.get(reverse("search_books") + "?q=Book")
        self.assertEqual(res.status_code, 200)
        data = res.json()["results"]
        result_map = {item["openlibrary_key"]: item["is_tracked"] for item in data}
        self.assertTrue(result_map["/works/OL100W"])
        self.assertFalse(result_map["/works/OL200W"])
        self.assertFalse(result_map["/works/OL300W"])
