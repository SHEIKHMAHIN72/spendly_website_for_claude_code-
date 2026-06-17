# Plan: Database Setup

## 1. `database/db.py`

### `get_db()`
- Connect to `expense_tracker.db` in project root
- Set `conn.row_factory = sqlite3.Row`
- Execute `PRAGMA foreign_keys = ON`
- Return connection

### `init_db()`
- Call `get_db()`
- Create `users` table with: id (PK AUTOINCREMENT), name (NOT NULL), email (UNIQUE NOT NULL), password_hash (NOT NULL), created_at (DEFAULT datetime('now'))
- Create `expenses` table with: id (PK AUTOINCREMENT), user_id (FK→users.id, NOT NULL), amount (REAL NOT NULL), category (TEXT NOT NULL), date (TEXT NOT NULL), description (TEXT), created_at (DEFAULT datetime('now'))
- Use `CREATE TABLE IF NOT EXISTS`
- Commit and close

### `seed_db()`
- Check if users table has data → if yes, return early
- Hash "demo123" with `werkzeug.security.generate_password_hash`
- Insert demo user (Demo User, demo@spendly.com)
- Insert 8 sample expenses across all 7 categories, spread across current month, amounts ₹50–₹2000
- Commit and close

## 2. `app.py`

- Import `get_db`, `init_db`, `seed_db` from `database.db`
- Call `init_db()` and `seed_db()` inside `with app.app_context():` before `if __name__`

## 3. Files Changed

- `database/db.py` — full implementation
- `app.py` — imports + startup calls

## 4. File Created

- `.opencode/plans/` directory
- `.opencode/plans/01-database-setup.md` (this file)
