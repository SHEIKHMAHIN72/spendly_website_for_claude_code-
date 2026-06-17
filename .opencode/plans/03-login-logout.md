# Implementation Plan: Login and Logout (Step 3)

## Files to modify

| File | Changes |
|------|---------|
| `app.py` | Add `flash` import; add `check_password_hash` import; add `flash()` call in `/register` before redirect; rewrite `/login` for GET+POST; rewrite `/logout` |
| `templates/login.html` | Add `value="{{ email }}"` on email input; add flash message display block |
| `templates/base.html` | Conditional nav — check `session.user_id` to show user name + logout or "Sign in"/"Get started" |

No new files, no new dependencies, no CSS changes.

## Step-by-step

### 1. `app.py` — imports
- Add `flash` to flask import line
- Add `check_password_hash` alongside `generate_password_hash` import

### 2. `app.py` — update `/register`
- Before `return redirect(url_for("login"))`, add `flash("Account created successfully! Sign in below.")`

### 3. `app.py` — rewrite `/login`
- Change decorator to `@app.route("/login", methods=["GET", "POST"])`
- **GET**: render `login.html`
- **POST**:
  - Extract `email`, `password` from form
  - Validate: if email or password empty → render with `error = "Invalid email or password"`
  - Query DB for user by email
  - If not found or password doesn't match → render with `error = "Invalid email or password"`
  - If correct → set `session["user_id"]` and `session["user_name"]`, redirect to `url_for("landing")`

### 4. `app.py` — rewrite `/logout`
- Call `session.clear()`
- Redirect to `url_for("landing")`

### 5. `templates/login.html`
- Add `value="{{ email }}"` to email input
- Add flash message display block using `get_flashed_messages()`

### 6. `templates/base.html` — nav
- Replace static links with conditional checking `session.user_id`

## Validation & edge cases

| Scenario | Behavior |
|----------|----------|
| Empty email or password | Re-render with `error = "Invalid email or password"` |
| Wrong email | Same generic error (no info leak) |
| Correct email, wrong password | Same generic error |
| Correct credentials | Session set, redirect to landing |
| `/logout` with no session | `session.clear()` is safe on empty, redirects to landing |

## Verification

1. `python app.py` — no errors
2. Visit `/login` — form renders
3. Submit wrong email — inline error "Invalid email or password"
4. Submit demo@spendly.com with wrong password — same error
5. Submit demo@spendly.com / demo123 — session created, redirected to landing, navbar shows user name + logout
6. Register new user — redirected to `/login` with green flash message
7. Click logout — session cleared, navbar back to "Sign in"/"Get started"
