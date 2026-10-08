# ---------- Stage 1: base (runtime dependencies only) ----------
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------- Stage 2: test (adds pytest/flake8 + tests; used by CI only) ----------
FROM base AS test
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .
CMD ["pytest", "--junitxml=/tmp/reports/junit.xml"]

# ---------- Stage 3: runtime (small, non-root production image) ----------
FROM base AS runtime
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/data && chown appuser:appuser /app/data
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser aceest/ aceest/
ENV ACEEST_DB=/app/data/aceest_fitness.db
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--preload", "app:create_app()"]
