import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-for-local-demo")
DB_PATH = os.path.join(os.path.dirname(__file__), "campus_demo.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123-change-me")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                roll_number TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS login_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username_or_email TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                result TEXT NOT NULL,
                event_time TEXT NOT NULL
            )
        """)


def log_event(identity, roll_number, result):
    with get_db() as db:
        db.execute(
            "INSERT INTO login_events (username_or_email, roll_number, result, event_time) VALUES (?, ?, ?, ?)",
            (identity, roll_number, result, datetime.now().strftime("%d-%m-%Y %I:%M:%S %p"))
        )


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        roll_number = request.form.get("roll_number", "").strip().upper()

        if not username or not email or not roll_number:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("register"))

        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO users (username, email, roll_number, created_at) VALUES (?, ?, ?, ?)",
                    (username, email, roll_number,
                     datetime.now().strftime("%d-%m-%Y %I:%M:%S %p"))
                )
            log_event(email, roll_number, "Demo account created")
            flash("Demo account created. You can now log in.", "success")
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            flash("That username, email, or roll number is already registered.", "error")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    identity = request.form.get("identity", "").strip()
    roll_number = request.form.get("roll_number", "").strip().upper()

    with get_db() as db:
        user = db.execute(
            "SELECT * FROM users WHERE (username = ? OR email = ?) AND roll_number = ?",
            (identity, identity.lower(), roll_number)
        ).fetchone()

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        log_event(identity, roll_number, "Successful demo login")
        flash("Welcome! You are logged in to the demo.", "success")
        return redirect(url_for("welcome"))

    log_event(identity or "(blank)", roll_number or "(blank)", "Failed demo login")
    flash("Those demo details did not match a registered account.", "error")
    return redirect(url_for("home"))


@app.route("/welcome")
def welcome():
    if not session.get("user_id"):
        return redirect(url_for("home"))
    return render_template("welcome.html", username=session.get("username"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have logged out.", "success")
    return redirect(url_for("home"))


@app.route("/forgot")
def forgot():
    return render_template("forgot.html")


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        if request.form.get("admin_password", "") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("dashboard"))
        flash("Incorrect dashboard password.", "error")
    return render_template("admin_login.html")


@app.route("/dashboard")
@admin_required
def dashboard():
    with get_db() as db:
        users = db.execute(
            "SELECT id, username, email, roll_number, created_at FROM users ORDER BY id DESC"
        ).fetchall()
        events = db.execute(
            "SELECT username_or_email, roll_number, result, event_time FROM login_events ORDER BY id DESC LIMIT 100"
        ).fetchall()
    return render_template("dashboard.html", users=users, events=events)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
