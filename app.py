from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db
from database.queries import get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown
from datetime import date, datetime, timedelta

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

    user_id = session["user_id"]
    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for("login"))

    initials = "".join(part[0].upper() for part in user["name"].split() if part)
    user["initials"] = initials

    date_from_s = request.args.get("date_from", "").strip()
    date_to_s = request.args.get("date_to", "").strip()

    date_from = None
    date_to = None

    if date_from_s:
        try:
            date_from = datetime.strptime(date_from_s, "%Y-%m-%d").date()
        except ValueError:
            date_from = None

    if date_to_s:
        try:
            date_to = datetime.strptime(date_to_s, "%Y-%m-%d").date()
        except ValueError:
            date_to = None

    if date_from and date_to and date_from > date_to:
        flash("Start date must be before end date.")
        date_from = None
        date_to = None

    today = date.today()
    presets = {
        "this_month": {"date_from": today.replace(day=1).isoformat(), "date_to": today.isoformat()},
        "last_3_months": {"date_from": (today - timedelta(days=90)).isoformat(), "date_to": today.isoformat()},
        "last_6_months": {"date_from": (today - timedelta(days=180)).isoformat(), "date_to": today.isoformat()},
    }

    active_preset = None
    if date_from and date_to:
        date_from_str = date_from.isoformat()
        date_to_str = date_to.isoformat()
        for key, val in presets.items():
            if val["date_from"] == date_from_str and val["date_to"] == date_to_str:
                active_preset = key
                break

    stats = get_summary_stats(user_id, date_from, date_to)
    transactions = get_recent_transactions(user_id, 10, date_from, date_to)
    categories = get_category_breakdown(user_id, date_from, date_to)

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
        date_from=date_from.isoformat() if date_from else "",
        date_to=date_to.isoformat() if date_to else "",
        active_preset=active_preset,
        presets=presets,
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
