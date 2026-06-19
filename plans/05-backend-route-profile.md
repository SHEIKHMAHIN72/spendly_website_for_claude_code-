# Integration Plan: Step 5 — Backend Route Profile

## Overview
Replace all hardcoded data in `/profile` route with live SQLite queries. Wire four sections (user info, summary stats, transaction list, category breakdown) to real data.

## Steps

### 1. Update seed data in `database/db.py`
Current seed data totals ₹4,675 (top: Shopping). Spec expects ₹346.24 (top: Bills, 8 txns, 7 categories).

Replace `seed_expenses` with:

| user_id | amount  | category      | description       |
|---------|---------|---------------|-------------------|
| 1       | 45.50   | Food          | Weekly groceries  |
| 1       | 35.00   | Transport     | Metro recharge    |
| 1       | 120.00  | Bills         | Electricity bill  |
| 1       | 25.00   | Health        | Pharmacy          |
| 1       | 30.00   | Entertainment | Movie tickets     |
| 1       | 55.00   | Shopping      | New headphones    |
| 1       | 15.74   | Food          | Morning coffee    |
| 1       | 20.00   | Other         | Gift wrapping     |

### 2. Create `database/queries.py` — 4 pure query helpers

| Function | SQL approach | Edge case |
|---|---|---|
| `get_user_by_id(user_id)` | SELECT, parse `created_at` → "Month YYYY" | Return `None` if not found |
| `get_summary_stats(user_id)` | 3 queries: SUM, COUNT, top category by SUM | No expenses → `{"total_spent":0,"transaction_count":0,"top_category":"—"}` |
| `get_recent_transactions(user_id, limit=10)` | SELECT ordered by `date` DESC, LIMIT | No expenses → `[]` |
| `get_category_breakdown(user_id)` | GROUP BY category, compute SUM | Round pct to int, adjust largest to absorb remainder |

### 3. Modify `app.py` — `profile()` route
Replace hardcoded dicts with calls to query helpers. Compute `user.initials` from name.

### 4. Modify `templates/profile.html` — align variable names
- `cat.total` → `cat.amount`
- `cat.percentage` → `cat.pct`

### 5. Create `tests/` test suite
- `tests/__init__.py` (empty)
- `tests/conftest.py` — Flask test app with in-memory DB, fixtures
- `tests/test_backend_connection.py` — 10 tests (8 unit + 2 route)

## Files changed

| Action | File |
|---|---|
| Modify | `database/db.py` |
| Create | `database/queries.py` |
| Modify | `app.py` |
| Modify | `templates/profile.html` |
| Create | `tests/__init__.py` |
| Create | `tests/conftest.py` |
| Create | `tests/test_backend_connection.py` |
