from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from decimal import Decimal

from .models import Exercise, ExerciseLog, ExerciseCategory, MuscleGroup, EquipmentType
from .seed_data import POPULAR_EXERCISES


class ExerciseModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fitnessuser", password="secretpassword123")

    def test_seed_exercises_exist(self):
        """Verify standard popular exercises are present in the database."""
        bench = Exercise.objects.filter(name="Barbell Bench Press").first()
        self.assertIsNotNone(bench)
        self.assertEqual(bench.category, ExerciseCategory.STRENGTH)
        self.assertEqual(bench.target_muscle_group, MuscleGroup.CHEST)
        self.assertEqual(bench.equipment, EquipmentType.BARBELL)
        self.assertFalse(bench.is_custom)

        # Check a cardio exercise
        running = Exercise.objects.filter(name="Outdoor Running / Jogging").first()
        self.assertIsNotNone(running)
        self.assertEqual(running.category, ExerciseCategory.CARDIO)

    def test_custom_exercise_creation(self):
        """Verify user can create a custom exercise."""
        custom_ex = Exercise.objects.create(
            name="Incline Smith Machine Hex Press",
            category=ExerciseCategory.STRENGTH,
            target_muscle_group=MuscleGroup.CHEST,
            equipment=EquipmentType.MACHINE,
            instructions="Squeeze dumbbells or machine handles together during pressing.",
            is_custom=True,
            created_by=self.user,
        )
        self.assertTrue(custom_ex.is_custom)
        self.assertEqual(custom_ex.created_by, self.user)
        self.assertTrue(custom_ex.slug.startswith("incline-smith-machine-hex-press"))

    def test_exercise_log_creation_and_stats(self):
        """Verify exercise logging functionality with weights, sets, reps, and PR calculation."""
        squat = Exercise.objects.get(name="Barbell Back Squat")
        log1 = ExerciseLog.objects.create(
            user=self.user,
            exercise=squat,
            logged_date=date(2026, 11, 1),
            sets=4,
            reps=8,
            weight_kg=Decimal("100.00"),
            rpe=8,
            notes="Felt smooth",
        )
        log2 = ExerciseLog.objects.create(
            user=self.user,
            exercise=squat,
            logged_date=date(2026, 11, 4),
            sets=3,
            reps=5,
            weight_kg=Decimal("120.00"),
            rpe=9,
            notes="New PR!",
        )

        logs = ExerciseLog.objects.filter(user=self.user, exercise=squat)
        self.assertEqual(logs.count(), 2)
        # Order should be newest first
        self.assertEqual(logs.first().pk, log2.pk)


class ExerciseViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="athlete", password="password123")
        self.other_user = User.objects.create_user(username="other", password="password123")
        self.client.login(username="athlete", password="password123")

    def test_exercise_list_view_requires_login(self):
        anonymous_client = Client()
        response = anonymous_client.get(reverse("exercise_list"))
        self.assertEqual(response.status_code, 302)

    def test_exercise_list_view_success(self):
        response = self.client.get(reverse("exercise_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "exercises/list.html")
        self.assertIn("exercises", response.context)
        self.assertGreaterEqual(response.context["total_exercises_count"], 60)

    def test_exercise_search_and_filter(self):
        # Search by query
        response = self.client.get(reverse("exercise_list"), {"q": "Deadlift"})
        self.assertEqual(response.status_code, 200)
        exercise_names = [e.name for e in response.context["exercises"]]
        self.assertTrue(any("Deadlift" in name for name in exercise_names))

        # Filter by muscle group
        response_chest = self.client.get(reverse("exercise_list"), {"muscle": "CHEST"})
        self.assertEqual(response_chest.status_code, 200)
        for ex in response_chest.context["exercises"]:
            self.assertEqual(ex.target_muscle_group, "CHEST")

    def test_exercise_detail_view(self):
        bench = Exercise.objects.get(name="Barbell Bench Press")
        response = self.client.get(reverse("exercise_detail", kwargs={"slug": bench.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "exercises/detail.html")
        self.assertEqual(response.context["exercise"], bench)

    def test_create_custom_exercise_view(self):
        payload = {
            "name": "Deficit Sumo Deadlift",
            "category": "STRENGTH",
            "target_muscle_group": "HAMSTRINGS",
            "equipment": "BARBELL",
            "secondary_muscles": "Glutes, Adductors",
            "instructions": "Stand on 2-inch platform, wide sumo stance.",
        }
        response = self.client.post(reverse("exercise_create"), payload)
        self.assertEqual(response.status_code, 302)

        created = Exercise.objects.filter(name="Deficit Sumo Deadlift").first()
        self.assertIsNotNone(created)
        self.assertTrue(created.is_custom)
        self.assertEqual(created.created_by, self.user)

    def test_log_exercise_view(self):
        pullup = Exercise.objects.get(name="Pull-Ups")
        payload = {
            "logged_date": "2026-11-04",
            "sets": 4,
            "reps": 12,
            "weight_kg": "0.0",
            "rpe": 7,
            "notes": "Strict bodyweight form",
        }
        response = self.client.post(reverse("exercise_log_create", kwargs={"slug": pullup.slug}), payload)
        self.assertEqual(response.status_code, 302)

        log = ExerciseLog.objects.filter(user=self.user, exercise=pullup).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.sets, 4)
        self.assertEqual(log.reps, 12)

    def test_delete_exercise_log(self):
        pullup = Exercise.objects.get(name="Pull-Ups")
        log = ExerciseLog.objects.create(
            user=self.user,
            exercise=pullup,
            logged_date=date(2026, 11, 4),
            sets=3,
            reps=10,
        )
        response = self.client.post(reverse("exercise_log_delete", kwargs={"pk": log.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ExerciseLog.objects.filter(pk=log.pk).exists())
