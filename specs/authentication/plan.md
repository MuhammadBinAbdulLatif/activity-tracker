# Technical Implementation Plan: Authentication

> **Feature Directory:** `specs/authentication/plan.md`  
> **Status:** Completed & Closed  

---

## 1. Architectural Strategy

We will encapsulate authentication within a dedicated Django application named `accounts` (or `users`). It integrates with Django's built-in `auth` framework while extending the user model or providing a companion `Profile` model to hold the security question and answer.

### Key Architectural Choices:
1. **User Profile Model (`accounts.models.Profile`):**
   - Linked One-to-One with Django's `User` model.
   - Stores `security_question` and hashed/normalized `security_answer`.
2. **Session-based Reset Flow:**
   - After successfully verifying the security answer, write a signed session token or user ID to `request.session['reset_user_id']` with an expiry.
   - The reset view verifies this session state before rendering the password reset form, preventing unauthorized resets.
3. **Forms:**
   - `SignUpForm`: Custom form inheriting from `UserCreationForm` with extra fields for question and answer.
   - `SignInForm`: Inherits from `AuthenticationForm` styled with dark input widgets.
   - `ForgotUsernameForm` & `SecurityAnswerForm`: Multi-step or clean dynamic forms.
   - `ResetPasswordForm`: Custom form validating new password and confirmation.
4. **Views:**
   - Class-Based Views (CBVs) or clean function views for maintainability and form handling.
5. **UI / Styling:**
   - Base authentication template (`templates/accounts/auth_base.html`) implementing the 50/50 split grid, shadcn-like dark theme, and the quote panel on the right.
   - Child templates for `signup.html`, `login.html`, `forgot_password.html`, and `reset_password.html`.

---

## 2. Step-by-Step Execution Plan

### Step 1: Django App Setup
- Create the app: `python manage.py startapp accounts` (if not already present).
- Register `accounts` in `INSTALLED_APPS` within `utrack/settings.py`.

### Step 2: Data Models
- Define `Profile` in `accounts/models.py`:
  - `user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')`
  - `security_question = models.CharField(max_length=255)`
  - `security_answer = models.CharField(max_length=255)` (stored normalized / stripped / lowercased)
- Run `makemigrations` and `migrate`.
- Hook up signals or form-level creation so every user has a Profile.

### Step 3: Forms & Logic
- Create `accounts/forms.py`:
  - Standardized list of predefined security questions (with optional custom question option).
  - Validation rules matching Django standards.
  - Custom widgets applying Tailwind / shadcn dark-themed CSS classes.

### Step 4: Routing & Views
- Wire routes in `accounts/urls.py` and include in `utrack/urls.py`:
  - `/accounts/signup/` $\rightarrow$ `SignUpView`
  - `/accounts/login/` $\rightarrow$ `SignInView`
  - `/accounts/logout/` $\rightarrow$ `SignOutView`
  - `/accounts/forgot-password/` $\rightarrow$ `ForgotPasswordView`
  - `/accounts/reset-password/` $\rightarrow$ `ResetPasswordView`

### Step 5: Templates & Dark Minimalist UI
- Create `templates/accounts/auth_base.html`:
  - Responsive 2-column layout (50% form on left, 50% dark gradient & quote on right).
  - Dark theme tokens (zinc/black shades).
- Create individual views:
  - `signup.html`
  - `login.html`
  - `forgot_password.html`
  - `reset_password.html`

### Step 6: Automated Testing & Validation
- Implement test suite in `accounts/tests.py` fulfilling all requirements in `validation.md`.
- Run tests and verify zero regressions.
