"""
Evaluate the deployed/trained CNN on a HELD-OUT IMAGE TEST SET.

Expected structure:
evaluation_data/test/
    angry/
        image1.jpg
    disgust/
        image2.jpg
    fear/
    happy/
    sad/
    surprise/
    neutral/

IMPORTANT:
- Do not evaluate on the training data.
- The folder/class order must match the model's label mapping.
- This script does not train the model.
- It produces real metrics; it never fabricates them.

Run:
    python evaluate_model.py --dataset-root "../evaluation_data/test"

Output:
    backend/model_metrics.json
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

from model import EMOTIONS, model, predict_emotion, model_metadata


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def iter_images(root: Path):
    for label in EMOTIONS:
        label_dir = root / label

        if not label_dir.exists():
            print(
                f"WARNING: missing class folder: {label_dir}"
            )
            continue

        for file in sorted(
            label_dir.rglob("*")
        ):
            if file.suffix.lower() in IMAGE_EXTENSIONS:
                yield label, file


def evaluate(dataset_root: Path):

    pairs = list(
        iter_images(dataset_root)
    )

    if not pairs:
        raise RuntimeError(
            "No images were found. "
            "Expected class folders under the test directory."
        )

    y_true = []
    y_pred = []

    total_latency = 0.0

    for index, (true_label, image_path) in enumerate(pairs, 1):

        started = time.perf_counter()

        result = predict_emotion(
            image_path
        )

        total_latency += (
            time.perf_counter() - started
        )

        y_true.append(true_label)
        y_pred.append(
            result["emotion"]
        )

        print(
            f"[{index}/{len(pairs)}] "
            f"{image_path.name} -> "
            f"{result['emotion']} "
            f"({result['confidence']:.1f}%)"
        )

    labels = EMOTIONS

    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=labels,
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    result = {
        "evaluation_protocol": {
            "dataset_type": "held-out image test set",
            "sample_count": len(y_true),
            "class_labels": labels,
        },

        "metrics": {
            "accuracy": round(
                float(
                    accuracy_score(
                        y_true,
                        y_pred
                    )
                ),
                6
            ),

            "macro_precision": round(
                float(
                    precision_score(
                        y_true,
                        y_pred,
                        labels=labels,
                        average="macro",
                        zero_division=0,
                    )
                ),
                6
            ),

            "macro_recall": round(
                float(
                    recall_score(
                        y_true,
                        y_pred,
                        labels=labels,
                        average="macro",
                        zero_division=0,
                    )
                ),
                6
            ),

            "macro_f1": round(
                float(
                    f1_score(
                        y_true,
                        y_pred,
                        labels=labels,
                        average="macro",
                        zero_division=0,
                    )
                ),
                6
            ),

            "weighted_f1": round(
                float(
                    f1_score(
                        y_true,
                        y_pred,
                        labels=labels,
                        average="weighted",
                        zero_division=0,
                    )
                ),
                6
            ),

            "mean_inference_ms": round(
                (
                    total_latency
                    /
                    len(y_true)
                )
                * 1000,
                3
            ),
        },

        "per_class": report,

        "confusion_matrix": {
            "labels": labels,
            "matrix": matrix.tolist(),
        },

        "model": model_metadata(),
    }

    return result


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset-root",
        required=True,
        type=Path,
        help="Held-out test directory.",
    )

    parser.add_argument(
        "--output",
        default="model_metrics.json",
        type=Path,
        help="Output JSON file.",
    )

    args = parser.parse_args()

    results = evaluate(
        args.dataset_root
    )

    args.output.write_text(
        json.dumps(
            results,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("MOODIFY MODEL EVALUATION")
    print("=" * 60)
    print(
        "Accuracy:",
        results["metrics"]["accuracy"]
    )
    print(
        "Macro F1:",
        results["metrics"]["macro_f1"]
    )
    print(
        "Mean inference:",
        results["metrics"]["mean_inference_ms"],
        "ms"
    )
    print(
        "Saved:",
        args.output.resolve()
    )


if __name__ == "__main__":
    main()
