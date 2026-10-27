from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Profile, SECURITY_QUESTION_CHOICES

INPUT_CLASS = (
    "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 "
    "text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none "
    "focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition-colors"
)

SELECT_CLASS = (
    "w-full px-3.5 py-2.5 rounded-lg bg-zinc-900 border border-zinc-800 "
    "text-zinc-100 text-sm focus:outline-none focus:border-zinc-500 "
    "focus:ring-1 focus:ring-zinc-500 transition-colors"
)


class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS, "placeholder": "Create a secure password"}),
    )
    password_confirm = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS, "placeholder": "Confirm your password"}),
    )
    security_question = forms.ChoiceField(
        choices=SECURITY_QUESTION_CHOICES,
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
        help_text="Used to recover your account if you forget your password.",
    )
    security_answer = forms.CharField(
        label="Security Answer",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Your recovery answer"}),
        help_text="Answers are case-insensitive.",
    )

    class Meta:
        model = User
        fields = ["username"]
        widgets = {
            "username": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Choose a username"}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            profile = Profile(
                user=user,
                security_question=self.cleaned_data["security_question"]
            )
            profile.set_security_answer(self.cleaned_data["security_answer"])
            profile.save()
        return user


class SignInForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Enter your username"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS, "placeholder": "Enter your password"}),
    )


class ForgotPasswordLookupForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Enter your username"}),
    )


class SecurityAnswerForm(forms.Form):
    security_answer = forms.CharField(
        label="Your Security Answer",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Enter your answer"}),
    )


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS, "placeholder": "Enter new password"}),
    )
    new_password_confirm = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS, "placeholder": "Confirm new password"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("new_password_confirm")
        if p1 and p2 and p1 != p2:
            self.add_error("new_password_confirm", "Passwords do not match.")
        return cleaned_data
