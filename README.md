# Moodify AI — PhD / Hackathon Competition Build

Moodify is a research-oriented multimodal web application combining:

- facial-expression inference with a trained 7-class CNN
- OpenCV face detection
- visual Beauty Scan proxies
- deterministic mood-to-music adaptation
- JWT authentication
- a research evidence console
- Dockerized FastAPI deployment
- Render cloud deployment without Azure

## Model

The trained model is included at:

```text
backend/models/emotion_cnn.h5
```

Expected input:

```text
(None, 48, 48, 1)
```

Expected output:

```text
7 classes
```

The configured class order is defined in `backend/model.py` and must match the order used during training.

## Local run

Backend:

```powershell
cd D:\Moodify_100_100_Competition_Build\Moodify_100_100_Competition_Build\backend
python -m uvicorn main:app --reload
```

Frontend:

```powershell
cd D:\Moodify_100_100_Competition_Build\Moodify_100_100_Competition_Build\frontend
npm install
npm run dev
```

## Render deployment

1. Push this repository to GitHub.
2. Open Render.
3. Create **New → Blueprint**.
4. Connect the GitHub repository.
5. Use the root `render.yaml`.
6. Set `MOODIFY_FRONTEND_ORIGINS` on the backend.
7. Set `VITE_API_URL` on the frontend.
8. Verify `/health/live`, `/health/ready`, `/docs` and the complete frontend workflow.

See:

```text
cloud/DEPLOYMENT_STEPS.md
cloud/README_RENDER.md
CLOUD_NO_AZURE.md
```

## Research integrity

The Research Dashboard must show measured metrics only. Do not type or invent model accuracy, F1, latency, or confusion-matrix values. A real held-out evaluation creates `backend/model_metrics.json`.

## Cloud truthfulness

The repository is cloud-ready. It should only be described as cloud-deployed after the Render services successfully build and the public endpoints pass verification.
