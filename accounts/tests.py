from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "omnireader"
        self.password = "Secur3P@ssw0rd!"
        self.security_question = "What was the name of your first pet?"
        self.security_answer = "Fluffy"

        # Pre-create a user for sign-in and password recovery tests
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )
        self.profile = Profile.objects.create(
            user=self.user,
            security_question=self.security_question
        )
        self.profile.set_security_answer(self.security_answer)
        self.profile.save()

    # --- Sign Up Tests ---
    def test_signup_page_renders_cleanly(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")
        self.assertContains(response, "Universal Activity & Media Tracker")
        self.assertContains(response, "Create Account")

    def test_signup_successful(self):
        payload = {
            "username": "newtracker",
            "password": "ValidPassword123!",
            "password_confirm": "ValidPassword123!",
            "security_question": "In what city were you born?",
            "security_answer": "  Seattle  ",  # with spaces to test normalization
        }
        response = self.client.post(reverse("signup"), payload)
        self.assertRedirects(response, reverse("home"))

        # Verify user and profile in DB
        user = User.objects.get(username="newtracker")
        self.assertTrue(user.check_password("ValidPassword123!"))
        self.assertEqual(user.profile.security_question, "In what city were you born?")
        self.assertEqual(user.profile.security_answer, "seattle")  # trimmed & lowercase

    def test_signup_duplicate_username_fails(self):
        payload = {
            "username": self.username,
            "password": "ValidPassword123!",
            "password_confirm": "ValidPassword123!",
            "security_question": "In what city were you born?",
            "security_answer": "Paris",
        }
        response = self.client.post(reverse("signup"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "username", "A user with that username already exists.")

    def test_signup_mismatched_password_fails(self):
        payload = {
            "username": "differentuser",
            "password": "Password123!",
            "password_confirm": "PasswordMismatch999!",
            "security_question": "In what city were you born?",
            "security_answer": "Tokyo",
        }
        response = self.client.post(reverse("signup"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "password_confirm", "Passwords do not match.")

    # --- Sign In Tests ---
    def test_signin_page_renders_cleanly(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, "Universal Activity & Media Tracker")

    def test_signin_successful(self):
        response = self.client.post(reverse("login"), {
            "username": self.username,
            "password": self.password,
        })
        self.assertRedirects(response, reverse("home"))
        # Verify authenticated session
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_signin_invalid_credentials_fails(self):
        response = self.client.post(reverse("login"), {
            "username": self.username,
            "password": "WrongPassword!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    # --- Sign Out Test ---
    def test_signout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    # --- Forgot Password & Security Question Tests ---
    def test_forgot_password_lookup_valid_username(self):
        response = self.client.post(reverse("forgot_password"), {
            "action": "lookup",
            "username": self.username,
        })
        self.assertRedirects(response, reverse("forgot_password"))

        # Follow redirect and verify question is displayed
        follow_response = self.client.get(reverse("forgot_password"))
        self.assertContains(follow_response, self.security_question)
        self.assertContains(follow_response, f"@{self.username}")

    def test_forgot_password_lookup_invalid_username(self):
        response = self.client.post(reverse("forgot_password"), {
            "action": "lookup",
            "username": "nonexistent_person_12345",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account with this username does not exist.")

    def test_forgot_password_verify_answer_case_insensitive(self):
        # Step 1: Look up user
        session = self.client.session
        session["forgot_user_id"] = self.user.pk
        session.save()

        # Step 2: Submit answer with mixed case and whitespace
        response = self.client.post(reverse("forgot_password"), {
            "action": "verify_answer",
            "security_answer": "   fLuFFy  ",
        })
        self.assertRedirects(response, reverse("reset_password"))
        self.assertEqual(self.client.session.get("reset_authorized_user_id"), self.user.pk)

    def test_forgot_password_wrong_answer_fails(self):
        session = self.client.session
        session["forgot_user_id"] = self.user.pk
        session.save()

        response = self.client.post(reverse("forgot_password"), {
            "action": "verify_answer",
            "security_answer": "WrongPetName",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect answer to security question.")

    # --- Reset Password Tests ---
    def test_reset_password_unauthorized_direct_access_redirects(self):
        # Direct GET without verifying security question
        response = self.client.get(reverse("reset_password"))
        self.assertRedirects(response, reverse("forgot_password"))

    def test_reset_password_successful(self):
        # Setup authorized reset session
        session = self.client.session
        session["reset_authorized_user_id"] = self.user.pk
        session.save()

        new_pass = "BrandNewP@ssword99"
        response = self.client.post(reverse("reset_password"), {
            "new_password": new_pass,
            "new_password_confirm": new_pass,
        })
        self.assertRedirects(response, reverse("login"))

        # Verify old password fails and new password works
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.password))
        self.assertTrue(self.user.check_password(new_pass))

        # Can log in with new password
        login_success = self.client.login(username=self.username, password=new_pass)
        self.assertTrue(login_success)
