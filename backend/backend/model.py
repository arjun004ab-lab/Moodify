"""
Moodify AI — Emotion CNN Runtime
================================

Single source of truth for:
- model loading
- model metadata
- optional face detection
- preprocessing
- emotion inference

Expected model:
    backend/models/emotion_cnn.h5

Default input:
    48 x 48 x 1 grayscale

Default classes:
    angry, disgust, fear, happy, sad, surprise, neutral

IMPORTANT:
The configured class order MUST match the order used during
training of the H5 model.
"""

from __future__ import annotations

import hashlib
import io
import logging
import os
from pathlib import Path
from typing import Any

import numpy as np
import tensorflow as tf
from PIL import Image


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=os.getenv(
        "LOG_LEVEL",
        "INFO",
    ),
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

LOGGER = logging.getLogger(
    "moodify.model"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_MODEL_PATH = (
    BASE_DIR
    / "models"
    / "emotion_cnn.h5"
)

MODEL_PATH = Path(
    os.getenv(
        "MOODIFY_MODEL_PATH",
        str(DEFAULT_MODEL_PATH),
    )
).resolve()


# ============================================================
# CLASS CONFIGURATION
# ============================================================

DEFAULT_EMOTIONS = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "sad",
    "surprise",
    "neutral",
]


def _load_emotion_labels() -> list[str]:

    raw = os.getenv(
        "MOODIFY_EMOTION_LABELS",
        ",".join(DEFAULT_EMOTIONS),
    )

    labels = [
        item.strip().lower()
        for item in raw.split(",")
        if item.strip()
    ]

    if len(labels) != 7:
        raise ValueError(
            "MOODIFY_EMOTION_LABELS must contain exactly "
            "7 comma-separated labels."
        )

    if len(set(labels)) != len(labels):
        raise ValueError(
            "MOODIFY_EMOTION_LABELS contains duplicate labels."
        )

    return labels


EMOTIONS = _load_emotion_labels()


# ============================================================
# LOAD CNN
# ============================================================

if not MODEL_PATH.exists():

    raise FileNotFoundError(
        "Moodify CNN model was not found.\n"
        f"Expected path: {MODEL_PATH}\n"
        "Place emotion_cnn.h5 in backend/models/ "
        "or set MOODIFY_MODEL_PATH."
    )


LOGGER.info(
    "Loading CNN model: %s",
    MODEL_PATH,
)


model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False,
)


LOGGER.info(
    "CNN loaded. input=%s output=%s",
    model.input_shape,
    model.output_shape,
)


# ============================================================
# OPTIONAL OPENCV FACE DETECTOR
# ============================================================

FACE_DETECTOR = None

try:

    import cv2

    if hasattr(
        cv2,
        "CascadeClassifier",
    ):

        cascade_path = (
            Path(
                cv2.data.haarcascades
            )
            / "haarcascade_frontalface_default.xml"
        )

        detector = cv2.CascadeClassifier(
            str(cascade_path)
        )

        if not detector.empty():

            FACE_DETECTOR = detector

            LOGGER.info(
                "OpenCV Haar face detector: READY"
            )

        else:

            LOGGER.warning(
                "OpenCV Haar detector could not be loaded."
            )

    else:

        LOGGER.warning(
            "OpenCV CascadeClassifier is unavailable. "
            "Full-image preprocessing will be used."
        )

except Exception as error:

    LOGGER.warning(
        "OpenCV face detection disabled: %s",
        error,
    )


# ============================================================
# MODEL METADATA
# ============================================================

def model_sha256() -> str:

    digest = hashlib.sha256()

    with MODEL_PATH.open(
        "rb"
    ) as file:

        for chunk in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):

            digest.update(
                chunk
            )

    return digest.hexdigest()


def model_metadata() -> dict[str, Any]:
    """
    Return auditable metadata for the deployed CNN.
    """

    input_shape = model.input_shape
    output_shape = model.output_shape

    if isinstance(
        input_shape,
        list,
    ):
        input_shape = input_shape[0]

    if isinstance(
        output_shape,
        list,
    ):
        output_shape = output_shape[0]

    return {

        "model_file":
            MODEL_PATH.name,

        "model_path":
            str(MODEL_PATH),

        "model_sha256":
            model_sha256(),

        "framework":
            "TensorFlow / Keras",

        "input_shape":
            list(input_shape),

        "output_shape":
            list(output_shape),

        "class_labels":
            EMOTIONS,

        "face_detector":
            FACE_DETECTOR is not None,

        "loaded":
            model is not None,

    }


# ============================================================
# IMAGE DECODING
# ============================================================

def read_image(
    image_data: bytes | str | Path,
) -> np.ndarray:

    if isinstance(
        image_data,
        (bytes, bytearray),
    ):

        return np.asarray(
            Image.open(
                io.BytesIO(
                    bytes(image_data)
                )
            ).convert("RGB")
        )


    if isinstance(
        image_data,
        (str, Path),
    ):

        path = Path(
            image_data
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Image file not found: {path}"
            )

        return np.asarray(
            Image.open(
                path
            ).convert("RGB")
        )


    raise TypeError(
        "image_data must be image bytes "
        "or a filesystem path."
    )


# ============================================================
# FACE CROPPING
# ============================================================

def crop_largest_face(
    rgb_image: np.ndarray,
) -> tuple[np.ndarray, bool]:

    if FACE_DETECTOR is None:

        return rgb_image, False


    try:

        import cv2

        gray = cv2.cvtColor(
            rgb_image,
            cv2.COLOR_RGB2GRAY,
        )

        faces = FACE_DETECTOR.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40),
        )

        if len(faces) == 0:

            return rgb_image, False


        x, y, w, h = max(
            faces,
            key=lambda box:
                int(
                    box[2] * box[3]
                ),
        )


        pad_x = int(
            w * 0.16
        )

        pad_y = int(
            h * 0.20
        )


        left = max(
            0,
            x - pad_x,
        )

        top = max(
            0,
            y - pad_y,
        )

        right = min(
            rgb_image.shape[1],
            x + w + pad_x,
        )

        bottom = min(
            rgb_image.shape[0],
            y + h + pad_y,
        )


        face = rgb_image[
            top:bottom,
            left:right
        ]


        if face.size == 0:

            return rgb_image, False


        return face, True


    except Exception as error:

        LOGGER.warning(
            "Face detection failed; "
            "using complete image: %s",
            error,
        )

        return rgb_image, False


# ============================================================
# PREPROCESSING
# ============================================================

def preprocess_image(
    image_data: bytes | str | Path,
) -> tuple[np.ndarray, bool]:

    rgb = read_image(
        image_data
    )


    cropped, face_detected = (
        crop_largest_face(
            rgb
        )
    )


    image = Image.fromarray(
        cropped
    ).convert("L")


    shape = model.input_shape

    if isinstance(
        shape,
        list,
    ):
        shape = shape[0]


    height = int(
        shape[1] or 48
    )

    width = int(
        shape[2] or 48
    )

    channels = int(
        shape[3] or 1
    )


    if channels not in (
        1,
        3,
    ):

        raise ValueError(
            "Unsupported CNN channel count: "
            f"{channels}"
        )


    image = image.resize(
        (
            width,
            height,
        ),
        Image.Resampling.BILINEAR,
    )


    array = (
        np.asarray(
            image,
            dtype=np.float32,
        )
        / 255.0
    )


    if channels == 1:

        array = np.expand_dims(
            array,
            axis=-1,
        )

    else:

        array = np.repeat(
            array[..., None],
            3,
            axis=-1,
        )


    array = np.expand_dims(
        array,
        axis=0,
    )


    return array, face_detected


# ============================================================
# PREDICTION
# ============================================================

def predict_emotion(
    image_data: bytes | str | Path,
) -> dict[str, Any]:

    batch, face_detected = (
        preprocess_image(
            image_data
        )
    )


    raw = np.asarray(
        model.predict(
            batch,
            verbose=0,
        )[0],
        dtype=np.float32,
    )


    if raw.ndim != 1:

        raise ValueError(
            "Unexpected CNN output shape: "
            f"{raw.shape}"
        )


    if len(raw) != len(
        EMOTIONS
    ):

        raise ValueError(
            "CNN output/class mismatch. "
            f"Model returned {len(raw)} values, "
            f"but {len(EMOTIONS)} labels are configured."
        )


    if (
        np.any(raw < 0)
        or not np.isclose(
            float(raw.sum()),
            1.0,
            atol=0.05,
        )
    ):

        shifted = (
            raw
            - np.max(raw)
        )

        exp_values = np.exp(
            shifted
        )

        probabilities = (
            exp_values
            /
            exp_values.sum()
        )

    else:

        probabilities = (
            raw
            /
            max(
                float(raw.sum()),
                1e-8,
            )
        )


    predicted_index = int(
        np.argmax(
            probabilities
        )
    )


    return {

        "emotion":
            EMOTIONS[predicted_index],

        "confidence":
            round(
                float(
                    probabilities[
                        predicted_index
                    ]
                    * 100
                ),
                2,
            ),

        "probabilities":
            {
                EMOTIONS[index]:
                    round(
                        float(
                            probabilities[index]
                            * 100
                        ),
                        2,
                    )
                for index in range(
                    len(EMOTIONS)
                )
            },

        "face_detected":
            face_detected,

    }
