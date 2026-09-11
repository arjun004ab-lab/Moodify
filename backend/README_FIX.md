# Moodify — Research Evaluation Fix

Replace BOTH files in your active project:

D:\moodify\backend\model.py
D:\moodify\backend\evaluate_model.py

Do not mix the old evaluator with the new model file.

Then run:

cd D:\moodify\backend

& "..\.venv\Scripts\python.exe" -m py_compile ".\model.py"

& "..\.venv\Scripts\python.exe" -m py_compile ".\evaluate_model.py"

& "..\.venv\Scripts\python.exe" ".\test_model_import.py"

Install evaluation dependencies:

& "..\.venv\Scripts\python.exe" -m pip install -r ".\requirements-evaluation.txt"

Run evaluation only against a REAL held-out image test set:

& "..\.venv\Scripts\python.exe" ".\evaluate_model.py" --dataset-root "..\evaluation_data\test"

Expected test-set structure:

D:\moodify\evaluation_data\test\
    angry\
    disgust\
    fear\
    happy\
    sad\
    surprise\
    neutral\

The evaluator generates:

D:\moodify\backend\model_metrics.json

The current model must still be the actual emotion_cnn.h5 that you want to claim as the evaluated model.

CRITICAL:
The EMOTIONS order must match the training label order of the H5.
Do not change the labels just to improve the apparent results.

No accuracy/F1 values should be added to the presentation until this evaluation has completed on a genuine held-out test set.
