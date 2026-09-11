from model import predict_emotion

IMAGE = "happy_test.jpg"

result = predict_emotion(IMAGE)

print("\n==============================")
print("MOODIFY CNN DIAGNOSTIC")
print("==============================")

print("Emotion    :", result.get("emotion"))
print("Confidence :", result.get("confidence"), "%")

print("\nProbabilities:")

probabilities = result.get("probabilities", {})

for emotion, probability in sorted(
    probabilities.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{emotion:10s}: {probability:6.2f}%")