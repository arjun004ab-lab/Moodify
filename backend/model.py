import hashlib
import io
import json
import logging
import os
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

LOGGER = logging.getLogger("moodify.model")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = Path(
    os.getenv(
        "MOODIFY_MODEL_PATH",
        str(BASE_DIR / "models" / "emotion_cnn.h5")
    )
)

DEFAULT_EMOTIONS = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "sad",
    "surprise",
    "neutral",
]

raw_labels = os.getenv(
    "MOODIFY_EMOTION_LABELS",
    ",".join(DEFAULT_EMOTIONS)
)

EMOTIONS = [
    item.strip().lower()
    for item in raw_labels.split(",")
    if item.strip()
]

if len(EMOTIONS) != 7:
    raise ValueError(
        "MOODIFY_EMOTION_LABELS must contain exactly 7 labels."
    )

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"CNN model not found: {MODEL_PATH}"
    )

LOGGER.info("Loading CNN model from %s", MODEL_PATH)

model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False
)

LOGGER.info(
    "CNN loaded. input=%s output=%s",
    model.input_shape,
    model.output_shape
)

# Optional OpenCV dependency. The CNN can still run without it.
FACE_DETECTOR = None

try:
    import cv2

    if hasattr(cv2, "CascadeClassifier"):
        cascade_path = (
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )
        detector = cv2.CascadeClassifier(cascade_path)

        if not detector.empty():
            FACE_DETECTOR = detector
            LOGGER.info("OpenCV Haar face detector ready.")
        else:
            LOGGER.warning(
                "OpenCV Haar cascade could not be loaded."
            )
    else:
        LOGGER.warning(
            "OpenCV does not expose CascadeClassifier. "
            "Full-image preprocessing will be used."
        )

except Exception as exc:
    LOGGER.warning(
        "OpenCV face detection disabled: %s",
        exc
    )


def model_sha256() -> str:
    digest = hashlib.sha256()

    with MODEL_PATH.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def model_metadata() -> dict:
    shape = model.input_shape
    if isinstance(shape, list):
        shape = shape[0]

    return {
        "model_file": MODEL_PATH.name,
        "model_sha256": model_sha256(),
        "input_shape": list(shape),
        "output_shape": list(model.output_shape),
        "class_labels": EMOTIONS,
        "face_detector": FACE_DETECTOR is not None,
    }


def read_image(data):
    if isinstance(data, (bytes, bytearray)):
        return np.asarray(
            Image.open(
                io.BytesIO(bytes(data))
            ).convert("RGB")
        )

    if isinstance(data, str):
        return np.asarray(
            Image.open(data).convert("RGB")
        )

    if isinstance(data, Path):
        return np.asarray(
            Image.open(data).convert("RGB")
        )

    raise TypeError(
        "Image data must be bytes or a file path."
    )


def crop_largest_face(rgb_image):
    if FACE_DETECTOR is None:
        return rgb_image

    try:
        import cv2

        gray = cv2.cvtColor(
            rgb_image,
            cv2.COLOR_RGB2GRAY
        )

        faces = FACE_DETECTOR.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40)
        )

        if len(faces) == 0:
            return rgb_image

        x, y, w, h = max(
            faces,
            key=lambda box: int(box[2] * box[3])
        )

        pad_x = int(w * 0.16)
        pad_y = int(h * 0.20)

        left = max(0, x - pad_x)
        top = max(0, y - pad_y)
        right = min(
            rgb_image.shape[1],
            x + w + pad_x
        )
        bottom = min(
            rgb_image.shape[0],
            y + h + pad_y
        )

        crop = rgb_image[
            top:bottom,
            left:right
        ]

        return crop if crop.size else rgb_image

    except Exception as exc:
        LOGGER.warning(
            "Face detection failed; using full image: %s",
            exc
        )
        return rgb_image


def preprocess(data):
    rgb = crop_largest_face(
        read_image(data)
    )

    image = Image.fromarray(
        rgb
    ).convert("L")

    shape = model.input_shape
    if isinstance(shape, list):
        shape = shape[0]

    height = int(shape[1] or 48)
    width = int(shape[2] or 48)
    channels = int(shape[3] or 1)

    image = image.resize(
        (width, height)
    )

    x = np.asarray(
        image,
        dtype=np.float32
    ) / 255.0

    if channels == 1:
        x = x[..., None]

    elif channels == 3:
        x = np.repeat(
            x[..., None],
            3,
            axis=-1
        )

    else:
        raise ValueError(
            f"Unsupported CNN channel count: {channels}"
        )

    return x[None, ...]


def predict_emotion(data):
    raw = np.asarray(
        model.predict(
            preprocess(data),
            verbose=0
        )[0],
        dtype=np.float32
    )

    if raw.ndim != 1:
        raise ValueError(
            f"Unexpected CNN output shape: {raw.shape}"
        )

    if raw.shape[0] != len(EMOTIONS):
        raise ValueError(
            "CNN output/class mismatch: "
            f"{raw.shape[0]} outputs for {len(EMOTIONS)} labels."
        )

    if (
        np.any(raw < 0)
        or not np.isclose(
            float(raw.sum()),
            1.0,
            atol=0.05
        )
    ):
        shifted = raw - np.max(raw)
        exp_values = np.exp(shifted)
        probabilities = exp_values / exp_values.sum()
    else:
        probabilities = raw / max(
            float(raw.sum()),
            1e-8
        )

    index = int(
        np.argmax(probabilities)
    )

    return {
        "emotion": EMOTIONS[index],
        "confidence": round(
            float(probabilities[index] * 100),
            2
        ),
        "probabilities": {
            EMOTIONS[i]: round(
                float(probabilities[i] * 100),
                2
            )
            for i in range(len(EMOTIONS))
        }
    }
