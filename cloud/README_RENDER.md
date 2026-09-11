# Moodify AI — Cloud-Ready Architecture (No Azure)

Moodify uses **Render** as its cloud target and completely removes the Azure dependency.

## Architecture

```text
Browser
   |
   +---- Render Static Site (React + Vite)
   |           |
   |           | HTTPS REST API
   |           v
   +---- Render Web Service (Docker)
               |
               +-- FastAPI / Uvicorn / Gunicorn
               +-- TensorFlow/Keras CNN
               +-- OpenCV face detection
               +-- Beauty Scan
               +-- JWT authentication
               +-- SQLite prototype storage
               +-- emotion_cnn.h5
```

Render officially supports static sites, Python/FastAPI web services, Docker-based deployments, health checks, environment variables, and Git-based auto-deploys. The free tier is suitable for evaluation/demo work, with documented sleep and ephemeral-filesystem limitations.

## Why this is technically defensible

- The AI model is the actual trained `emotion_cnn.h5` file.
- The backend is deployed as the same Dockerized application used locally.
- The frontend calls a public HTTPS backend URL via `VITE_API_URL`.
- CORS is explicitly restricted through `MOODIFY_FRONTEND_ORIGINS`.
- Health endpoints expose live/readiness status.
- Research metrics are displayed only after actual held-out evaluation.
- No Azure resource or Azure CLI is required.

## Source code locations

```text
backend/
  main.py
  model.py
  beauty.py
  recommendations.py
  auth.py
  database.py
  schemas.py
  Dockerfile
  requirements.txt
  models/emotion_cnn.h5

frontend/
  src/
  package.json

render.yaml
```

## Deployment truthfulness

The repository is **cloud-ready**. It becomes **actually cloud-deployed** only after the Render services build successfully and their public URLs pass health and end-to-end checks.
