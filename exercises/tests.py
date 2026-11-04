from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from decimal import Decimal

from .models import (
    Exercise,
    ExerciseLog,
    UserExerciseTrack,
    ExerciseTrackingStatus,
    ExerciseCategory,
    MuscleGroup,
    EquipmentType,
)


class ExerciseModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fitnessuser", password="secretpassword123")

    def test_seed_exercises_exist(self):
        bench = Exercise.objects.filter(name="Barbell Bench Press").first()
        self.assertIsNotNone(bench)
        self.assertEqual(bench.category, ExerciseCategory.STRENGTH)
        self.assertTrue(bench.is_resistance_type)
        self.assertFalse(bench.is_cardio_type)

        running = Exercise.objects.filter(name="Outdoor Running / Jogging").first()
        self.assertIsNotNone(running)
        self.assertEqual(running.category, ExerciseCategory.CARDIO)
        self.assertTrue(running.is_cardio_type)
        self.assertFalse(running.is_resistance_type)

    def test_user_exercise_tracking_shelves(self):
        bench = Exercise.objects.get(name="Barbell Bench Press")
        track = UserExerciseTrack.objects.create(
            user=self.user,
            exercise=bench,
            status=ExerciseTrackingStatus.IN_PROGRESS,
            personal_goal="Bench 100kg",
        )
        self.assertEqual(track.status, ExerciseTrackingStatus.IN_PROGRESS)
        self.assertEqual(track.user, self.user)
        self.assertEqual(track.exercise, bench)

    def test_exercise_log_and_stats(self):
        squat = Exercise.objects.get(name="Barbell Back Squat")
        log1 = ExerciseLog.objects.create(
            user=self.user,
            exercise=squat,
            logged_date=date(2026, 11, 1),
            sets=4,
            reps=8,
            weight_kg=Decimal("100.00"),
            rpe=8,
        )
        self.assertEqual(log1.weight_kg, Decimal("100.00"))


class ExerciseViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="athlete", password="password123")
        self.client.login(username="athlete", password="password123")

    def test_exercise_list_view_shelves(self):
        # Add bench to in_progress
        bench = Exercise.objects.get(name="Barbell Bench Press")
        UserExerciseTrack.objects.create(
            user=self.user,
            exercise=bench,
            status=ExerciseTrackingStatus.IN_PROGRESS,
        )

        response = self.client.get(reverse("exercise_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "exercises/list.html")
        self.assertEqual(response.context["in_progress"].count(), 1)
        self.assertEqual(response.context["planned"].count(), 0)
        self.assertEqual(response.context["completed"].count(), 0)

    def test_search_catalog_modal(self):
        response = self.client.get(reverse("search_catalog_modal"), {"q": "Bench"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "exercises/partials/catalog_search_results.html")
        results = response.context["results"]
        self.assertTrue(len(results) > 0)
        self.assertTrue(any("Bench" in r["exercise"].name for r in results))

    def test_track_and_untrack_exercise(self):
        bench = Exercise.objects.get(name="Barbell Bench Press")
        # Track exercise
        response = self.client.post(reverse("track_exercise", kwargs={"exercise_id": bench.id}), {
            "status": "PLANNED",
            "personal_goal": "Start training bench next month",
        })
        self.assertEqual(response.status_code, 302)
        track = UserExerciseTrack.objects.filter(user=self.user, exercise=bench).first()
        self.assertIsNotNone(track)
        self.assertEqual(track.status, ExerciseTrackingStatus.PLANNED)

        # Update status
        self.client.post(reverse("update_track_status", kwargs={"track_id": track.id}), {
            "status": "IN_PROGRESS",
        })
        track.refresh_from_db()
        self.assertEqual(track.status, ExerciseTrackingStatus.IN_PROGRESS)

        # Untrack
        self.client.post(reverse("untrack_exercise", kwargs={"track_id": track.id}))
        self.assertFalse(UserExerciseTrack.objects.filter(pk=track.id).exists())

    def test_exercise_log_form_tailoring(self):
        bench = Exercise.objects.get(name="Barbell Bench Press")
        running = Exercise.objects.get(name="Outdoor Running / Jogging")

        # GET detail view for bench
        resp_bench = self.client.get(reverse("exercise_detail", kwargs={"slug": bench.slug}))
        self.assertEqual(resp_bench.status_code, 200)
        self.assertTrue(resp_bench.context["is_resistance"])
        self.assertFalse(resp_bench.context["is_cardio"])

        # GET detail view for running
        resp_run = self.client.get(reverse("exercise_detail", kwargs={"slug": running.slug}))
        self.assertEqual(resp_run.status_code, 200)
        self.assertTrue(resp_run.context["is_cardio"])
        self.assertFalse(resp_run.context["is_resistance"])

    def test_create_custom_exercise_view(self):
        payload = {
            "name": "Hex Bar Neutral Grip Deadlift",
            "category": "STRENGTH",
            "target_muscle_group": "HAMSTRINGS",
            "equipment": "BARBELL",
            "status": "IN_PROGRESS",
        }
        response = self.client.post(reverse("exercise_create"), payload)
        self.assertEqual(response.status_code, 302)

        created = Exercise.objects.filter(name="Hex Bar Neutral Grip Deadlift").first()
        self.assertIsNotNone(created)
        self.assertTrue(created.is_custom)
        # Check auto-shelved
        track = UserExerciseTrack.objects.filter(user=self.user, exercise=created).first()
        self.assertIsNotNone(track)
        self.assertEqual(track.status, ExerciseTrackingStatus.IN_PROGRESS)
