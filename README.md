# F1 Statistics API

A RESTful API for Formula 1 race data built with Python FastAPI and SQLite. 

The database is pre-seeded with Formula One data from 1950 to 2024, originally from the Ergast Motor Racing Dataset (https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020?resource=download). 

You can query drivers, teams, races, and results, as well as statistics such as championship standings, leaderboards, and career summaries.

---

## Setup

Requires Python 3.11 onwards

```bash
git clone https://github.com/kyrikonis/F1_API.git
cd F1_API
python -m venv venv
source venv/bin/activate  # for windows do venv\Scripts\activate
pip install -r requirements.txt
export API_KEY=f1-api-key  # for windows do set API_KEY=f1-api-key
uvicorn main:app --reload
```

API available at `http://127.0.0.1:8000`, can access swagger UI at `/docs`.

---

## Deployment

The API is deployed at: https://kyrik2005.pythonanywhere.com

Swagger UI: https://kyrik2005.pythonanywhere.com/docs

---

## Running Tests

```bash
API_KEY=f1-api-key python -m pytest tests/ -v
```

On Windows:
```bash
set API_KEY=f1-api-key && python -m pytest tests/ -v
```

Tests do not affect the seeded data as they use an in memory SQLite database.

---

## Authentication

Write operations (POST, PATCH, DELETE) require an API key passed as a request header:
```
X-API-Key: f1-api-key
```

The key value is set via the `API_KEY` environment variable. Read operations do not require a key.

---

## API Endpoints

Full documentation is available at `/docs` when the server is running or within [api_documentation.pdf](api_documentation.pdf).

Includes example requests and responses for correct authentication, rejected requests with an invalid key, and numerous endpoints.

| Tag | Method | Endpoint | Description |
|-----|--------|------|-------------|
| Drivers | GET | `/drivers/` | List drivers (filter by `active_only`, `nationality`, `team_id`, `name` )|
| Drivers | GET | `/drivers/{ref}` | Get a driver by ID, 3 letter code (e.g. `HAM`), or name |
| Drivers | POST | `/drivers/` | Create a driver |
| Drivers | PATCH | `/drivers/{id}` | Update a driver |
| Drivers | DELETE | `/drivers/{id}` | Delete a driver |
| Teams | GET | `/teams/` | List teams (filter by `active_only`, `name`) |
| Teams | GET | `/teams/{ref}` | Get a team by ID or name (e.g. `Ferrari`,`Red_bull`) |
| Teams | POST | `/teams/` | Create a team |
| Teams | PATCH | `/teams/{id}` | Update a team |
| Teams | DELETE | `/teams/{id}` | Delete a team |
| Races | GET | `/races/` | List races (filter by `year`, `country`, `circuit`) |
| Races | GET | `/races/{ref}` | Get a race by ID or name (e.g. `Monaco`) |
| Races | POST | `/races/` | Create a race |
| Races | PATCH | `/races/{id}` | Update a race |
| Races | DELETE | `/races/{id}` | Delete a race |
| Results | GET | `/results/` | List results (filter by `race_id`, `driver_id`, `team_id`) |
| Results | GET | `/results/{id}` | Get a result by ID |
| Results | POST | `/results/` | Create a result |
| Results | PATCH | `/results/{id}` | Update a result |
| Results | DELETE | `/results/{id}` | Delete a result |
| Analysis | GET | `/analysis/standings/drivers/{year}` | Drivers' Championship standings for a season |
| Analysis | GET | `/analysis/standings/constructors/{year}` | Constructors' Championship standings for a season |
| Analysis | GET | `/analysis/leaderboard/wins` | All-time race wins leaderboard |
| Analysis | GET | `/analysis/drivers/{ref}/career` | Career summary for a driver (accepts ID, 3 letter code, or name) |

---

## Re-seeding the Database

The database file is included. If you need to rebuild it from the Ergast Dataset CSV files, place them in a `data/` folder and run:

```bash
python seed.py
```
