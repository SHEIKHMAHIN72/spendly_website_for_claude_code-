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


def get_summary_stats(user_id):
    db = get_db()
    total = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = ?", (user_id,)
    ).fetchone()["total"]
    count = db.execute(
        "SELECT COUNT(*) AS cnt FROM expenses WHERE user_id = ?", (user_id,)
    ).fetchone()["cnt"]
    top = db.execute(
        "SELECT category, SUM(amount) AS total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    db.close()
    return {
        "total_spent": total,
        "transaction_count": count,
        "top_category": top["category"] if top else "\u2014",
    }


def get_recent_transactions(user_id, limit=10):
    db = get_db()
    rows = db.execute(
        "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC, created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    db.close()
    return [dict(row) for row in rows]


def get_category_breakdown(user_id):
    db = get_db()
    rows = db.execute(
        "SELECT category, SUM(amount) AS total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user_id,),
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
