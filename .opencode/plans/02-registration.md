# Implementation Plan: Registration (Step 2)

## Files to modify

| File | Changes |
|------|---------|
| `app.py` | Add imports (`request`, `redirect`, `url_for`, `session`, `generate_password_hash`); set `app.secret_key`; rewrite `/register` route for GET+POST |
| `templates/register.html` | Add `value="{{ name }}"` and `value="{{ email }}"` to preserve form inputs on validation error |

No new files, no new dependencies, no CSS changes.

## Step-by-step

### 1. `app.py` — imports
- Add `request`, `redirect`, `url_for`, `session` from flask
- Add `generate_password_hash` from `werkzeug.security`

### 2. `app.py` — secret key
- Add `app.secret_key = "spendly-dev-secret-key"` right after `app = Flask(__name__)`

### 3. `app.py` — rewrite `/register` route
- Change decorator to `@app.route("/register", methods=["GET", "POST"])`
- **GET**: render template as before
- **POST**:
  - Extract `name`, `email`, `password` from `request.form`
  - Validate inputs
  - Check DB for duplicate email
  - Hash password with `generate_password_hash(password)`
  - Insert user via parameterised query
  - Redirect to `url_for("login")` on success
  - On validation failure, re-render with `error` message and submitted values

### 4. `templates/register.html` — preserve values
- Add `value="{{ name }}"` to name input
- Add `value="{{ email }}"` to email input
- Pass `name` and `email` back to template along with `error` on validation failure

## Validation rules

| Field | Rule | Error message |
|-------|------|---------------|
| name | non-empty after strip | "Name is required" |
| email | contains `@` | "Enter a valid email address" |
| password | ≥ 8 characters | "Password must be at least 8 characters" |
| email | not in DB already | "An account with this email already exists" |

## After successful registration

Redirect to `/login` page. The user can then sign in with their new credentials.

## Verification

1. Run `python app.py` — app starts without errors
2. Visit `http://127.0.0.1:5001/register` — form renders
3. Submit empty form — see error messages
4. Submit with existing email (`demo@spendly.com`) — see duplicate email error
5. Submit with valid data — redirected to `/login`
6. Check `expense_tracker.db` — new user row with hashed password
