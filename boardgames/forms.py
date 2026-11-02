from django import forms
from .models import BoardGameEntry, BoardGameStatus


class BoardGameEntryForm(forms.ModelForm):
    class Meta:
        model = BoardGameEntry
        fields = [
            "title",
            "year_published",
            "status",
            "play_count",
            "last_played",
            "avg_session_minutes",
            "favorite_players",
            "rating",
            "review",
            "notes",
            "min_players",
            "max_players",
            "min_playtime",
            "max_playtime",
            "designers",
            "publishers",
            "categories",
            "mechanics",
            "custom_cover",
            "cover_url",
            "external_id",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "placeholder": "Game Title (e.g. Catan, Dune: Imperium)",
            }),
            "year_published": forms.NumberInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "placeholder": "Year (e.g. 1995)",
            }),
            "status": forms.Select(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-zinc-600 transition-colors",
            }),
            "play_count": forms.NumberInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "min": "0",
            }),
            "last_played": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
            }),
            "avg_session_minutes": forms.NumberInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "placeholder": "e.g. 75",
                "min": "0",
            }),
            "favorite_players": forms.TextInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "placeholder": "e.g. Alex, Maya, Sam",
            }),
            "rating": forms.NumberInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "placeholder": "1.0 - 10.0",
                "step": "0.1",
                "min": "1.0",
                "max": "10.0",
            }),
            "review": forms.Textarea(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors resize-none",
                "rows": 3,
                "placeholder": "Your personal verdict or retrospective review...",
            }),
            "notes": forms.Textarea(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors resize-none",
                "rows": 2,
                "placeholder": "Expansions owned, house rules, sleeves used, storage notes...",
            }),
            "min_players": forms.NumberInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "placeholder": "Min (e.g. 1)",
            }),
            "max_players": forms.NumberInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "placeholder": "Max (e.g. 5)",
            }),
            "min_playtime": forms.NumberInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "placeholder": "Min (e.g. 60)",
            }),
            "max_playtime": forms.NumberInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
                "placeholder": "Max (e.g. 120)",
            }),
            "designers": forms.TextInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
            }),
            "publishers": forms.TextInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
            }),
            "categories": forms.TextInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
            }),
            "mechanics": forms.TextInput(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors",
            }),
            "custom_cover": forms.ClearableFileInput(attrs={
                "class": "block w-full text-xs text-zinc-400 file:mr-4 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-zinc-800 file:text-zinc-200 hover:file:bg-zinc-700 cursor-pointer",
            }),
            "cover_url": forms.HiddenInput(),
            "external_id": forms.HiddenInput(),
            "description": forms.Textarea(attrs={
                "class": "w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 transition-colors resize-none",
                "rows": 3,
            }),
        }
