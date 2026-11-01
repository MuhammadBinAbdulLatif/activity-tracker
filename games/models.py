from django.db import models
from django.contrib.auth.models import User


class GameStatus(models.TextChoices):
    PLAYING = "PLAYING", "Currently Playing"
    COMPLETED = "COMPLETED", "Completed"
    ON_HOLD = "ON_HOLD", "On Hold"
    DROPPED = "DROPPED", "Dropped"
    BACKLOG = "BACKLOG", "Backlog / Plan to Play"


class GameEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_entries")

    # Provider metadata
    external_id = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255)
    cover_url = models.CharField(max_length=1000, blank=True)
    custom_cover = models.ImageField(upload_to="games/covers/", null=True, blank=True)
    description = models.TextField(blank=True)
    release_year = models.PositiveSmallIntegerField(null=True, blank=True)
    developers = models.CharField(max_length=500, blank=True)
    publishers = models.CharField(max_length=500, blank=True)
    genres = models.CharField(max_length=500, blank=True)

    # Platform info
    platforms_available = models.CharField(max_length=500, blank=True, help_text="All platforms the game ships on")
    platform_played = models.CharField(max_length=100, blank=True, help_text="Platform this user played on")

    # Tracking
    status = models.CharField(max_length=20, choices=GameStatus.choices, default=GameStatus.BACKLOG)
    hours_played = models.DecimalField(max_digits=6, decimal_places=1, default=0.0)
    completion_percentage = models.PositiveSmallIntegerField(default=0)

    # Rating & review
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    review = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Dates
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Game Entry"
        verbose_name_plural = "Game Entries"

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    # ------------------------------------------------------------------ #
    # Computed properties
    # ------------------------------------------------------------------ #

    @property
    def display_cover(self) -> str:
        """Returns the best available cover URL."""
        if self.custom_cover:
            return self.custom_cover.url
        return self.cover_url or ""

    @property
    def hours_display(self) -> str:
        """Human-readable hours string, e.g. '12.5h'."""
        return f"{self.hours_played}h"

    @property
    def completion_display(self) -> str:
        """Human-readable completion string, e.g. '75%'."""
        return f"{self.completion_percentage}%"

    @property
    def status_badge_class(self) -> str:
        """CSS classes for the status badge per styles.md."""
        mapping = {
            GameStatus.PLAYING: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40",
            GameStatus.COMPLETED: "bg-zinc-800 text-zinc-300 border border-zinc-700",
            GameStatus.BACKLOG: "bg-blue-500/10 text-blue-400 border border-blue-500/30",
            GameStatus.ON_HOLD: "bg-yellow-500/10 text-yellow-400 border border-yellow-500/30",
            GameStatus.DROPPED: "bg-red-950/40 text-red-400 border border-red-800/40",
        }
        return mapping.get(self.status, "bg-zinc-800 text-zinc-300 border border-zinc-700")
