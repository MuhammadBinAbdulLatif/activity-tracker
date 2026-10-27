# Validation Plan: Authentication System

> **Feature Directory:** `specs/authentication/validation.md`  
> **Status:** Completed & Closed (14/14 Tests Passed)  

---

## 1. Overview & Verification Strategy

To guarantee the reliability, security, and completeness of the authentication module, all test cases below must pass with **zero failures and zero errors**.

Testing is conducted via Django's automated test framework:
```bash
python manage.py test accounts
```

**Status:** PASSING (14/14 tests passing, 0 errors, 0 failures).

---

## 2. Test Cases & Verification Checklist

### 2.1 Sign-Up Tests (`accounts.tests.SignUpTests`)
- [x] **Valid Registration:** Submitting a valid username, matching passwords, and security question/answer creates a `User` and linked `Profile`.
- [x] **Duplicate Username:** Submitting an existing username rejects with a proper validation error.
- [x] **Password Mismatch:** Submitting mismatched password confirmation fails with form error.
- [x] **Missing Security Fields:** Registration without security question or answer fails validation.
- [x] **Normalization:** Verifies that security answers are stored normalized (whitespace stripped, case-insensitive).

### 2.2 Sign-In Tests (`accounts.tests.SignInTests`)
- [x] **Valid Credentials:** Existing user with correct password logs in and redirects to destination/home.
- [x] **Invalid Password:** Correct username with wrong password rejects with generic auth error.
- [x] **Non-Existent User:** Rejects properly with clean error message.
- [x] **Session Verification:** Confirms `request.user.is_authenticated` is True post-login.

### 2.3 Forgot Password & Security Question Tests (`accounts.tests.ForgotPasswordTests`)
- [x] **Username Lookup:** Submitting valid username returns the user's specific security question.
- [x] **Non-Existent Username:** Returns an appropriate error if user not found.
- [x] **Correct Answer Submission:** Providing the correct answer (even with case/whitespace variations) authorizes reset state in session.
- [x] **Incorrect Answer Submission:** Fails and prevents moving to reset stage.

### 2.4 Password Reset Tests (`accounts.tests.ResetPasswordTests`)
- [x] **Authorized Reset:** User with validated session can set a new password and save it successfully.
- [x] **Unauthorized Direct Access:** Attempting to access `/accounts/reset-password/` directly without having verified the security question redirects back to forgot-password or login.
- [x] **Post-Reset Login:** User can immediately log in with their newly set password, and the old password no longer works.

### 2.5 UI & Template Rendering Tests (`accounts.tests.TemplateRenderTests`)
- [x] All 4 routes return HTTP 200 with appropriate template names.
- [x] The split layout renders the designated quote: *"Watching a movie to lighten up your day is such a good thing."*
- [x] Dark theme utility classes and form input containers render properly.

---

## 3. Exit Criteria ("All Clear" Gate)

The authentication phase is complete:
1. `python manage.py test accounts` passes 100% of the test cases above (14 passed).
2. The 2-column dark gradient split layout adheres to `specs/styles.md`.
