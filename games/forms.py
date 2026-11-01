from django import forms
from .models import GameEntry, GameStatus


class GameEntryForm(forms.ModelForm):
    """
    Full game entry form for manual creation and the detail-modal update.
    """

    class Meta:
        model = GameEntry
        fields = [
            "title",
            "status",
            "platform_played",
            "hours_played",
            "completion_percentage",
            "rating",
            "review",
            "notes",
            "start_date",
            "finish_date",
            "custom_cover",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none "
                         "focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition-colors",
                "placeholder": "Game title",
            }),
            "status": forms.Select(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 text-sm focus:outline-none focus:border-zinc-500 "
                         "focus:ring-1 focus:ring-zinc-500 transition-colors",
            }),
            "platform_played": forms.TextInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none "
                         "focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition-colors",
                "placeholder": "e.g. PC, PS5, Xbox Series X, Switch",
            }),
            "hours_played": forms.NumberInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 text-sm focus:outline-none focus:border-zinc-500 "
                         "focus:ring-1 focus:ring-zinc-500 transition-colors",
                "step": "0.5",
                "min": "0",
            }),
            "completion_percentage": forms.NumberInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 text-sm focus:outline-none focus:border-zinc-500 "
                         "focus:ring-1 focus:ring-zinc-500 transition-colors",
                "min": "0",
                "max": "100",
            }),
            "rating": forms.NumberInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 text-sm focus:outline-none focus:border-zinc-500 "
                         "focus:ring-1 focus:ring-zinc-500 transition-colors",
                "step": "0.1",
                "min": "1",
                "max": "10",
                "placeholder": "1.0 – 10.0",
            }),
            "review": forms.Textarea(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none "
                         "focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition-colors",
                "rows": 3,
                "placeholder": "Your review…",
            }),
            "notes": forms.Textarea(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none "
                         "focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition-colors",
                "rows": 2,
                "placeholder": "Private notes…",
            }),
            "start_date": forms.DateInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 text-sm focus:outline-none focus:border-zinc-500 "
                         "focus:ring-1 focus:ring-zinc-500 transition-colors",
                "type": "date",
            }),
            "finish_date": forms.DateInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
                         "text-zinc-100 text-sm focus:outline-none focus:border-zinc-500 "
                         "focus:ring-1 focus:ring-zinc-500 transition-colors",
                "type": "date",
            }),
        }

    def clean_completion_percentage(self):
        value = self.cleaned_data.get("completion_percentage", 0)
        return max(0, min(100, value))

    def clean_hours_played(self):
        value = self.cleaned_data.get("hours_played", 0)
        if value < 0:
            raise forms.ValidationError("Hours played cannot be negative.")
        return value

    def clean_rating(self):
        value = self.cleaned_data.get("rating")
        if value is not None and not (1.0 <= float(value) <= 10.0):
            raise forms.ValidationError("Rating must be between 1.0 and 10.0.")
        return value
