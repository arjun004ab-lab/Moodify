import csv
from pathlib import Path
from PIL import Image

SOURCE_CSV = Path("fer2013.csv")

OUTPUT_ROOT = Path(
    "evaluation_data"
) / "test"

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
            f"FER2013 CSV not found:\n{SOURCE_CSV.resolve()}\n\n"
            "Place your FER2013 CSV in the project root and name it "
            "'fer2013.csv'."
        )

    for label in LABELS.values():
        (OUTPUT_ROOT / label).mkdir(
            parents=True,
            exist_ok=True
        )

    counts = {
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
            "Usage"
        }

        missing = required - set(
            reader.fieldnames or []
        )

        if missing:
            raise ValueError(
                "FER2013 CSV is missing columns: "
                + ", ".join(sorted(missing))
            )

        for row in reader:

            # PrivateTest is the original held-out
            # FER2013 test split.
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

            pixel_values = [
                int(value)
                for value in row["pixels"].split()
            ]

            if len(pixel_values) != 48 * 48:
                continue

            image = Image.new(
                "L",
                (48, 48)
            )

            image.putdata(
                pixel_values
            )

            counts[label] += 1

            filename = (
                OUTPUT_ROOT
                / label
                / f"{label}_{counts[label]:05d}.png"
            )

            image.save(filename)

    print()
    print("=" * 60)
    print("FER2013 TEST SET CREATED")
    print("=" * 60)

    total = 0

    for label in LABELS.values():
        count = counts[label]
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
        OUTPUT_ROOT.resolve()
    )


if __name__ == "__main__":
    main()
