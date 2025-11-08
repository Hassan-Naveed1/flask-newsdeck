Public News Aggregator — flask-newsdeck

A minimal, free-tier-friendly news aggregator built with Flask, SQLite, and APScheduler.
It fetches top headlines (tech / business / sports) from NewsAPI on a schedule, caches them in SQLite, exposes a clean REST API, and lets you save favorites.

Free-friendly note: Uses NewsAPI's free tier (dev key) with simple caching + pagination.

✨ Features

Fetches top headlines for tech, business, and sports

SQLite persistence for articles and favorites

APScheduler background job to refresh every 15 minutes

Pagination & topic filters (/api/articles?topic=tech&page=1&limit=20)

Favorites endpoints to save and view picks

Lightweight UI: simple HTML list with filters (or use the REST API directly)

🧰 Tech Stack

Flask (API + minimal UI)

SQLite (storage)

APScheduler (15-min refresh job)

Requests (calling NewsAPI)

python-dotenv (env configuration)

📦 Project Structure
flask-newsdeck/
├─ app.py
├─ models.py
├─ news.py               # external API + mappers
├─ scheduler.py          # APScheduler init
├─ db/
│  └─ schema.sql
├─ static/
│  └─ styles.css
├─ templates/
│  └─ index.html
├─ .env.example
└─ README.md

⚙️ Setup
1️⃣ Clone and enter
git clone https://github.com/yourname/flask-newsdeck.git
cd flask-newsdeck

2️⃣ Create & activate virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure environment

Create .env from example and fill your key.

cp .env.example .env
# then edit .env and set:
# NEWSAPI_KEY=your_dev_key
# REFRESH_MINUTES=15
# FLASK_ENV=development

5️⃣ Initialize database
python -c "from app import init_db; init_db()"

6️⃣ Run the application
flask --app app run


Visit → http://127.0.0.1:5000/

🔌 How it works (data-flow)
[APScheduler job] → calls → [NewsAPI]
                       ↓
                  [Mapper/clean] → [SQLite: articles]
                       ↓
   [/api/articles] ← Flask ← [SQLite]
   [/api/favorites] ↕ POST/GET/DELETE


A background job fetches headlines for each topic every REFRESH_MINUTES.

Raw responses are normalized (deduplicated by URL + title hash) and written into articles table.

REST endpoints read from SQLite (never hot-hit NewsAPI), providing pagination and filters.

Favorites are stored in a separate table keyed by article_id.

🧪 Try quickly (cURL)
# list tech headlines
curl "http://127.0.0.1:5000/api/articles?topic=tech&limit=5"

# mark favorite
curl -X POST -H "Content-Type: application/json" -d "{\"article_id\": 123}" http://127.0.0.1:5000/api/favorites

# list favorites
curl http://127.0.0.1:5000/api/favorites

🗃️ Schema (minimal)
articles(
  id INTEGER PRIMARY KEY,
  topic TEXT,                 -- tech|business|sports
  title TEXT,
  source TEXT,
  url TEXT UNIQUE,
  image_url TEXT,
  published_at TEXT,          -- ISO8601
  fetched_at TEXT             -- ISO8601
)

favorites(
  id INTEGER PRIMARY KEY,
  article_id INTEGER UNIQUE,  -- FK to articles.id
  saved_at TEXT               -- ISO8601
)

🖼️ Screenshots

Data-flow diagram: see diagram.png

Runtime logs (fetch job + API calls): see logs.png

Frontend preview: see test_frontend.png (optional proof-of-run image for reviewers)

🚧 Limits / Notes

NewsAPI free tier may restrict some country sources or commercial use.

Responses are cached locally to minimize quota usage.

For production, consider rotating keys, structured logging, and retries/backoff.

🏷️ License

MIT License

📁 What Each File Does (Purpose & Responsibilities)
app.py

Flask application factory and route definitions.

Initializes logging, database (init_db()), and background scheduler (start_scheduler()).

Endpoints:

GET / → serves minimal UI (templates/index.html)

GET /api/articles → paginated, optional topic filter

GET /api/favorites → list saved favorites

POST /api/favorites → save favorite by article_id

DELETE /api/favorites/<article_id> → remove favorite

models.py

SQLite persistence layer.

init_db() runs schema initialization.

upsert_articles(items) inserts new articles, skipping duplicates by url.

list_articles(topic, page, limit) returns paginated results and total count.

add_favorite(article_id), list_favorites(), delete_favorite(article_id) manage favorites.

news.py

External REST calls to NewsAPI.

fetch_topic(topic, api_key, page=1, page_size=50) maps internal topics (tech | business | sports) to NewsAPI categories, calls /v2/top-headlines, and normalizes results (title, url, source, image_url, published_at, fetched_at, topic).

scheduler.py

Background job manager using APScheduler.

Refreshes cached articles every REFRESH_MINUTES.

Reads NEWSAPI_KEY and REFRESH_MINUTES from .env.

For each topic, calls news.fetch_topic() and writes to SQLite via models.upsert_articles().

Logs insert counts and new row totals.

db/schema.sql

Defines two core tables:

articles → fetched NewsAPI articles (unique on url)

favorites → saved favorites (unique on article_id)

templates/index.html

Minimal, dependency-free frontend (vanilla JS).

Topic selection, pagination, and “Save” (favorites) via REST calls.

static/styles.css

Simple dark theme with clean spacing.

Styled header, article cards, and endpoint badges.

No CSS frameworks.

requirements.txt

Pinned dependencies: Flask, APScheduler, Requests, python-dotenv.

.env.example

Template for environment variables. Copy to .env and set:

NEWSAPI_KEY=your_api_key_here
REFRESH_MINUTES=15
FLASK_ENV=development

docs/

diagram.png → architecture/data-flow diagram.

logs.png → example runtime logs.

(Optional) test_frontend.png → screenshot of the running frontend.

🧩 Project Setup Verification

Project is set up

Full Flask app (flask-newsdeck) with clear modular structure (app.py, models.py, news.py, scheduler.py, db/, templates/, static/, docs/).

README, data-flow diagram, and example logs included.

Environment is ready

Virtual environment (.venv) created and activated.

Dependencies installed — external Python packages such as Flask, APScheduler, requests, and python-dotenv.

Configuration is in place

.env.example exists; .env copied with real values.

Key variables set: NEWSAPI_KEY, REFRESH_MINUTES=15, FLASK_ENV=development.

Database layer works

SQLite database (db/news.db) initialized and populated.

Verified with: select count(*) from articles → (126,).

Background refresh works

APScheduler fetches topics (tech | business | sports), normalizes results, and writes to SQLite.

Logs confirm successful fetch and insert cycles.

API + minimal UI work

/api/articles?topic=tech&limit=3 returns live data.

Frontend lists articles, supports pagination, and allows “Save” actions.

Favorites feature is wired

POST /api/favorites saves an article by article_id.

GET /api/favorites lists saved favorites.

DELETE /api/favorites/<article_id> removes favorites.

Dev helper is added

run.sh (cross-platform) bootstraps environment and launches Flask quickly.

API and script tested successfully.

Screenshots for reviewers

test_frontend.png shows UI for quick proof-of-run (recommended under docs/ and linked here)