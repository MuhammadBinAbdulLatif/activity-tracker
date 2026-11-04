from django import forms
from django.utils import timezone
from .models import Exercise, ExerciseLog, UserExerciseTrack, ExerciseTrackingStatus


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = [
            "name",
            "category",
            "target_muscle_group",
            "secondary_muscles",
            "equipment",
            "instructions",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-colors",
                "placeholder": "e.g., Incline Hammer Strength Chest Press",
            }),
            "category": forms.Select(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 text-sm focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-colors",
            }),
            "target_muscle_group": forms.Select(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 text-sm focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-colors",
            }),
            "secondary_muscles": forms.TextInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-colors",
                "placeholder": "e.g., Triceps, Front Deltoids",
            }),
            "equipment": forms.Select(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 text-sm focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-colors",
            }),
            "instructions": forms.Textarea(attrs={
                "rows": 3,
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-colors",
                "placeholder": "Cues, setup alignment, and range-of-motion guidance...",
            }),
        }


class UserExerciseTrackForm(forms.ModelForm):
    class Meta:
        model = UserExerciseTrack
        fields = [
            "status",
            "personal_goal",
            "frequency_per_week",
            "personal_notes",
        ]
        widgets = {
            "status": forms.Select(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 text-sm focus:outline-none focus:border-teal-500",
            }),
            "personal_goal": forms.TextInput(attrs={
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500",
                "placeholder": "e.g., Reach 100kg Bench Press or 20 Consecutive Pull-Ups",
            }),
            "frequency_per_week": forms.NumberInput(attrs={
                "min": 1,
                "max": 7,
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500",
                "placeholder": "e.g., 2 times/week",
            }),
            "personal_notes": forms.Textarea(attrs={
                "rows": 2,
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500",
                "placeholder": "Progression cues, warm-up habits, or tempo...",
            }),
        }


class ExerciseLogForm(forms.ModelForm):
    class Meta:
        model = ExerciseLog
        fields = [
            "logged_date",
            "sets",
            "reps",
            "weight_kg",
            "duration_minutes",
            "distance_km",
            "calories_burned",
            "rpe",
            "notes",
        ]
        widgets = {
            "logged_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 text-sm focus:outline-none focus:border-teal-500 transition-colors",
            }),
            "sets": forms.NumberInput(attrs={
                "min": 1,
                "placeholder": "e.g., 4",
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 transition-colors",
            }),
            "reps": forms.NumberInput(attrs={
                "min": 1,
                "placeholder": "e.g., 10",
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 transition-colors",
            }),
            "weight_kg": forms.NumberInput(attrs={
                "step": "0.5",
                "min": 0,
                "placeholder": "e.g., 80.0",
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 transition-colors",
            }),
            "duration_minutes": forms.NumberInput(attrs={
                "min": 1,
                "placeholder": "e.g., 30",
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 transition-colors",
            }),
            "distance_km": forms.NumberInput(attrs={
                "step": "0.1",
                "min": 0,
                "placeholder": "e.g., 5.0",
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 transition-colors",
            }),
            "calories_burned": forms.NumberInput(attrs={
                "min": 0,
                "placeholder": "e.g., 320",
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 transition-colors",
            }),
            "rpe": forms.NumberInput(attrs={
                "min": 1,
                "max": 10,
                "placeholder": "1-10",
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 transition-colors",
            }),
            "notes": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Form feedback, tempo, warm-up sets, or feeling...",
                "class": "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-teal-500 transition-colors",
            }),
        }

    def __init__(self, *args, exercise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get("logged_date"):
            self.initial["logged_date"] = timezone.localdate()

        # Tailor form fields dynamically based on the exercise profile!
        if exercise:
            if exercise.is_cardio_type and not exercise.is_resistance_type:
                # Pure cardio: hide resistance lifting fields
                for field_name in ["sets", "reps", "weight_kg"]:
                    if field_name in self.fields:
                        self.fields[field_name].widget = forms.HiddenInput()
            elif exercise.is_resistance_type and not exercise.is_cardio_type:
                # Pure strength/resistance/weights: hide cardio fields
                for field_name in ["duration_minutes", "distance_km", "calories_burned"]:
                    if field_name in self.fields:
                        self.fields[field_name].widget = forms.HiddenInput()
