from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="testpassword123"
        )

    def test_dashboard_requires_login(self):
        """Unauthenticated user is redirected to login page"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_renders_for_logged_in_user(self):
        """Authenticated user gets 200 OK and dashboard template"""
        self.client.login(username="tester", password="testpassword123")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/home.html")
        self.assertTemplateUsed(response, "dashboard/sidebar.html")
        self.assertContains(response, "Welcome back, tester")

    def test_sidebar_contains_all_media_links(self):
        """Sidebar includes Books, Audiobooks, Movies, Series, Comics, and Exercises"""
        self.client.login(username="tester", password="testpassword123")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Verify media category links (using html=False or exact string)
        self.assertContains(response, "Movies")
        self.assertContains(response, "Series & TV", html=False)
        self.assertContains(response, "Books")
        self.assertContains(response, "Audiobooks")
        self.assertContains(response, "Comics & Manga", html=False)
        self.assertContains(response, "Games")
        self.assertContains(response, "Board Games")
        self.assertContains(response, "Exercises & Habits", html=False)

    def test_sidebar_profile_and_breaker(self):
        """Sidebar contains divider breaker, user username, settings link, and logout form"""
        self.client.login(username="tester", password="testpassword123")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, "tester")
        self.assertContains(response, "Settings")
        self.assertContains(response, "Sign Out")
        self.assertContains(response, 'border-t border-zinc-800')

    def test_heatmap_and_in_progress_data(self):
        """Dashboard renders heatmap data, in-progress items, planned items, and recently finished"""
        self.client.login(username="tester", password="testpassword123")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        # Check context
        self.assertIn("heatmap_weeks", response.context)
        self.assertEqual(len(response.context["heatmap_weeks"]), 52)
        self.assertIn("in_progress", response.context)
        self.assertIn("planned_queue", response.context)
        self.assertIn("recently_finished", response.context)

        # Check in-progress titles
        self.assertContains(response, "Severance")
        self.assertContains(response, "Dune: Part Two")
        self.assertContains(response, "Project Hail Mary")
        self.assertContains(response, "Atomic Habits")
        self.assertContains(response, "Berserk")
        self.assertContains(response, "Elden Ring")
        self.assertContains(response, "Brass: Birmingham")
        self.assertContains(response, "5K Strength")
