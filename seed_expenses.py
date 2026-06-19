import sys
import random
from datetime import date, timedelta, datetime
import calendar

from database.db import get_db


CATEGORIES = {
    "Food": {"weight": 5, "range": (50, 800), "desc": ["Weekly groceries", "Lunch with team", "Dinner at restaurant", "Coffee & snacks", "Birthday cake", "Street food", "Breakfast ordering", "Zomato order"]},
    "Transport": {"weight": 3, "range": (20, 500), "desc": ["Metro recharge", "Bus pass", "Cab to office", "Auto rickshaw", "Petrol", "Parking fee", "Uber ride", "Train ticket"]},
    "Bills": {"weight": 3, "range": (200, 3000), "desc": ["Electricity bill", "Water bill", "Internet recharge", "Mobile recharge", "Gas cylinder", "Wifi bill", "DTH recharge"]},
    "Health": {"weight": 1, "range": (100, 2000), "desc": ["Pharmacy", "Doctor consultation", "Health checkup", "Gym membership", "Medicine", "Dental checkup", "Eye checkup"]},
    "Entertainment": {"weight": 1, "range": (100, 1500), "desc": ["Movie tickets", "Concert tickets", "Netflix subscription", "Spotify premium", "Book purchase", "AMC app"]},
    "Shopping": {"weight": 3, "range": (200, 5000), "desc": ["New headphones", "Clothing", "Kitchen supplies", "Home decor", "Electronics", "Stationery", "Shoes", "Furniture"]},
    "Other": {"weight": 2, "range": (50, 1000), "desc": ["Gift wrapping", "Donation", "ATM charges", "Laundry", "Miscellaneous", "Tailoring", "Pooja items"]},
}


def parse_args():
    if len(sys.argv) != 4:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        sys.exit(1)
    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        sys.exit(1)
    if count < 1 or months < 1:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        sys.exit(1)
    return user_id, count, months


def check_user_exists(user_id):
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    if user is None:
        print(f"No user found with id {user_id}.")
        sys.exit(1)


def weighted_category():
    items = []
    for cat, info in CATEGORIES.items():
        items.extend([cat] * info["weight"])
    return random.choice(items)


def random_date(months_back):
    today = date.today()
    start = today - timedelta(days=months_back * 30)
    delta = (today - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


def generate_expenses(user_id, count, months):
    expenses = []
    for _ in range(count):
        cat = weighted_category()
        info = CATEGORIES[cat]
        amt = round(random.uniform(*info["range"]), 2)
        desc = random.choice(info["desc"])
        d = random_date(months)
        expenses.append((user_id, amt, cat, d, desc))
    return expenses


def insert_expenses(expenses):
    db = get_db()
    try:
        db.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
        db.commit()
    except Exception:
        db.rollback()
        db.close()
        raise
    db.close()
    return len(expenses)


def main():
    user_id, count, months = parse_args()
    check_user_exists(user_id)
    expenses = generate_expenses(user_id, count, months)
    inserted = insert_expenses(expenses)
    dates = [e[3] for e in expenses]
    print(f"Inserted {inserted} expenses for user {user_id}.")
    print(f"Date range: {min(dates)} to {max(dates)}")
    print("Sample:")
    for row in expenses[:5]:
        print(f"  Rs.{row[1]:>7.2f}  {row[3]}  {row[2]:15s}  {row[4]}")


if __name__ == "__main__":
    main()
