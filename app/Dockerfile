# Usamos una imagen base ligera de Python 3.12
FROM python:3.12-slim

# Evitar la escritura de archivos .pyc y forzar logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas (junto con Gunicorn)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar el código fuente del proyecto
COPY . .

# Recopilar los archivos estáticos en /app/staticfiles
RUN python manage.py collectstatic --noinput

# Exponer el puerto de Gunicorn
EXPOSE 8000

# Ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:8000", "mysite.wsgi:application"]
