FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY templates/ templates/

# Data volume – mount your RDF files here
VOLUME ["/app/data"]

ENV RDF_DIR=/app/data \
    PORT=5000 \
    FLASK_DEBUG=0

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]
