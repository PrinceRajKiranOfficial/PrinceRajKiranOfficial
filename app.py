from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-me"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///travelplanner.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    city = db.Column(db.String(120))
    country = db.Column(db.String(120))


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    start_place = db.Column(db.String(120), nullable=False)
    end_place = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)


@app.route("/")
def index():
    trips = Trip.query.order_by(Trip.start_date.desc()).all()
    return render_template("index.html", trips=trips)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please use another email.", "error")
            return redirect(url_for("register"))

        user = User(
            first_name=request.form["first_name"].strip(),
            last_name=request.form["last_name"].strip(),
            email=email,
            city=request.form.get("city", "").strip(),
            country=request.form.get("country", "").strip(),
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/trip/new", methods=["GET", "POST"])
def new_trip():
    if request.method == "POST":
        start_date = date.fromisoformat(request.form["start_date"])
        end_date = date.fromisoformat(request.form["end_date"])

        if end_date < start_date:
            flash("End date cannot be before start date.", "error")
            return redirect(url_for("new_trip"))

        trip = Trip(
            title=request.form["title"].strip(),
            start_place=request.form["start_place"].strip(),
            end_place=request.form["end_place"].strip(),
            start_date=start_date,
            end_date=end_date,
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(trip)
        db.session.commit()
        flash("Trip created successfully.", "success")
        return redirect(url_for("index"))

    return render_template("new_trip.html")


@app.route("/trip/<int:trip_id>")
def trip_detail(trip_id: int):
    trip = Trip.query.get_or_404(trip_id)
    return render_template("trip_detail.html", trip=trip)


@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    print("Database initialized.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
