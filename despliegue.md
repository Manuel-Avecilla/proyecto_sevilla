# Despliegue de Ruleta Sevillana (Django) en Producción

El despliegue de la aplicación **Ruleta Sevillana** se gestiona utilizando contenedores de Docker, orquestados mediante Docker Compose. Esto permite un entorno de ejecución aislado, predecible y replicable, ideal para servidores locales o instancias en la nube (como AWS EC2).

La arquitectura se compone de tres servicios: la aplicación web (Django servida con Gunicorn), un generador de certificados SSL efímero, y un proxy inverso (Nginx) que maneja el tráfico seguro (HTTPS) y sirve los archivos estáticos de forma directa.

---

## 🏗️ Arquitectura de Despliegue

La arquitectura se basa en tres componentes que se comunican a través de una red privada puente (`ruleta_net`):

1.  **Proxy Inverso (Nginx)**: Actúa como el punto de entrada público, escuchando en el puerto `80` (HTTP) y `443` (HTTPS). Redirige todo el tráfico HTTP a HTTPS de forma automática, maneja el cifrado SSL y sirve los archivos estáticos directamente desde un volumen compartido, liberando de carga al servidor de la aplicación.
2.  **Aplicación Web (Django)**: Ejecuta el código de Django a través de **Gunicorn**, un servidor WSGI de producción de alto rendimiento. Mapea la base de datos local SQLite para persistir las puntuaciones, usuarios y paneles.
3.  **Generador de Certificados (Cert-Generator)**: Contenedor temporal (efímero) que comprueba si existe un certificado SSL en el volumen compartido. Si no existe, genera uno autofirmado de inmediato mediante `openssl`, permitiendo arrancar el servidor HTTPS sin intervención manual.

---

## 📂 Archivos de Configuración Creados

Todos los archivos de configuración se encuentran en el directorio `app/`:

-   **`Dockerfile`**: Define cómo construir la imagen de Django. Instala las dependencias y corre `collectstatic` para recopilar las hojas de estilo y scripts de Bootstrap en un único directorio. Crea la carpeta `/app/data` para almacenar la base de datos.
-   **`docker-compose.yml`**: Define y orquesta los tres contenedores, configurando la persistencia mediante la carpeta `./data` y volúmenes compartidos para certificados y archivos estáticos. Pasa la variable `DJANGO_DB_DIR=/app/data` al contenedor.
-   **`nginx.conf`**: Configura Nginx para realizar la terminación SSL, servir los estáticos en la ruta `/static/` desde el volumen y redirigir el resto de solicitudes a Gunicorn en `http://web:8000`.

---

## ⚙️ Pasos para el Despliegue

Para desplegar la aplicación en cualquier servidor Linux (como Ubuntu Server en AWS EC2):

### 1. Preparación del Servidor
Asegúrate de tener instalados **Docker** y **Docker Compose**. Si estás en Ubuntu:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2
```

### 2. Navegar al Directorio del Proyecto
Navega al directorio `app/` donde se ubican las configuraciones de Docker:
```bash
cd proyecto_sevilla/app/
```

### 3. Levantar los Servicios en Segundo Plano
Construye las imágenes e inicia los servicios:
```bash
sudo docker compose up -d --build
```
*Este comando descargará las imágenes base, construirá el contenedor de Django, generará el certificado SSL autofirmado de forma transparente y levantará el proxy Nginx. Docker Compose creará de forma automática el directorio `./data` en el host.*

### 4. Inicializar y Poblar la Base de Datos
Dado que la base de datos SQLite se almacena en el volumen compartido en `/app/data/db.sqlite3`, ejecuta las migraciones y carga las preguntas iniciales directamente en el contenedor en ejecución:
```bash
# Aplicar migraciones de base de datos
sudo docker compose exec web python manage.py migrate

# Cargar los paneles/preguntas de Sevilla
sudo docker compose exec web python manage.py loaddata preguntas
```

### 5. Crear un Superusuario (Opcional, para el Panel de Control)
Si deseas acceder al panel de administración de Django (`/admin`) en producción para añadir o editar paneles:
```bash
sudo docker compose exec web python manage.py createsuperuser
```

---

## 🔍 Verificación del Funcionamiento

1.  Abre un navegador y accede mediante HTTP a la dirección IP del servidor (ej. `http://<IP_SERVIDOR>`).
2.  Verifica que Nginx redirige de forma automática a la conexión segura `https://<IP_SERVIDOR>`.
3.  Comprueba que la página de inicio carga de forma correcta (los archivos estáticos como Bootstrap deben renderizarse sin problemas).
4.  Inicia sesión o regístrate y juega una partida para corroborar que el flujo multijugador y el guardado de puntuaciones operan adecuadamente.
