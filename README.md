# Travel Planner Full Stack App

Flask + HTML/CSS application based on your multi-screen travel planner wireframe.

## What is included
- Login/registration style onboarding screen (`/register`)
- Main dashboard style page (`/`)
- Create trip flow (`/trip/new`)
- Build itinerary sections (`/trip/<id>/itinerary`)
- Trip detail and listing pages (`/trip/<id>`, `/trips`)
- Profile page (`/profile`)
- Local database with **SQLite (stdlib `sqlite3`)** — no ORM dependency required

## Tech stack
- Backend: Flask
- Frontend: HTML templates + CSS
- Local DB: SQLite (`travelplanner.db` auto-created)

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then open: `http://127.0.0.1:5000`

## Initialize DB manually
```bash
flask --app app init-db
```

## GitHub-ready structure
- `app.py` backend entrypoint
- `templates/` all pages
- `static/css/style.css` shared styling
- `.gitignore` excludes virtualenv and sqlite DB artifacts
