FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the BGE-small weights into the image. This is the difference between a
# five-second and a forty-second first boot in front of an examiner.
ENV FASTEMBED_CACHE_PATH=/app/.model-cache
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"

COPY src/ ./src/
COPY data/ ./data/
COPY web/ ./web/
COPY tools/ ./tools/
COPY run_app.py .

ENV PYTHONPATH=/app/src PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "run_app.py", "--host", "0.0.0.0", "--port", "8000"]
