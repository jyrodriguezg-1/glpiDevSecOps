# glpi-bot/Dockerfile
FROM python:3.12-slim

# ──────────────────────────────────────────────
# 1. Variables de entorno (valores reales en .env)
# ──────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    GLPI_API_URL="" \
    GLPI_APP_TOKEN="" \
    GLPI_USER_TOKEN="" \
    BOT_TOKEN=""

# ──────────────────────────────────────────────
# 2. Dependencias
# ──────────────────────────────────────────────
RUN pip install --no-cache-dir fastapi==0.110.2 "uvicorn[standard]"==0.29.0 requests==2.32.2 python-dotenv==1.0.1

# ──────────────────────────────────────────────
# 3. Copiar el código
# ──────────────────────────────────────────────
WORKDIR /app
COPY app.py /app/app.py

EXPOSE 8000
VOLUME ["/app/logs"]

CMD ["uvicorn", "app:api", "--host", "0.0.0.0", "--port", "8000"]
