from model import EMOTIONS, model, model_metadata

print("IMPORT TEST: PASS")
print("INPUT :", model.input_shape)
print("OUTPUT:", model.output_shape)
print("LABELS:", EMOTIONS)
print("METADATA:")
print(model_metadata())
