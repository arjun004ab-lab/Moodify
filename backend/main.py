import logging
import os
import time
import uuid
from typing import Optional

import pandas as pd
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from beauty import scan_beauty
from database import Base, User, engine, get_db
from model import model, model_metadata, predict_emotion
from recommendations import get_recommendation
from schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

LOGGER = logging.getLogger("moodify.api")

Base.metadata.create_all(bind=engine)

APP_VERSION = "5.0.0"
MAX_IMAGE_BYTES = 8 * 1024 * 1024

frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "MOODIFY_FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="Moodify AI",
    version=APP_VERSION,
    description=(
        "Research-oriented multimodal platform for "
        "emotion inference, visual beauty signals "
        "and adaptive music."
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def request_logging(request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    try:
        response = await call_next(request)
        return response

    finally:
        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        LOGGER.info(
            "%s %s -> %.1fms request_id=%s",
            request.method,
            request.url.path,
            elapsed_ms,
            request_id
        )


@app.get("/")
def root():
    return {
        "project": "Moodify AI",
        "version": APP_VERSION,
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health/live")
def live():
    return {
        "status": "alive",
        "version": APP_VERSION,
    }


@app.get("/health/ready")
def ready():
    database_ok = False

    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )
        database_ok = True
    except Exception as exc:
        LOGGER.error(
            "Database readiness failure: %s",
            exc
        )

    cnn_ok = model is not None

    status_code = 200 if (
        database_ok and cnn_ok
    ) else 503

    result = {
        "status": (
            "ready"
            if status_code == 200
            else "not_ready"
        ),
        "cnn_loaded": cnn_ok,
        "database": database_ok,
        "version": APP_VERSION,
    }

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status_code,
        content=result
    )


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "cnn_loaded": model is not None,
        "version": APP_VERSION,
    }


@app.get("/analytics/model")
def analytics_model():
    metrics_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "model_metrics.json"
    )

    payload = {
        "evaluated": False,
        "metrics": None,
        "model": model_metadata(),
    }

    if os.path.exists(metrics_path):
        try:
            import json

            with open(
                metrics_path,
                "r",
                encoding="utf-8"
            ) as handle:
                payload["metrics"] = json.load(handle)

            payload["evaluated"] = True

        except Exception as exc:
            LOGGER.warning(
                "Could not load model metrics: %s",
                exc
            )

    return payload


def current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header.",
        )

    user_id = decode_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    return user


def validate_upload(file: UploadFile):
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=(
                "Unsupported image type. "
                "Use JPG, PNG or WebP."
            ),
        )


async def read_upload(file: UploadFile):
    data = await file.read(
        MAX_IMAGE_BYTES + 1
    )

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds the 8 MB limit.",
        )

    return data


@app.post(
    "/auth/register",
    response_model=TokenResponse
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    email = data.email.lower().strip()

    existing = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                "An account with this email already exists."
            ),
        )

    try:
        password_hash = hash_password(
            data.password
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    user = User(
        name=data.name.strip(),
        email=email,
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        user.id
    )

    return {
        "success": True,
        "message": "Account created successfully.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


@app.post(
    "/auth/login",
    response_model=TokenResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    email = data.email.lower().strip()

    user = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if (
        user is None
        or not verify_password(
            data.password,
            user.password_hash
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    token = create_access_token(
        user.id
    )

    return {
        "success": True,
        "message": "Login successful.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


@app.get(
    "/auth/me",
    response_model=UserOut
)
def me(
    user: User = Depends(current_user),
):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
):
    validate_upload(file)
    data = await read_upload(file)

    try:
        result = predict_emotion(data)

        recommendation = get_recommendation(
            result["emotion"]
        )

        return {
            "success": True,
            **result,
            "music": recommendation["music"],
        }

    except HTTPException:
        raise

    except Exception as error:
        LOGGER.exception(
            "Emotion prediction failed"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Emotion inference failed. "
                "Check model compatibility and logs."
            ),
        )


@app.post("/beauty/scan")
async def beauty_scan_endpoint(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
):
    validate_upload(file)
    data = await read_upload(file)

    try:
        return scan_beauty(data)

    except Exception as error:
        LOGGER.exception(
            "Beauty scan failed"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Beauty analysis failed. "
                "Check image quality and server logs."
            ),
        )


@app.get("/analytics/dataset")
def dataset_analytics(
    user: User = Depends(current_user),
):
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "..",
            "data",
            "AI_Face_Mood_Beauty_Dataset_1000(1).csv",
        )
    )

    if not os.path.exists(path):
        return {
            "available": False,
            "rows": 0,
        }

    df = pd.read_csv(path)

    return {
        "available": True,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "mood_distribution": (
            df["mood_label"]
            .value_counts()
            .to_dict()
            if "mood_label" in df.columns
            else {}
        ),
        "beauty_concern_distribution": (
            df["primary_beauty_concern"]
            .value_counts()
            .to_dict()
            if "primary_beauty_concern" in df.columns
            else {}
        ),
    }
