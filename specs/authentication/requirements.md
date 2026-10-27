# Requirements: Baseline Authentication System

> **Feature Directory:** `specs/authentication/requirements.md`  
> **Status:** Completed & Closed  

---

## 1. Overview & Objectives

Deliver a fast, friction-free, session-based authentication flow for **uTrack** utilizing Django's built-in authentication foundations. 

Email verification is explicitly out of scope for this baseline. Users authenticate with a **username** and **password**. Account recovery relies on a **security question & answer** defined during registration.

---

## 2. Target Routes

1. **Sign-Up (`/accounts/signup/`):**
   - User creates an account with username, password, password confirmation, security question selection, and security answer.
2. **Sign-In (`/accounts/login/`):**
   - User authenticates with username and password. Supports "Remember Me" session handling. Redirects to homepage upon success.
3. **Forgot Password (`/accounts/forgot-password/`):**
   - User enters username to fetch their registered security question.
   - User submits the answer to the security question.
   - On match, authorizes transition to the password reset view.
4. **Reset Password (`/accounts/reset-password/`):**
   - Securely sets a new password for the validated user session.
   - Redirects to Sign-In with a success confirmation.

*(Note: Sign-Out `/accounts/logout/` is included as standard auth plumbing).*

---

## 3. Detailed Functional Requirements

### 3.1 Sign-Up Flow
- **Fields:**
  - `username` (unique, alphanumeric + underscores, min 3 chars).
  - `password` (standard Django password validation rules).
  - `password_confirm` (must match `password`).
  - `security_question` (dropdown of predefined questions or customizable prompt).
  - `security_answer` (case-insensitive trimmed storage or hashed comparison).
- **Behavior:**
  - Auto-login upon successful registration or direct redirect to sign-in with a success toast/banner.

### 3.2 Sign-In Flow
- **Fields:** `username`, `password`.
- **Validation:** Clear error message if credentials do not match (*"Invalid username or password"*).
- **Post-Login:** Directs to the application dashboard/home page.

### 3.3 Forgot Password & Security Question Recovery
- **Step 1:** User enters `username`.
  - If user does not exist: Provide clear, friendly feedback.
  - If user exists: Present their assigned `security_question`.
- **Step 2:** User inputs `security_answer`.
  - Normalizes whitespace and case (e.g. `answer.strip().lower()`).
  - If correct: Grants access to the reset password stage (stored securely in a short-lived signed session token).
  - If incorrect: Returns clear error message (*"Incorrect answer to security question"*).

### 3.4 Reset Password Flow
- User inputs new `password` and `password_confirm`.
- Password validation applied.
- Password is updated (`user.set_password()`), session token cleared, and user is redirected to Sign-In.

---

## 4. Visual & UI Requirements (Conforming to `specs/styles.md`)

- **Two-Column Split Layout:**
  - Desktop: 50/50 split grid.
  - Left: Vertically centered dark form panel (`bg-black` / `bg-zinc-950`).
  - Right: Dark aesthetic gradient (`from-zinc-900 via-zinc-950 to-black`) featuring the quote:
    > *"Watching a movie to lighten up your day is such a good thing."*
  - Mobile: Single column with clean dark card aesthetic.
- **Styling Details:**
  - High-tech, dark, minimalist shadcn-style controls (dark inputs, hairline zinc borders, crisp white primary CTA button).

---

## 5. Definition of Done (Acceptance Criteria)

- [x] All four primary routes are accessible and operational (`/accounts/signup/`, `/accounts/login/`, `/accounts/forgot-password/`, `/accounts/reset-password/`).
- [x] Sign-up captures username, password, security question, and answer.
- [x] Sign-in authenticates valid users and rejects invalid credentials.
- [x] Forgot password correctly displays the registered security question and verifies the answer.
- [x] Password reset updates the password and permits subsequent sign-in with the new password.
- [x] Forms provide accessible client & server validation with inline errors.
- [x] Dynamic submission spinners and disabled state feedback on buttons prevent double-submits.
- [x] Floating Sonner-style toasts deliver unobtrusive success, error, and info feedback without distorting layout.
- [x] Split-screen modern dark UI matches the canonical standards in `specs/styles.md`.
- [x] Automated test suite in `specs/authentication/validation.md` passes with 100% success (14/14 tests).
