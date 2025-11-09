# Usar imagen base oficial de Python
FROM python:3.11-slim-bullseye

# Información del mantenedor
LABEL maintainer="jardin@example.com"
LABEL description="Django application for Jardin project"

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario sin privilegios para ejecutar la aplicación
RUN groupadd -r django && useradd -r -g django django

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove gcc

# Crear directorios de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias de Python
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ .
COPY scripts/entrypoint.sh /entrypoint.sh

# Crear directorios para archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/mediafiles

# Hacer el script de entrada ejecutable
RUN chmod +x /entrypoint.sh

# Cambiar permisos de archivos a usuario django
RUN chown -R django:django /app /entrypoint.sh

# Cambiar a usuario no privilegiado
USER django

# Puerto que expone la aplicación
EXPOSE 8000

# Comando de entrada
ENTRYPOINT ["/entrypoint.sh"]