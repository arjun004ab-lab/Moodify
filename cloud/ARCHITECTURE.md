# Moodify Render Architecture

The SVG at `diagrams/moodify-render-architecture.svg` is the updated architecture diagram for the subscription-free cloud-ready build.

Primary path:

```text
Browser
  ↓ HTTPS
Render Static Site (React/Vite)
  ↓ HTTPS REST API
Render Web Service (Docker)
  ├─ FastAPI
  ├─ TensorFlow/Keras CNN
  ├─ OpenCV
  ├─ Beauty Scan
  ├─ JWT authentication
  └─ SQLite prototype storage
```

For public deployment, the frontend is configured with `VITE_API_URL`, while backend CORS is restricted with `MOODIFY_FRONTEND_ORIGINS`.
