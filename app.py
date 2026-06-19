from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = "spendly-dev-secret-key"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        error = None
        if not name:
            error = "Name is required"
        elif "@" not in email:
            error = "Enter a valid email address"
        elif len(password) < 8:
            error = "Password must be at least 8 characters"

        if not error:
            db = get_db()
            existing = db.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing:
                error = "An account with this email already exists"
            db.close()

        if error:
            return render_template("register.html", error=error, name=name, email=email)

        password_hash = generate_password_hash(password)
        db = get_db()
        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        db.commit()
        db.close()
        flash("Account created successfully! Sign in below.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template("login.html", error="Invalid email or password", email=email)

        db = get_db()
        user = db.execute(
            "SELECT id, name, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
        db.close()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password", email=email)

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "member_since": "January 15, 2025",
        "initials": "DU",
    }
    stats = {
        "total_spent": 12450,
        "transaction_count": 42,
        "top_category": "Food",
    }
    transactions = [
        {"date": "15 Apr 2025", "description": "Weekly groceries",   "category": "Food",         "amount": 450},
        {"date": "12 Apr 2025", "description": "Metro recharge",     "category": "Transport",    "amount": 150},
        {"date": "10 Apr 2025", "description": "Electricity bill",   "category": "Bills",        "amount": 1200},
        {"date": "08 Apr 2025", "description": "Pharmacy",           "category": "Health",       "amount": 300},
        {"date": "05 Apr 2025", "description": "Movie tickets",      "category": "Entertainment","amount": 500},
        {"date": "02 Apr 2025", "description": "New headphones",     "category": "Shopping",     "amount": 1800},
    ]
    categories = [
        {"name": "Food",         "total": 3200, "percentage": 32},
        {"name": "Bills",        "total": 2800, "percentage": 28},
        {"name": "Transport",    "total": 1800, "percentage": 18},
        {"name": "Health",       "total": 1200, "percentage": 12},
        {"name": "Entertainment","total": 800,   "percentage": 8},
        {"name": "Shopping",     "total": 500,   "percentage": 5},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
