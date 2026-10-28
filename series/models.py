from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class SeriesUserStatus(models.TextChoices):
    WATCHING = "WATCHING", "Currently Watching"
    WAITING_FOR_NEXT_SEASON = "WAITING_FOR_NEXT_SEASON", "Waiting for Next Season"
    PLAN_TO_WATCH = "PLAN_TO_WATCH", "Plan to Watch"
    COMPLETED = "COMPLETED", "Completed"
    ON_HOLD = "ON_HOLD", "On Hold"
    DROPPED = "DROPPED", "Dropped"

class SeriesShowStatus(models.TextChoices):
    RETURNING = "Returning Series", "Returning Series"
    ENDED = "Ended", "Ended"
    CANCELED = "Canceled", "Canceled"
    IN_PRODUCTION = "In Production", "In Production"
    PILOT = "Pilot", "Pilot"

class SeriesEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="series_entries")
    tmdb_id = models.IntegerField(null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255)
    first_air_date = models.DateField(null=True, blank=True)
    poster_path = models.CharField(max_length=500, blank=True)
    backdrop_path = models.CharField(max_length=500, blank=True)
    overview = models.TextField(blank=True)
    genres = models.CharField(max_length=255, blank=True)
    show_status = models.CharField(max_length=50, choices=SeriesShowStatus.choices, default=SeriesShowStatus.RETURNING)
    
    total_seasons = models.PositiveIntegerField(default=1)
    total_episodes = models.PositiveIntegerField(default=0)

    # Tracking Progress State
    user_status = models.CharField(
        max_length=30,
        choices=SeriesUserStatus.choices,
        default=SeriesUserStatus.PLAN_TO_WATCH,
        db_index=True
    )
    current_season_number = models.PositiveIntegerField(default=1)
    current_episode_number = models.PositiveIntegerField(default=0)
    
    # Broadcast and Schedule Awareness (synced from TMDB)
    next_episode_air_date = models.DateField(null=True, blank=True)
    next_episode_name = models.CharField(max_length=255, blank=True)
    next_episode_season_num = models.PositiveIntegerField(null=True, blank=True)
    next_episode_ep_num = models.PositiveIntegerField(null=True, blank=True)
    last_air_date = models.DateField(null=True, blank=True)

    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    review = models.TextField(blank=True)
    is_custom = models.BooleanField(default=False)
    custom_poster = models.ImageField(upload_to="posters/series/%Y/%m/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Series Entry"
        verbose_name_plural = "Series Entries"

    def __str__(self):
        return f"{self.title} - S{self.current_season_number}E{self.current_episode_number} ({self.user.username})"

    @property
    def poster_url(self):
        if self.custom_poster:
            try:
                return self.custom_poster.url
            except Exception:
                pass
        if self.poster_path:
            if self.poster_path.startswith("http"):
                return self.poster_path
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=400&q=80"

    @property
    def has_new_episode_aired(self):
        """Returns True if an episode aired within the last 7 days and user is watching"""
        if self.user_status == SeriesUserStatus.WATCHING and self.last_air_date:
            today = timezone.now().date()
            return self.last_air_date <= today and (today - self.last_air_date).days <= 7
        return False

    @property
    def upcoming_episode_days_away(self):
        """Returns number of days until next episode airs if known"""
        if self.next_episode_air_date:
            today = timezone.now().date()
            delta = (self.next_episode_air_date - today).days
            if delta >= 0:
                return delta
        return None

class SeasonEntry(models.Model):
    series = models.ForeignKey(SeriesEntry, on_delete=models.CASCADE, related_name="seasons")
    season_number = models.PositiveIntegerField()
    name = models.CharField(max_length=255, blank=True)
    episode_count = models.PositiveIntegerField(default=0)
    air_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["season_number"]
        unique_together = ("series", "season_number")

    def __str__(self):
        return f"{self.series.title} - Season {self.season_number}"

class EpisodeLog(models.Model):
    series = models.ForeignKey(SeriesEntry, on_delete=models.CASCADE, related_name="episode_logs")
    season_number = models.PositiveIntegerField()
    episode_number = models.PositiveIntegerField()
    watched_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-watched_at"]

    def __str__(self):
        return f"{self.series.title} S{self.season_number}E{self.episode_number} at {self.watched_at.strftime('%Y-%m-%d')}"
