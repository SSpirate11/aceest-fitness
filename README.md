# ACEest Fitness & Gym – Flask App with Automated CI/CD

[![ACEest CI/CD Pipeline](https://github.com/SSpirate11/aceest-fitness/actions/workflows/main.yml/badge.svg)](https://github.com/SSpirate11/aceest-fitness/actions/workflows/main.yml)

A Flask web app for gym and fitness management. It's built from the ACEest Tkinter
prototypes (`Aceestver-1.0` … `Aceestver-3.2.4`) and ships with Pytest tests, a
multi-stage Docker image, a Jenkins BUILD pipeline and a GitHub Actions CI/CD workflow.

## Features

| Area | Endpoint(s) | Origin version |
|------|-------------|----------------|
| Program catalogue (Fat Loss / Muscle Gain / Beginner) | `GET /`, `GET /api/programs`, `GET /api/programs/<code>` | 1.0 – 1.1.2 |
| Calorie calculator (weight × program factor) | `POST /api/calories` | 1.1 – 2.x |
| BMI and risk category | `POST /api/bmi` | 2.2.4 |
| Clients (SQLite) | `GET/POST /api/clients`, `GET /api/clients/<name>` | 2.0.1 – 3.0.1 |
| Weekly adherence progress | `GET/POST /api/clients/<name>/progress` | 2.0.1+ |
| Workout logging | `GET/POST /api/clients/<name>/workouts` | 2.2.4+ |
| Login (hashed passwords) | `POST /api/login` | 3.1.2+ |
| AI-style program generator | `POST /api/generate-program` | 3.1.2 |
| Membership status | `GET /api/clients/<name>/membership` | 3.2.4 |
| Health check | `GET /health` | – |

## Project Structure

```
.
├── app.py                    # Flask app factory + routes
├── aceest/
│   ├── fitness.py            # Pure business logic (calories, BMI, AI program, membership)
│   ├── db.py                 # SQLite schema & connection handling
│   └── clients.py            # Client management blueprint
├── tests/                    # Pytest suite (unit + API tests)
├── requirements.txt          # Runtime deps
├── requirements-dev.txt      # Test/lint deps
├── Dockerfile                # Multi-stage: base -> test -> runtime
├── Jenkinsfile               # Jenkins BUILD & quality gate
└── .github/workflows/main.yml  # GitHub Actions pipeline
```

## Local Setup & Execution

```bash
git clone https://github.com/SSpirate11/aceest-fitness.git
cd aceest-fitness
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
python app.py                       # http://localhost:5000
```

### Run with Docker

```bash
docker build -t aceest-fitness .                     # builds the runtime stage
docker run -d --name aceest -p 5000:5000 aceest-fitness
curl http://localhost:5000/health
```

### Example API calls

```bash
curl -X POST localhost:5000/api/calories -H 'Content-Type: application/json' -d '{"weight":70,"program":"FL"}'
curl -X POST localhost:5000/api/clients  -H 'Content-Type: application/json' \
     -d '{"name":"Arjun","age":28,"height":175,"weight":70,"program":"FL","membership_end":"2027-12-31"}'
curl localhost:5000/api/clients/Arjun
```

Default login is `admin` / `admin`. You can change it with the `ACEEST_ADMIN_PASSWORD` environment variable.

## Running Tests Manually

```bash
pytest                                   # all tests (verbose)
pytest --cov=aceest --cov=app            # with coverage
flake8 .                                 # lint
# or, exactly like CI, inside a container:
docker build --target test -t aceest-fitness:test .
docker run --rm aceest-fitness:test
```

## CI/CD Integration Overview

```
 git push / PR ──► GitHub Actions ──► Build & Lint ──► Docker Image Assembly ──► Containerised Pytest + Smoke test
        │
        └──────► Jenkins (Poll SCM) ──► Clean Checkout ──► Build Test Image ──► Lint ──► Unit Tests (JUnit)
                                         ──► Build Runtime Image ──► Smoke Test
```

### GitHub Actions (`.github/workflows/main.yml`)
Runs on every `push` (any branch) and every `pull_request` to `main`:
1. **Build & Lint** – installs dependencies, runs `compileall` to catch syntax errors, then runs `flake8`.
2. **Docker Image Assembly** – builds the `test` and `runtime` stages and passes both images to the next job as an artifact.
3. **Automated Testing** – runs the Pytest suite **inside the test container**, then starts the runtime container and checks that `/health` responds. The JUnit report is uploaded as an artifact.

### Jenkins (`Jenkinsfile`)
Jenkins is the secondary BUILD and quality gate. A Pipeline job ("Pipeline script from SCM")
pulls the latest `main` from GitHub every 5 minutes (Poll SCM), wipes the workspace for a
clean build, builds the Docker images, runs lint and tests in containers, publishes JUnit
results and smoke-tests the runtime image. Temporary containers and images are removed afterwards.

### Docker image design
* `python:3.12-slim` base, `--no-cache` pip installs, and a `.dockerignore` keep the image small.
* Multi-stage build: test tools (pytest, flake8) only exist in the `test` stage, never in production.
* The runtime stage runs as a **non-root user** (`appuser`), serves with gunicorn and has a `HEALTHCHECK`.

## Git Workflow

* `main` – stable, always green.
* `feature/*` – new functionality (`feature/flask-core`, `feature/client-management`, `feature/pytest-suite`).
* `infra/*` – infrastructure (`infra/docker`, `infra/github-actions`, `infra/jenkins`).
* `fix/*` – bug fixes.
* Commits follow Conventional Commits (`feat:`, `fix:`, `test:`, `ci:`, `docs:`, `chore:`).
* Releases are tagged (`v1.0.0`, `v2.0.0`, `v3.0.0`).

