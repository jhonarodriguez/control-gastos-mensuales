FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/config /app/logs /tmp/control_gastos \
    && useradd -m -u 10001 appuser \
    && chown -R appuser:appuser /app /tmp/control_gastos

EXPOSE 8080

VOLUME ["/app/config", "/app/logs", "/tmp/control_gastos"]

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request; p=os.getenv('PORT','8080'); urllib.request.urlopen(f'http://127.0.0.1:{p}/api/config', timeout=3)" || exit 1

CMD ["sh", "-c", "python web_server.py --no-browser --port ${PORT:-8080}"]
