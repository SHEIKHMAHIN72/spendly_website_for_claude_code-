from database.db import get_db
from datetime import datetime


def get_user_by_id(user_id):
    db = get_db()
    row = db.execute("SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    if row is None:
        return None
    created = datetime.fromisoformat(row["created_at"])
    member_since = created.strftime("%B %Y")
    return {"name": row["name"], "email": row["email"], "member_since": member_since}


def _date_filter_sql(date_from, date_to):
    if date_from and date_to:
        return " AND date BETWEEN ? AND ?", (date_from, date_to)
    return "", ()


def get_summary_stats(user_id, date_from=None, date_to=None):
    db = get_db()
    dsql, dpar = _date_filter_sql(date_from, date_to)

    total = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = ?" + dsql,
        (user_id,) + dpar,
    ).fetchone()["total"]
    count = db.execute(
        "SELECT COUNT(*) AS cnt FROM expenses WHERE user_id = ?" + dsql,
        (user_id,) + dpar,
    ).fetchone()["cnt"]
    top = db.execute(
        "SELECT category, SUM(amount) AS total FROM expenses WHERE user_id = ?" + dsql + " GROUP BY category ORDER BY total DESC LIMIT 1",
        (user_id,) + dpar,
    ).fetchone()
    db.close()
    return {
        "total_spent": total,
        "transaction_count": count,
        "top_category": top["category"] if top else "\u2014",
    }


def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    db = get_db()
    dsql, dpar = _date_filter_sql(date_from, date_to)
    rows = db.execute(
        "SELECT date, description, category, amount FROM expenses WHERE user_id = ?" + dsql + " ORDER BY date DESC, created_at DESC LIMIT ?",
        (user_id,) + dpar + (limit,),
    ).fetchall()
    db.close()
    return [dict(row) for row in rows]


def get_category_breakdown(user_id, date_from=None, date_to=None):
    db = get_db()
    dsql, dpar = _date_filter_sql(date_from, date_to)
    rows = db.execute(
        "SELECT category, SUM(amount) AS total FROM expenses WHERE user_id = ?" + dsql + " GROUP BY category ORDER BY total DESC",
        (user_id,) + dpar,
    ).fetchall()
    db.close()
    if not rows:
        return []
    grand_total = sum(row["total"] for row in rows)
    breakdown = []
    for row in rows:
        pct = round(row["total"] / grand_total * 100)
        breakdown.append({"name": row["category"], "amount": row["total"], "pct": pct})
    pct_sum = sum(b["pct"] for b in breakdown)
    if pct_sum != 100:
        diff = 100 - pct_sum
        breakdown[0]["pct"] += diff
    return breakdown
