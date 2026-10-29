from django.db import models
from django.contrib.auth.models import User

class MovieStatus(models.TextChoices):
    PLAN_TO_WATCH = "PLAN_TO_WATCH", "Plan to Watch"
    WATCHING = "WATCHING", "Currently Watching"
    COMPLETED = "COMPLETED", "Completed"
    DROPPED = "DROPPED", "Dropped"

class MovieEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="movie_entries")
    tmdb_id = models.IntegerField(null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(null=True, blank=True)
    runtime = models.PositiveIntegerField(default=0, help_text="Runtime in minutes")
    poster_path = models.CharField(max_length=500, blank=True)
    backdrop_path = models.CharField(max_length=500, blank=True)
    overview = models.TextField(blank=True)
    genres = models.CharField(max_length=255, blank=True, help_text="Comma-separated genres")
    director = models.CharField(max_length=255, blank=True)
    cast = models.TextField(blank=True, help_text="Comma-separated or listed actors/cast")
    tagline = models.CharField(max_length=500, blank=True)

    # Personal Tracking Details
    status = models.CharField(
        max_length=20,
        choices=MovieStatus.choices,
        default=MovieStatus.PLAN_TO_WATCH,
        db_index=True
    )
    watch_date = models.DateField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Rating out of 10")
    review = models.TextField(blank=True)
    rewatch_count = models.PositiveIntegerField(default=0)
    is_custom = models.BooleanField(default=False)
    custom_poster = models.ImageField(upload_to="posters/movies/%Y/%m/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Movie Entry"
        verbose_name_plural = "Movie Entries"

    def __str__(self):
        return f"{self.title} ({self.user.username})"

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
        return "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=400&q=80"

    @property
    def backdrop_url(self):
        if self.backdrop_path:
            if self.backdrop_path.startswith("http"):
                return self.backdrop_path
            return f"https://image.tmdb.org/t/p/w1280{self.backdrop_path}"
        return self.poster_url

    @property
    def cast_list(self):
        """Returns clean list of actor names"""
        if not self.cast:
            return []
        # Support either comma or newline separation
        items = [name.strip() for name in self.cast.replace("\n", ",").split(",") if name.strip()]
        return items[:12]
