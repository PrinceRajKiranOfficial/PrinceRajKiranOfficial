import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "travelplanner.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-me"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            city TEXT,
            country TEXT,
            bio TEXT
        );

        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_place TEXT NOT NULL,
            end_place TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            notes TEXT,
            budget REAL DEFAULT 0,
            status TEXT DEFAULT 'Upcoming'
        );

        CREATE TABLE IF NOT EXISTS itinerary_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            day_number INTEGER NOT NULL,
            section_title TEXT NOT NULL,
            activity TEXT NOT NULL,
            travel_time TEXT,
            allocated_budget REAL DEFAULT 0,
            FOREIGN KEY(trip_id) REFERENCES trips(id) ON DELETE CASCADE
        );
        """
    )
    db.commit()


@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Database initialized.")


@app.route("/")
def index():
    db = get_db()
    trips = db.execute("SELECT * FROM trips ORDER BY start_date DESC").fetchall()
    featured = trips[:3]
    return render_template("index.html", trips=trips, featured=featured)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = get_db()
        email = request.form["email"].strip().lower()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("Email already registered. Please use another email.", "error")
            return redirect(url_for("register"))

        db.execute(
            """
            INSERT INTO users (first_name, last_name, email, phone, city, country, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["first_name"].strip(),
                request.form["last_name"].strip(),
                email,
                request.form.get("phone", "").strip(),
                request.form.get("city", "").strip(),
                request.form.get("country", "").strip(),
                request.form.get("bio", "").strip(),
            ),
        )
        db.commit()
        flash("Registration successful.", "success")
        return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/trip/new", methods=["GET", "POST"])
def new_trip():
    if request.method == "POST":
        start_date = date.fromisoformat(request.form["start_date"])
        end_date = date.fromisoformat(request.form["end_date"])
        if end_date < start_date:
            flash("End date cannot be before start date.", "error")
            return redirect(url_for("new_trip"))

        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO trips (title, start_place, end_place, start_date, end_date, notes, budget, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["title"].strip(),
                request.form["start_place"].strip(),
                request.form["end_place"].strip(),
                start_date.isoformat(),
                end_date.isoformat(),
                request.form.get("notes", "").strip(),
                float(request.form.get("budget", 0) or 0),
                request.form.get("status", "Upcoming"),
            ),
        )
        trip_id = cursor.lastrowid
        db.commit()
        flash("Trip created successfully. Add itinerary sections now.", "success")
        return redirect(url_for("build_itinerary", trip_id=trip_id))

    return render_template("new_trip.html")


@app.route("/trip/<int:trip_id>/itinerary", methods=["GET", "POST"])
def build_itinerary(trip_id):
    db = get_db()
    trip = db.execute("SELECT * FROM trips WHERE id = ?", (trip_id,)).fetchone()
    if not trip:
        return redirect(url_for("index"))

    if request.method == "POST":
        db.execute(
            """
            INSERT INTO itinerary_items (trip_id, day_number, section_title, activity, travel_time, allocated_budget)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                trip_id,
                int(request.form.get("day_number", 1)),
                request.form["section_title"].strip(),
                request.form["activity"].strip(),
                request.form.get("travel_time", "").strip(),
                float(request.form.get("allocated_budget", 0) or 0),
            ),
        )
        db.commit()
        flash("Itinerary section added.", "success")
        return redirect(url_for("build_itinerary", trip_id=trip_id))

    items = db.execute(
        "SELECT * FROM itinerary_items WHERE trip_id = ? ORDER BY day_number, id", (trip_id,)
    ).fetchall()
    return render_template("build_itinerary.html", trip=trip, items=items)


@app.route("/trip/<int:trip_id>")
def trip_detail(trip_id):
    db = get_db()
    trip = db.execute("SELECT * FROM trips WHERE id = ?", (trip_id,)).fetchone()
    items = db.execute(
        "SELECT * FROM itinerary_items WHERE trip_id = ? ORDER BY day_number, id", (trip_id,)
    ).fetchall()
    return render_template("trip_detail.html", trip=trip, items=items)


@app.route("/trips")
def trip_listing():
    db = get_db()
    trips = db.execute("SELECT * FROM trips ORDER BY start_date DESC").fetchall()
    return render_template("trip_listing.html", trips=trips)


@app.route("/profile")
def profile():
    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1").fetchall()
    trips = db.execute("SELECT * FROM trips ORDER BY start_date DESC").fetchall()
    return render_template("profile.html", users=users, trips=trips)


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
