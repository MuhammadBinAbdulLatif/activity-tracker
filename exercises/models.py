from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class ExerciseCategory(models.TextChoices):
    STRENGTH = "STRENGTH", "Strength & Hypertrophy"
    BODYWEIGHT = "BODYWEIGHT", "Bodyweight & Calisthenics"
    CARDIO = "CARDIO", "Cardiovascular & Endurance"
    OLYMPIC = "OLYMPIC", "Olympic & Powerlifting"
    MOBILITY = "MOBILITY", "Mobility, Flexibility & Core"


class MuscleGroup(models.TextChoices):
    CHEST = "CHEST", "Chest"
    BACK = "BACK", "Back"
    SHOULDERS = "SHOULDERS", "Shoulders"
    BICEPS = "BICEPS", "Biceps"
    TRICEPS = "TRICEPS", "Triceps"
    FOREARMS = "FOREARMS", "Forearms"
    QUADS = "QUADS", "Quadriceps"
    HAMSTRINGS = "HAMSTRINGS", "Hamstrings"
    GLUTES = "GLUTES", "Glutes"
    CALVES = "CALVES", "Calves"
    CORE = "CORE", "Core & Abs"
    FULL_BODY = "FULL_BODY", "Full Body"
    CARDIO = "CARDIO", "Cardiovascular System"


class EquipmentType(models.TextChoices):
    BARBELL = "BARBELL", "Barbell"
    DUMBBELL = "DUMBBELL", "Dumbbell"
    BODYWEIGHT = "BODYWEIGHT", "Bodyweight / Calisthenics"
    CABLE = "CABLE", "Cable Machine"
    MACHINE = "MACHINE", "Gym Machine"
    KETTLEBELL = "KETTLEBELL", "Kettlebell"
    BAND = "BAND", "Resistance Band"
    CARDIO_MACHINE = "CARDIO_MACHINE", "Cardio Machine"
    OTHER = "OTHER", "Other / None"


class ExerciseTrackingStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "Active / In Routine"
    PLANNED = "PLANNED", "Planned / Want to Try"
    COMPLETED = "COMPLETED", "Mastered / Completed Target"


class Exercise(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    category = models.CharField(
        max_length=30,
        choices=ExerciseCategory.choices,
        default=ExerciseCategory.STRENGTH,
    )
    target_muscle_group = models.CharField(
        max_length=30,
        choices=MuscleGroup.choices,
        default=MuscleGroup.FULL_BODY,
    )
    secondary_muscles = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secondary muscles engaged, comma-separated.",
    )
    equipment = models.CharField(
        max_length=30,
        choices=EquipmentType.choices,
        default=EquipmentType.BODYWEIGHT,
    )
    instructions = models.TextField(
        blank=True,
        help_text="Step-by-step form cues and technique guidance.",
    )
    is_custom = models.BooleanField(
        default=False,
        help_text="True if created by a specific user rather than the global catalog.",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="custom_exercises",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Exercise"
        verbose_name_plural = "Exercises"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Exercise.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_cardio_type(self):
        return self.category == ExerciseCategory.CARDIO or self.target_muscle_group == MuscleGroup.CARDIO or self.equipment == EquipmentType.CARDIO_MACHINE

    @property
    def is_resistance_type(self):
        return self.category in [ExerciseCategory.STRENGTH, ExerciseCategory.BODYWEIGHT, ExerciseCategory.OLYMPIC] or self.equipment in [EquipmentType.BARBELL, EquipmentType.DUMBBELL, EquipmentType.CABLE, EquipmentType.MACHINE, EquipmentType.KETTLEBELL]


class UserExerciseTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exercise_tracks")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="user_tracks")
    status = models.CharField(
        max_length=20,
        choices=ExerciseTrackingStatus.choices,
        default=ExerciseTrackingStatus.IN_PROGRESS,
        db_index=True,
    )
    personal_goal = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g., Reach 100kg Bench, Run 5km under 25m, or Master 15 clean reps",
    )
    frequency_per_week = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Target frequency per week")
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    personal_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ("user", "exercise")
        verbose_name = "User Exercise Track"
        verbose_name_plural = "User Exercise Tracks"

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} [{self.get_status_display()}]"


class ExerciseLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exercise_logs")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="logs")
    logged_date = models.DateField()
    
    # Resistance / Strength Metrics (Shown only for lifting/bodyweight/machines)
    sets = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Number of completed sets")
    reps = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Reps per set or total reps")
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Weight lifted in kg")

    # Cardio / Endurance Metrics (Shown only for cardio/aerobic exercises)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Session duration in minutes")
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Distance covered in km")
    calories_burned = models.PositiveIntegerField(null=True, blank=True, help_text="Estimated calories burned")

    # Subjective metrics & Notes
    rpe = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Rate of Perceived Exertion (1 to 10)")
    notes = models.TextField(blank=True, help_text="Personal notes, form reflections, or cues.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-logged_date", "-created_at"]
        verbose_name = "Exercise Log"
        verbose_name_plural = "Exercise Logs"

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} ({self.logged_date})"
