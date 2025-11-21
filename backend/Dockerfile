# Usa una imagen oficial de Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# --- ¡ESTA ES LA PARTE QUE FALTABA! ---
# Instala 'build-essential' y otras dependencias del sistema
# que son necesarias para compilar 'bcrypt' y 'psycopg2'
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
# --- FIN DE LA CORRECCIÓN ---

# Copia e instala las librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código
COPY . .

# (El comando 'uvicorn' se ejecuta desde 'docker-compose.yml')