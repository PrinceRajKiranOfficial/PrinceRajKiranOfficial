# Travel Planner (Flask + HTML/CSS)

A full-stack starter project inspired by your wireframes:
- Frontend: HTML + CSS (Jinja templates)
- Backend: Flask
- Local database option: SQLite (default)

## Features
- User registration form
- Create and save trips
- Trip listing on the home page
- Trip details page
- Local SQLite database via SQLAlchemy

## Project structure
```
.
├── app.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── new_trip.html
│   └── trip_detail.html
└── static/css/style.css
```

## Run locally
1. Create virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Start app
   ```bash
   python app.py
   ```
4. Open `http://127.0.0.1:5000`

## Optional: initialize DB manually
```bash
flask --app app init-db
```

## Notes for GitHub upload
- Repo is already organized with templates/static separation.
- `.gitignore` excludes local DB and virtualenv files.
- You can add GitHub Actions later for tests/deploy.
