FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=10000 \
    CUDA_VISIBLE_DEVICES=-1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    TF_NUM_INTRAOP_THREADS=1 \
    TF_NUM_INTEROP_THREADS=1 \
    OMP_NUM_THREADS=1 \
    TF_ENABLE_ONEDNN_OPTS=0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgomp1 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

# Verify the production model exists.
RUN test -f models/emotion_cnn.h5

# Verify the research evaluation artifact exists.
RUN test -f model_metrics.json

# Validate the research artifact structure.
RUN python -c "import json; d=json.load(open('model_metrics.json', encoding='utf-8')); assert d['evaluation_protocol']['sample_count'] > 0; assert 'accuracy' in d['metrics']; assert 'macro_f1' in d['metrics']; print('Evaluation artifact: VALID')"

EXPOSE 10000

CMD ["sh", "-c", "exec gunicorn main:app --bind 0.0.0.0:${PORT:-10000} --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --graceful-timeout 30"]