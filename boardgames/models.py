from django.db import models
from django.contrib.auth.models import User


class BoardGameStatus(models.TextChoices):
    PLAYED = "PLAYED", "Played"
    OWNED = "OWNED", "Owned / On Shelf"
    WANT_TO_PLAY = "WANT_TO_PLAY", "Want to Play"
    WISHLIST = "WISHLIST", "Wishlist"
    TRADED_AWAY = "TRADED_AWAY", "Traded Away"


class BoardGameEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boardgame_entries")

    # External Provider (BGG) Metadata
    external_id = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255)
    cover_url = models.CharField(max_length=1000, blank=True)
    custom_cover = models.ImageField(upload_to="boardgames/covers/", null=True, blank=True)
    description = models.TextField(blank=True)
    year_published = models.PositiveSmallIntegerField(null=True, blank=True)

    # Credits & Taxonomies
    designers = models.CharField(max_length=500, blank=True)
    publishers = models.CharField(max_length=500, blank=True)
    categories = models.CharField(max_length=500, blank=True)
    mechanics = models.CharField(max_length=500, blank=True)

    # Game Characteristics
    min_players = models.PositiveSmallIntegerField(null=True, blank=True)
    max_players = models.PositiveSmallIntegerField(null=True, blank=True)
    min_playtime = models.PositiveSmallIntegerField(null=True, blank=True)
    max_playtime = models.PositiveSmallIntegerField(null=True, blank=True)

    # BGG Community Scores
    bgg_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    bgg_rank = models.PositiveIntegerField(null=True, blank=True)

    # Tracking & Play Logs
    status = models.CharField(
        max_length=20,
        choices=BoardGameStatus.choices,
        default=BoardGameStatus.WANT_TO_PLAY
    )
    play_count = models.PositiveIntegerField(default=0, blank=True)
    last_played = models.DateField(null=True, blank=True)
    avg_session_minutes = models.PositiveIntegerField(null=True, blank=True)
    favorite_players = models.CharField(max_length=255, blank=True)

    # Rating & Personal Notes
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    review = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Board Game Entry"
        verbose_name_plural = "Board Game Entries"

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    # ------------------------------------------------------------------ #
    # Computed Properties
    # ------------------------------------------------------------------ #

    @property
    def display_cover(self) -> str:
        """Returns the best available cover image URL."""
        if self.custom_cover:
            return self.custom_cover.url
        return self.cover_url or ""

    @property
    def player_count_display(self) -> str:
        """Human-readable player count, e.g. '2–4 players' or '2 players'."""
        if self.min_players is not None and self.max_players is not None:
            if self.min_players == self.max_players:
                return f"{self.min_players} player" if self.min_players == 1 else f"{self.min_players} players"
            return f"{self.min_players}–{self.max_players} players"
        elif self.min_players is not None:
            return f"{self.min_players}+ players"
        elif self.max_players is not None:
            return f"Up to {self.max_players} players"
        return "Players unlisted"

    @property
    def playtime_display(self) -> str:
        """Human-readable playtime, e.g. '30–90 min' or '60 min'."""
        if self.min_playtime is not None and self.max_playtime is not None:
            if self.min_playtime == self.max_playtime:
                return f"{self.min_playtime} min"
            return f"{self.min_playtime}–{self.max_playtime} min"
        elif self.min_playtime is not None:
            return f"{self.min_playtime}+ min"
        elif self.max_playtime is not None:
            return f"Up to {self.max_playtime} min"
        return "Playtime unlisted"

    @property
    def status_badge_class(self) -> str:
        """Tailwind CSS badge styling per specs/styles.md."""
        mapping = {
            BoardGameStatus.PLAYED: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40",
            BoardGameStatus.OWNED: "bg-zinc-800 text-zinc-300 border border-zinc-700",
            BoardGameStatus.WANT_TO_PLAY: "bg-blue-500/10 text-blue-400 border border-blue-500/30",
            BoardGameStatus.WISHLIST: "bg-purple-500/10 text-purple-400 border border-purple-500/30",
            BoardGameStatus.TRADED_AWAY: "bg-zinc-900/60 text-zinc-600 border border-zinc-800",
        }
        return mapping.get(self.status, "bg-zinc-800 text-zinc-300 border border-zinc-700")

    @property
    def total_hours_played(self) -> str:
        """Estimated total hours spent playing."""
        if self.play_count and self.avg_session_minutes:
            total_mins = self.play_count * self.avg_session_minutes
            hours = round(total_mins / 60.0, 1)
            return f"{hours}h"
        return "0h"
