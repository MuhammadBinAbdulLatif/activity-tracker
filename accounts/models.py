from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


SECURITY_QUESTION_CHOICES = [
    ("What was the name of your first pet?", "What was the name of your first pet?"),
    ("In what city were you born?", "In what city were you born?"),
    ("What is your mother's maiden name?", "What is your mother's maiden name?"),
    ("What was the name of your elementary school?", "What was the name of your elementary school?"),
    ("What was your childhood favorite movie?", "What was your childhood favorite movie?"),
    ("What was your first car model?", "What was your first car model?"),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    security_question = models.CharField(max_length=255)
    security_answer = models.CharField(
        max_length=255,
        help_text="Stored normalized (trimmed and lowercase) for case-insensitive verification."
    )

    def set_security_answer(self, raw_answer: str):
        self.security_answer = (raw_answer or "").strip().lower()

    def check_security_answer(self, candidate_answer: str) -> bool:
        normalized_candidate = (candidate_answer or "").strip().lower()
        return bool(self.security_answer and normalized_candidate == self.security_answer)

    def __str__(self):
        return f"Profile({self.user.username})"
