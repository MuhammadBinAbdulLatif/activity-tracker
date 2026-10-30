from django.db import models
from django.contrib.auth.models import User

class BookStatus(models.TextChoices):
    PLAN_TO_READ = "PLAN_TO_READ", "Want to Read"
    READING = "READING", "Currently Reading"
    COMPLETED = "COMPLETED", "Completed"
    DROPPED = "DROPPED", "Dropped"

class BookFormat(models.TextChoices):
    HARDCOVER = "HARDCOVER", "Hardcover"
    PAPERBACK = "PAPERBACK", "Paperback"
    EBOOK = "EBOOK", "E-Book / Kindle"
    AUDIOBOOK = "AUDIOBOOK", "Audiobook"
    OTHER = "OTHER", "Other"

class BookEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="book_entries")
    openlibrary_key = models.CharField(max_length=100, blank=True, db_index=True)
    isbn = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, help_text="Author name(s)")
    publish_year = models.PositiveIntegerField(null=True, blank=True)
    page_count = models.PositiveIntegerField(default=0, help_text="Total pages")
    cover_url = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    genres = models.CharField(max_length=255, blank=True, help_text="Genres or subjects")

    # Personal Tracking
    status = models.CharField(
        max_length=20,
        choices=BookStatus.choices,
        default=BookStatus.PLAN_TO_READ,
        db_index=True
    )
    current_page = models.PositiveIntegerField(default=0, help_text="Current page read")
    book_format = models.CharField(
        max_length=20,
        choices=BookFormat.choices,
        default=BookFormat.PAPERBACK
    )
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Rating out of 10")
    review = models.TextField(blank=True, help_text="General review and overall thoughts")

    # Mind-Changing Insights & Journaling
    mind_changing_takeaways = models.TextField(
        blank=True,
        help_text="Key paradigm shifts, mind-changing insights, mental models, or actionable principles"
    )
    favorite_quotes = models.TextField(
        blank=True,
        help_text="Memorable quotes or passages from this book"
    )
    reread_count = models.PositiveIntegerField(default=0)

    # Custom Entry Handling
    is_custom = models.BooleanField(default=False)
    custom_cover = models.ImageField(upload_to="posters/books/%Y/%m/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Book Entry"
        verbose_name_plural = "Book Entries"

    def __str__(self):
        return f"{self.title} by {self.author or 'Unknown'} ({self.user.username})"

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
    def progress_percentage(self):
        if self.status == BookStatus.COMPLETED:
            return 100
        if not self.page_count or self.page_count <= 0:
            return 0
        pct = int((self.current_page / self.page_count) * 100)
        return min(100, max(0, pct))

    @property
    def authors_list(self):
        if not self.author:
            return []
        return [a.strip() for a in self.author.split(",") if a.strip()]
