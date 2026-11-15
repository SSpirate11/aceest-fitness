# ACEest Fitness & Gym – Full CI/CD Pipeline, SonarQube & Kubernetes Orchestration

[![ACEest CI/CD Pipeline](https://github.com/SSpirate11/aceest-fitness/actions/workflows/main.yml/badge.svg)](https://github.com/SSpirate11/aceest-fitness/actions/workflows/main.yml)

A cloud-native Flask microservice for gym and fitness management refactored from the ACEest Tkinter prototypes (`Aceestver-1.0` … `Aceestver-3.2.4`). It features a 35-test Pytest suite (99% coverage), SonarQube static analysis & Quality Gate, a multi-stage non-root Docker architecture pushed to Docker Hub (`9597654915/aceest-fitness`), dual CI/CD pipelines (GitHub Actions & Jenkins), and Kubernetes (Minikube) manifests implementing **5 progressive deployment strategies with automated rollback**.

## Features & API Endpoints

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
├── app.py                        # Flask app factory + REST routes
├── aceest/
│   ├── __init__.py               # Version metadata (APP_VERSION)
│   ├── fitness.py                # Pure business logic (calories, BMI, AI program, membership)
│   ├── db.py                     # SQLite schema & thread-safe connection handling
│   └── clients.py                # Client management REST blueprint
├── k8s/                          # Kubernetes (Minikube) Deployment Strategies
│   ├── 01-rolling-update.yaml    # Strategy 1: Rolling Update + Rollback (NodePort 30081)
│   ├── 02-blue-green.yaml        # Strategy 2: Blue-Green Deployment (NodePort 30082)
│   ├── 03-canary.yaml            # Strategy 3: Canary Release 80/20 Split (NodePort 30083)
│   ├── 04-shadow.yaml            # Strategy 4: Shadow Traffic Mirroring (NodePort 30084)
│   └── 05-ab-testing.yaml        # Strategy 5: A/B Testing Header Routing (NodePort 30085)
├── legacy/                       # Original Tkinter prototypes (1.0 -> 3.2.4)
├── tests/                        # Pytest suite (35 unit + API integration tests)
├── sonar-project.properties      # SonarQube project & coverage configuration
├── Dockerfile                    # Multi-stage: base -> test -> runtime (non-root appuser)
├── Jenkinsfile                   # End-to-End Jenkins CI/CD Pipeline
└── .github/workflows/main.yml    # GitHub Actions CI workflow
```

## Docker Hub Multi-Version Repository

Repository: `https://hub.docker.com/r/9597654915/aceest-fitness`

```bash
docker build --target runtime --build-arg APP_VERSION=1.0.0 -t 9597654915/aceest-fitness:v1.0.0 .
docker build --target runtime --build-arg APP_VERSION=2.0.0 -t 9597654915/aceest-fitness:v2.0.0 .
docker build --target runtime --build-arg APP_VERSION=3.0.0 -t 9597654915/aceest-fitness:v3.0.0 -t 9597654915/aceest-fitness:latest .
```

## SonarQube Code Quality Analysis

```bash
sonar-scanner \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=$SONAR_TOKEN
```

## Kubernetes Deployment Strategies & Rollback

```bash
kubectl apply -f k8s/01-rolling-update.yaml
kubectl apply -f k8s/02-blue-green.yaml
kubectl apply -f k8s/03-canary.yaml
kubectl apply -f k8s/04-shadow.yaml
kubectl apply -f k8s/05-ab-testing.yaml

# Instant Rollback on failure
kubectl rollout undo deployment/aceest-rolling -n aceest-gym
```
