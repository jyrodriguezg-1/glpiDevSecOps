# --------------------------------------------------------------
#  → Imagen base ligera de Python
# --------------------------------------------------------------
FROM python:3.11-slim

# --------------------------------------------------------------
#  1) Instalación de utilidades mínimas del sistema 
# --------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------
#  2) Definir directorio de trabajo y copiar requirements
# --------------------------------------------------------------
WORKDIR /glpi-bot
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------------------
#  3) Copiar el código del bot
# --------------------------------------------------------------
COPY app.py .

# --------------------------------------------------------------
#  4) Exponer el puerto en el que escucharemos (8000)
# --------------------------------------------------------------
EXPOSE 8000

# --------------------------------------------------------------
#  5) Comando por defecto: ejecutar directamente el servidor
# --------------------------------------------------------------
CMD ["python", "app.py"]
