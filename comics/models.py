from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class ComicMangaType(models.TextChoices):
    COMIC = "COMIC", "Comic / Graphic Novel"
    MANGA = "MANGA", "Manga / Manhwa / Manhua"
    LIGHT_NOVEL = "LIGHT_NOVEL", "Light Novel"


class ComicMangaStatus(models.TextChoices):
    PLAN_TO_READ = "PLAN_TO_READ", "Plan to Read"
    READING = "READING", "Currently Reading"
    COMPLETED = "COMPLETED", "Completed"
    ON_HOLD = "ON_HOLD", "On Hold"
    DROPPED = "DROPPED", "Dropped"


class ComicMangaEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comic_entries")
    external_id = models.CharField(max_length=100, blank=True, db_index=True)
    item_type = models.CharField(
        max_length=20,
        choices=ComicMangaType.choices,
        default=ComicMangaType.MANGA
    )
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    creator_author = models.CharField(max_length=255, blank=True, help_text="Writer / Mangaka")
    artist = models.CharField(max_length=255, blank=True, help_text="Illustrator / Inker / Colorist")
    publisher = models.CharField(max_length=255, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    
    # Progress & Counts
    total_chapters = models.PositiveIntegerField(default=0, help_text="Total serialized chapters or issues")
    total_volumes = models.PositiveIntegerField(default=0, help_text="Total compiled volumes / TPBs")
    current_chapter = models.PositiveIntegerField(default=0, help_text="Last chapter read")
    current_volume = models.PositiveIntegerField(default=0, help_text="Last volume read")

    # Cover
    cover_url = models.CharField(max_length=1000, blank=True)
    custom_cover = models.ImageField(upload_to="comics/covers/", null=True, blank=True)

    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=ComicMangaStatus.choices,
        default=ComicMangaStatus.PLAN_TO_READ
    )

    # Ratings
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)],
        help_text="Overall Story & Character Rating (1-10)"
    )
    art_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)],
        help_text="Art & Linework Quality Rating (1-10)"
    )

    # Reflections & Highlights
    review = models.TextField(blank=True)
    favorite_arc_or_issue = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    # Tracking Dates & Reliving
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    reread_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Comic / Manga Entry"
        verbose_name_plural = "Comic & Manga Entries"

    def __str__(self):
        return f"{self.title} ({self.get_item_type_display()}) - {self.user.username}"

    @property
    def display_cover(self) -> str:
        """Returns custom uploaded cover if available; otherwise returns external cover URL."""
        if self.custom_cover:
            try:
                return self.custom_cover.url
            except Exception:
                pass
        return self.cover_url or ""

    @property
    def progress_percentage(self) -> int:
        """Calculates completion progress percentage based on chapters (or volumes if no chapters)."""
        if self.total_chapters and self.total_chapters > 0:
            pct = int((self.current_chapter / self.total_chapters) * 100)
            return min(pct, 100)
        elif self.total_volumes and self.total_volumes > 0:
            pct = int((self.current_volume / self.total_volumes) * 100)
            return min(pct, 100)
        elif self.status == ComicMangaStatus.COMPLETED:
            return 100
        return 0

    @property
    def progress_display(self) -> str:
        """Formatted string indicating current reading progress."""
        if self.total_chapters > 0:
            return f"Ch. {self.current_chapter} / {self.total_chapters}"
        elif self.total_volumes > 0:
            return f"Vol. {self.current_volume} / {self.total_volumes}"
        elif self.current_chapter > 0:
            return f"Ch. {self.current_chapter}"
        elif self.current_volume > 0:
            return f"Vol. {self.current_volume}"
        return "Not Started"
