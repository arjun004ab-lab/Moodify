"""
Moodify AI — Reproducible Emotion CNN Evaluation
=================================================

Evaluates the deployed emotion CNN on a REAL held-out test set.

Expected dataset:
    evaluation_data/test/
        angry/
        disgust/
        fear/
        happy/
        sad/
        surprise/
        neutral/

This script NEVER invents metrics.

It produces:
- accuracy
- macro precision
- macro recall
- macro F1
- weighted F1
- top-2 accuracy
- mean inference latency
- standard deviation of inference latency
- per-class precision/recall/F1/support
- confusion matrix
- model file hash
- preprocessing metadata
- test-set composition

For stronger research reporting:
- Keep the test set untouched during model development.
- Do not report results from training images.
- Verify that the label order matches model training.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from model import (
    EMOTIONS,
    model,
    model_metadata,
    predict_emotion,
)


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def collect_images(
    dataset_root: Path,
):

    pairs = []


    for label in EMOTIONS:

        class_dir = (
            dataset_root
            / label
        )


        if not class_dir.exists():

            print(
                f"WARNING: Missing class folder: {class_dir}"
            )

            continue


        for file in sorted(
            class_dir.rglob("*")
        ):

            if (
                file.is_file()
                and file.suffix.lower()
                in IMAGE_EXTENSIONS
            ):

                pairs.append(
                    (
                        label,
                        file,
                    )
                )


    return pairs


def evaluate(
    dataset_root: Path,
):

    pairs = collect_images(
        dataset_root
    )


    if not pairs:

        raise RuntimeError(
            "\nNo evaluation images were found.\n\n"
            "Expected folders:\n"
            + "\n".join(
                str(dataset_root / label)
                for label in EMOTIONS
            )
        )


    y_true = []
    y_pred = []

    confidence_values = []
    latency_values = []

    top2_correct = 0

    failed = 0
    face_detected_count = 0


    print()
    print("=" * 72)
    print("MOODIFY — HELD-OUT CNN EVALUATION")
    print("=" * 72)

    print(
        "Dataset:",
        dataset_root,
    )

    print(
        "Images:",
        len(pairs),
    )

    print(
        "Classes:",
        ", ".join(EMOTIONS),
    )

    print()


    for index, (
        true_label,
        image_path,
    ) in enumerate(
        pairs,
        start=1,
    ):

        try:

            started = time.perf_counter()

            result = predict_emotion(
                image_path
            )

            elapsed = (
                time.perf_counter()
                - started
            )


            latency_values.append(
                elapsed * 1000
            )


            predicted_label = (
                result["emotion"]
            )


            confidence = float(
                result["confidence"]
            )


            y_true.append(
                true_label
            )

            y_pred.append(
                predicted_label
            )

            confidence_values.append(
                confidence
            )


            if result.get(
                "face_detected",
                False,
            ):

                face_detected_count += 1


            # ------------------------------------------------
            # TOP-2 ACCURACY
            #
            # The backend returns a probability map.
            # ------------------------------------------------

            probability_map = (
                result.get(
                    "probabilities",
                    {},
                )
            )


            ranked = sorted(
                probability_map.items(),
                key=lambda item:
                    item[1],
                reverse=True,
            )


            top2_labels = [
                label
                for label, _ in ranked[:2]
            ]


            if true_label in top2_labels:

                top2_correct += 1


            print(
                f"[{index:04d}/{len(pairs):04d}] "
                f"TRUE={true_label:<9} "
                f"PRED={predicted_label:<9} "
                f"CONF={confidence:6.2f}% "
                f"TIME={elapsed * 1000:7.2f}ms"
            )


        except Exception as error:

            failed += 1

            print(
                f"[ERROR] {image_path}"
            )

            print(
                f"        {error}"
            )


    if not y_true:

        raise RuntimeError(
            "No samples completed successfully."
        )


    # ========================================================
    # CORE METRICS
    # ========================================================

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )


    macro_precision = precision_score(
        y_true,
        y_pred,
        labels=EMOTIONS,
        average="macro",
        zero_division=0,
    )


    macro_recall = recall_score(
        y_true,
        y_pred,
        labels=EMOTIONS,
        average="macro",
        zero_division=0,
    )


    macro_f1 = f1_score(
        y_true,
        y_pred,
        labels=EMOTIONS,
        average="macro",
        zero_division=0,
    )


    weighted_f1 = f1_score(
        y_true,
        y_pred,
        labels=EMOTIONS,
        average="weighted",
        zero_division=0,
    )


    top2_accuracy = (
        top2_correct
        /
        len(y_true)
    )


    mean_latency = (
        statistics.mean(
            latency_values
        )
        if latency_values
        else 0.0
    )


    std_latency = (
        statistics.stdev(
            latency_values
        )
        if len(latency_values) > 1
        else 0.0
    )


    mean_confidence = (
        statistics.mean(
            confidence_values
        )
        if confidence_values
        else 0.0
    )


    report = classification_report(
        y_true,
        y_pred,
        labels=EMOTIONS,
        target_names=EMOTIONS,
        output_dict=True,
        zero_division=0,
    )


    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=EMOTIONS,
    )


    # ========================================================
    # CLASS DISTRIBUTION
    # ========================================================

    class_distribution = {
        label:
            int(
                sum(
                    1
                    for value in y_true
                    if value == label
                )
            )
        for label in EMOTIONS
    }


    # ========================================================
    # FINAL AUDITABLE RESULT
    # ========================================================

    results = {

        "evaluation_protocol": {

            "type":
                "held-out image test set",

            "dataset_root":
                str(dataset_root),

            "total_images_found":
                len(pairs),

            "successfully_evaluated":
                len(y_true),

            "failed_images":
                failed,

            "class_labels":
                EMOTIONS,

            "class_distribution":
                class_distribution,

            "face_detected_count":
                face_detected_count,

            "face_detection_rate":
                round(
                    face_detected_count
                    /
                    len(y_true),
                    6,
                ),

        },


        "metrics": {

            "accuracy":
                round(
                    float(
                        accuracy
                    ),
                    6,
                ),

            "top2_accuracy":
                round(
                    float(
                        top2_accuracy
                    ),
                    6,
                ),

            "macro_precision":
                round(
                    float(
                        macro_precision
                    ),
                    6,
                ),

            "macro_recall":
                round(
                    float(
                        macro_recall
                    ),
                    6,
                ),

            "macro_f1":
                round(
                    float(
                        macro_f1
                    ),
                    6,
                ),

            "weighted_f1":
                round(
                    float(
                        weighted_f1
                    ),
                    6,
                ),

            "mean_confidence_percent":
                round(
                    float(
                        mean_confidence
                    ),
                    4,
                ),

            "mean_inference_ms":
                round(
                    float(
                        mean_latency
                    ),
                    4,
                ),

            "std_inference_ms":
                round(
                    float(
                        std_latency
                    ),
                    4,
                ),

        },


        "per_class":
            report,


        "confusion_matrix": {

            "labels":
                EMOTIONS,

            "matrix":
                matrix.tolist(),

        },


        "model":
            model_metadata(),

    }


    return results


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Evaluate Moodify's emotion CNN "
            "on a held-out test dataset."
        )
    )


    parser.add_argument(
        "--dataset-root",
        required=True,
        type=Path,
        help=(
            "Root directory containing one "
            "subdirectory per emotion class."
        ),
    )


    parser.add_argument(
        "--output",
        default="model_metrics.json",
        type=Path,
        help="Output JSON path.",
    )


    args = parser.parse_args()


    dataset_root = (
        args.dataset_root.resolve()
    )


    output_path = (
        args.output.resolve()
    )


    if not dataset_root.exists():

        raise FileNotFoundError(
            "Evaluation dataset does not exist:\n"
            f"{dataset_root}"
        )


    results = evaluate(
        dataset_root
    )


    output_path.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )


    metrics = results[
        "metrics"
    ]


    print()
    print("=" * 72)
    print("MOODIFY EVALUATION COMPLETE")
    print("=" * 72)

    print(
        "Accuracy        : "
        f"{metrics['accuracy'] * 100:.2f}%"
    )

    print(
        "Top-2 Accuracy  : "
        f"{metrics['top2_accuracy'] * 100:.2f}%"
    )

    print(
        "Macro Precision : "
        f"{metrics['macro_precision'] * 100:.2f}%"
    )

    print(
        "Macro Recall    : "
        f"{metrics['macro_recall'] * 100:.2f}%"
    )

    print(
        "Macro F1        : "
        f"{metrics['macro_f1'] * 100:.2f}%"
    )

    print(
        "Weighted F1     : "
        f"{metrics['weighted_f1'] * 100:.2f}%"
    )

    print(
        "Mean latency    : "
        f"{metrics['mean_inference_ms']:.2f} ms"
    )

    print(
        "Latency std.    : "
        f"{metrics['std_inference_ms']:.2f} ms"
    )

    print()

    print(
        "Model SHA-256   : "
        f"{results['model']['model_sha256']}"
    )

    print(
        "Saved results   : "
        f"{output_path}"
    )

    print("=" * 72)


if __name__ == "__main__":
    main()
