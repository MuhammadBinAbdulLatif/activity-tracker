from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from .forms import (
    SignUpForm,
    SignInForm,
    ForgotPasswordLookupForm,
    SecurityAnswerForm,
    ResetPasswordForm,
)
from .models import Profile
from .quotes import get_random_quote


class SignUpView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = SignUpForm()
        return render(request, "accounts/signup.html", {"form": form, "quote_data": get_random_quote()})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to uTrack, {user.username}!")
            return redirect("home")
        return render(request, "accounts/signup.html", {"form": form, "quote_data": get_random_quote()})


class SignInView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = SignInForm()
        return render(request, "accounts/login.html", {"form": form, "quote_data": get_random_quote()})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next") or "home"
            return redirect(next_url)
        return render(request, "accounts/login.html", {"form": form, "quote_data": get_random_quote()})


class SignOutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("login")

    def get(self, request):
        logout(request)
        return redirect("login")


class ForgotPasswordView(View):
    def get(self, request):
        # Check if already in the middle of verifying a user
        lookup_user_id = request.session.get("forgot_user_id")
        if lookup_user_id:
            try:
                user = User.objects.get(pk=lookup_user_id)
                profile = user.profile
                form = SecurityAnswerForm()
                return render(
                    request,
                    "accounts/forgot_password_answer.html",
                    {"user_obj": user, "profile": profile, "form": form, "quote_data": get_random_quote()},
                )
            except (User.DoesNotExist, Profile.DoesNotExist):
                request.session.pop("forgot_user_id", None)

        form = ForgotPasswordLookupForm()
        return render(request, "accounts/forgot_password_lookup.html", {"form": form, "quote_data": get_random_quote()})

    def post(self, request):
        action = request.POST.get("action")

        if action == "lookup":
            form = ForgotPasswordLookupForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"].strip()
                try:
                    user = User.objects.get(username__iexact=username)
                    if hasattr(user, "profile") and user.profile.security_question:
                        request.session["forgot_user_id"] = user.pk
                        return redirect("forgot_password")
                    else:
                        form.add_error("username", "No security question is configured for this account.")
                except User.DoesNotExist:
                    form.add_error("username", "Account with this username does not exist.")
            return render(request, "accounts/forgot_password_lookup.html", {"form": form, "quote_data": get_random_quote()})

        elif action == "verify_answer":
            user_id = request.session.get("forgot_user_id")
            if not user_id:
                return redirect("forgot_password")
            try:
                user = User.objects.get(pk=user_id)
                profile = user.profile
            except (User.DoesNotExist, Profile.DoesNotExist):
                request.session.pop("forgot_user_id", None)
                return redirect("forgot_password")

            form = SecurityAnswerForm(request.POST)
            if form.is_valid():
                candidate_answer = form.cleaned_data["security_answer"]
                if profile.check_security_answer(candidate_answer):
                    # Answer verified! Authorize reset
                    request.session.pop("forgot_user_id", None)
                    request.session["reset_authorized_user_id"] = user.pk
                    return redirect("reset_password")
                else:
                    form.add_error("security_answer", "Incorrect answer to security question.")

            return render(
                request,
                "accounts/forgot_password_answer.html",
                {"user_obj": user, "profile": profile, "form": form, "quote_data": get_random_quote()},
            )

        elif action == "cancel":
            request.session.pop("forgot_user_id", None)
            return redirect("forgot_password")

        return redirect("forgot_password")


class ResetPasswordView(View):
    def get(self, request):
        user_id = request.session.get("reset_authorized_user_id")
        if not user_id:
            messages.error(request, "Please verify your account before resetting your password.")
            return redirect("forgot_password")

        form = ResetPasswordForm()
        return render(request, "accounts/reset_password.html", {"form": form, "quote_data": get_random_quote()})

    def post(self, request):
        user_id = request.session.get("reset_authorized_user_id")
        if not user_id:
            messages.error(request, "Session expired or unauthorized. Please verify your account again.")
            return redirect("forgot_password")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            request.session.pop("reset_authorized_user_id", None)
            return redirect("forgot_password")

        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            user.set_password(new_password)
            user.save()
            request.session.pop("reset_authorized_user_id", None)
            messages.success(request, "Your password has been successfully reset. You may now sign in.")
            return redirect("login")

        return render(request, "accounts/reset_password.html", {"form": form, "quote_data": get_random_quote()})
