import csv
from pathlib import Path

from PIL import Image


SOURCE_CSV = Path(
    r"D:\Moodify_100_100_Competition_Build\Moodify_100_100_Competition_Build\fer2013.csv"
)

OUTPUT_ROOT = Path(
    r"D:\Moodify_100_100_Competition_Build\Moodify_100_100_Competition_Build\evaluation_data\test"
)


LABELS = {
    0: "angry",
    1: "disgust",
    2: "fear",
    3: "happy",
    4: "sad",
    5: "surprise",
    6: "neutral",
}


def main():

    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"FER2013 CSV not found:\n{SOURCE_CSV}"
        )

    for label in LABELS.values():
        (OUTPUT_ROOT / label).mkdir(
            parents=True,
            exist_ok=True
        )

    counters = {
        label: 0
        for label in LABELS.values()
    }

    with SOURCE_CSV.open(
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        required = {
            "emotion",
            "pixels",
            "Usage",
        }

        missing = required - set(
            reader.fieldnames or []
        )

        if missing:
            raise ValueError(
                "CSV is missing columns: "
                + ", ".join(sorted(missing))
            )

        for row in reader:

            # Use the official held-out public test split.
            # Do not use Training.
            if row["Usage"] != "PrivateTest":
                continue

            emotion_id = int(
                row["emotion"]
            )

            label = LABELS.get(
                emotion_id
            )

            if label is None:
                continue

            pixels = [
                int(value)
                for value in row[
                    "pixels"
                ].split()
            ]

            if len(pixels) != 48 * 48:
                continue

            image = Image.new(
                "L",
                (48, 48)
            )

            image.putdata(
                pixels
            )

            counters[label] += 1

            filename = (
                OUTPUT_ROOT
                / label
                / f"{label}_{counters[label]:05d}.png"
            )

            image.save(
                filename
            )

    print()
    print("=" * 60)
    print("FER2013 TEST SET CREATED")
    print("=" * 60)

    total = 0

    for label in LABELS.values():

        count = counters[label]
        total += count

        print(
            f"{label:10s}: {count}"
        )

    print("-" * 60)
    print(
        f"Total     : {total}"
    )

    print(
        "Location  :",
        OUTPUT_ROOT
    )


if __name__ == "__main__":
    main()