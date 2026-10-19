FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 \
    APP_ENV=production COOKIE_SECURE=true DATABASE_PATH=/app/instance/campusrelay.db
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 appuser \
  && mkdir -p /app/instance && chown -R appuser:appuser /app
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser static/ ./static/
COPY --chown=appuser:appuser data/ ./data/
USER appuser
EXPOSE 8000
CMD ["sh","-c","exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
