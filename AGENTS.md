# Spendly — expense tracker

## Stack
- Python 3.10+ · Flask 3.1.3 · Jinja2 · SQLite (raw `sqlite3`, no ORM)
- pytest + pytest-flask for testing (no tests written yet)
- No Node.js, no Flask extensions (no Flask-Login, no Flask-WTF, etc.) — auth and forms are manual

## Commands
```bash
venv\Scripts\activate          # activate venv
pip install -r requirements.txt
python app.py                  # dev server on http://127.0.0.1:5001 (debug mode, auto-reload)
pytest -v                      # run all tests
```

## Project structure
```
app.py                      — single Flask entrypoint (routes, app factory not used)
database/
  db.py                     — placeholder; students implement get_db(), init_db(), seed_db()
templates/                  — Jinja2 templates inheriting from base.html
static/css/style.css        — custom CSS (~700 lines, no framework)
static/js/main.js           — vanilla JS (demo modal only)
```

## Key facts
- **App name**: Spendly — tracks expenses in Indian Rupees (₹)
- **Educational scaffold**: placeholder routes (logout, profile, expense CRUD) return plain-text stubs labeled "coming in Step N"
- **DB file**: `expense_tracker.db` is gitignored — generated at runtime by `init_db()`
- **Config**: no `opencode.json`, no existing instruction files
- **No typechecker, no linter, no formatter** configured
