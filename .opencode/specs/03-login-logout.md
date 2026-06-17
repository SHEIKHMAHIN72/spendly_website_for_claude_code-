# Spec: Login and Logout

## Overview

Allow registered users to sign in with their email and password, and sign out when done. The registration form (Step 2) already redirects here on success, so a working login flow closes the loop. The navbar updates to show the logged-in user's name and a logout button, hiding the public "Sign in" and "Get started" links.

## Depends on

- Step 1 — Database Setup (users table must exist)
- Step 2 — Registration (users must be able to create accounts; login validates against those accounts)

## Routes

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| GET | `/login` | Show login form | Public |
| POST | `/login` | Authenticate user, create session | Public |
| GET | `/logout` | Clear session, redirect to landing | Logged-in |

## Database changes

No new tables or columns.

## Templates

- **Modify** `templates/login.html` — add `value="{{ email }}"` to preserve email on error; add flash message display for success notification after registration
- **Modify** `templates/base.html` — conditionally show user name + logout link when `session.user_id` is set, otherwise show "Sign in" / "Get started"

No new templates.

## Files to change

- `app.py` — implement login POST route (validate credentials with `check_password_hash`, set `session['user_id']`); implement logout route (clear session); import `check_password_hash` from werkzeug

## Files to create

None.

## New dependencies

No new dependencies.

## Rules for implementation

- No ORMs (no SQLAlchemy)
- Use parameterised queries only
- Passwords must be verified with `werkzeug.security.check_password_hash`
- Use Flask's `session` dict to store `user_id` (no Flask-Login)
- On login failure re-render the form with an `error` variable
- On login success redirect to the landing page (`url_for('landing')`)
- On logout call `session.clear()` then redirect to landing page
- The navbar in `base.html` must check `session.user_id` to toggle between logged-in and logged-out state
- After registration (Step 2) the user is redirected to `/login` — display a flash message "Account created successfully! Sign in below."
- All templates extend `base.html`
- Use CSS variables — never hardcode hex values

## Definition of done

- [ ] `GET /login` renders the sign-in form
- [ ] `POST /login` with correct credentials creates a session and redirects to landing
- [ ] `POST /login` with wrong email/password shows an inline error
- [ ] `POST /login` with wrong password for existing email shows an error
- [ ] After successful registration, `/login` displays a success flash message
- [ ] `/logout` clears the session and redirects to landing
- [ ] Navbar shows user name + logout when logged in, "Sign in" / "Get started" when logged out
- [ ] App starts without errors
- [ ] All queries use parameterised SQL
