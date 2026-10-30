from django.db import models
from django.contrib.auth.models import User

class AudiobookStatus(models.TextChoices):
    PLAN_TO_LISTEN = "PLAN_TO_LISTEN", "Plan to Listen"
    LISTENING = "LISTENING", "Currently Listening"
    COMPLETED = "COMPLETED", "Completed"
    DROPPED = "DROPPED", "Dropped"

class AudiobookEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="audiobook_entries")
    external_id = models.CharField(max_length=100, blank=True, db_index=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, help_text="Author name")
    narrator = models.CharField(max_length=255, blank=True, default="Narrator Unlisted", help_text="Narrator / Performer name")
    
    # Audio Length and Listening Tracking
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Total audio length in minutes")
    current_progress_minutes = models.PositiveIntegerField(default=0, help_text="Listening progress in minutes")
    playback_speed = models.DecimalField(max_digits=3, decimal_places=2, default=1.00, help_text="Listening speed (e.g. 1.0, 1.25, 1.5, 2.0)")

    # Artwork and Audio Preview
    cover_url = models.CharField(max_length=500, blank=True)
    custom_cover = models.ImageField(upload_to="posters/audiobooks/%Y/%m/", blank=True, null=True)
    preview_audio_url = models.CharField(max_length=500, blank=True, help_text="30s-90s audio preview stream")
    
    # Metadata
    genre = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    release_year = models.PositiveIntegerField(null=True, blank=True)
    is_custom = models.BooleanField(default=False)

    # Personal Reflections & Rating
    status = models.CharField(
        max_length=20,
        choices=AudiobookStatus.choices,
        default=AudiobookStatus.PLAN_TO_LISTEN,
        db_index=True,
    )
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Content/Book rating (1-10)")
    narrator_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Narration performance rating (1-10)")
    review = models.TextField(blank=True, help_text="Personal thoughts on story and narration")
    mind_changing_takeaways = models.TextField(blank=True, help_text="Core paradigm shifts and insights")
    favorite_quotes = models.TextField(blank=True, help_text="Memorable quotes or spoken passages")

    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    relive_count = models.PositiveIntegerField(default=0, help_text="Number of re-listens")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Audiobook Entry"
        verbose_name_plural = "Audiobook Entries"

    def __str__(self):
        return f"{self.title} - Narrated by {self.narrator} ({self.user.username})"

    @property
    def display_cover(self):
        if self.custom_cover:
            try:
                return self.custom_cover.url
            except Exception:
                pass
        if self.cover_url:
            return self.cover_url
        return "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80"

    @property
    def progress_percentage(self) -> int:
        if self.status == AudiobookStatus.COMPLETED:
            return 100
        if not self.duration_minutes or self.duration_minutes <= 0:
            return 0
        pct = int((self.current_progress_minutes / self.duration_minutes) * 100)
        return min(max(pct, 0), 100)

    @property
    def duration_display(self) -> str:
        if not self.duration_minutes:
            return "Duration TBA"
        hours = self.duration_minutes // 60
        mins = self.duration_minutes % 60
        if hours > 0 and mins > 0:
            return f"{hours}h {mins}m"
        elif hours > 0:
            return f"{hours}h"
        return f"{mins}m"

    @property
    def current_progress_display(self) -> str:
        hours = self.current_progress_minutes // 60
        mins = self.current_progress_minutes % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    @property
    def time_remaining_display(self) -> str:
        if not self.duration_minutes or self.current_progress_minutes >= self.duration_minutes:
            return "0m"
        rem = self.duration_minutes - self.current_progress_minutes
        hours = rem // 60
        mins = rem % 60
        if hours > 0:
            return f"{hours}h {mins}m left"
        return f"{mins}m left"
