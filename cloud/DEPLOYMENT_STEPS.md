# Moodify AI — Render Free Deployment

This project removes Azure completely. The deployment target is Render's free tier: a Render Static Site for React/Vite and a Render Web Service built from the FastAPI Dockerfile.

Render currently documents free web services and static sites, with a 750-hour monthly free-instance allowance. Free web services spin down after 15 minutes of inactivity and have ephemeral local files. Render also states that no payment card is required for the free tier. Use this deployment for demos/testing, not as a production SLA.

## 1. Push Moodify to GitHub

From the project root:

```powershell
git init
git add .
git commit -m "Moodify Render cloud deployment"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## 2. Create the Render Blueprint

Open Render and choose **New → Blueprint**. Connect the GitHub repository containing `render.yaml`.

The Blueprint defines:

- `moodify-api`: Docker web service using `backend/Dockerfile`
- `moodify-frontend`: static React/Vite site
- `/health/live` as the backend health probe
- generated backend JWT secret
- frontend CORS and API URL supplied as environment variables

## 3. Backend environment variables

Set on `moodify-api`:

```text
MOODIFY_FRONTEND_ORIGINS=https://<your-frontend>.onrender.com
MOODIFY_EMOTION_LABELS=angry,disgust,fear,happy,surprise,sad,neutral
```

IMPORTANT: the label order must match the CNN training order. The supplied project uses the model order already established in `backend/model.py`.

The Blueprint generates `MOODIFY_SECRET_KEY` automatically. Do not commit a secret into Git.

## 4. Frontend environment variable

Set on `moodify-frontend`:

```text
VITE_API_URL=https://<your-backend>.onrender.com
```

Vite embeds `VITE_*` variables during the static build, so changing `VITE_API_URL` requires a new frontend build/deploy.

## 5. Verify the backend

Open:

```text
https://<your-backend>.onrender.com/health/live
https://<your-backend>.onrender.com/health/ready
https://<your-backend>.onrender.com/docs
```

Expected `/health/live`:

```json
{
  "status": "alive",
  "version": "5.0.0"
}
```

Expected `/health/ready` should report both `cnn_loaded: true` and `database: true`.

## 6. Verify the frontend

Open the static-site URL and test:

```text
Landing → Register → Login → Dashboard → Emotion Scan → Analyze → Music → Beauty Scan → Research
```

## 7. Verify the cloud boundary

Open browser developer tools → Network.

During login/scan requests, the request URL must start with:

```text
https://<your-backend>.onrender.com/
```

It must NOT be:

```text
http://127.0.0.1:8000/
http://localhost:8000/
```

## 8. Important Render free-tier limitation

The backend includes TensorFlow + OpenCV and loads a trained CNN at startup. The Render free web service has 512 MB RAM. The first deployment may therefore fail due to memory pressure depending on the TensorFlow wheel/model runtime. If that happens, the correct research-grade response is to document the constraint and either run the live demo locally or use a larger hosted compute tier/provider; do not fabricate a successful deployment.

SQLite is used by default for the prototype. Render documents that the free service filesystem is ephemeral, so local SQLite data can disappear after redeploy/restart/spin-down. For durable production data, use a managed database.
