# Examen - Desarrollo Web Entorno Servidor

Examen de Formularios, Sesiones y Permisos en Django.

---
## Instalación y ejecución en local

#### 1. Clonar el repositorio:
```bash
git clone git@github.com:Manuel-Avecilla/DWS_Examen_Manuel.git
```
#### 2. Acceder al directorio del proyecto:
```bash
cd DWS_Examen_Manuel/app/
```
#### 3. Crear un entorno virtual:
```bash
python3 -m venv myvenv
```
#### 4. Activar el entorno virtual:
```bash
source myvenv/bin/activate
```
#### 5. Actualizar `pip`:
```bash
python -m pip install --upgrade pip
```
#### 6. Instalar los requerimientos del proyecto:
```bash
pip install -r requirements.txt
```
#### 7. Crear la base de datos y aplicar migraciones:
```bash
python manage.py migrate
```
#### 8. Cargar datos iniciales:
```bash
python manage.py loaddata examen/fixtures/datos.json
```
#### 9. Iniciar el servidor de desarrollo:
```bash
python manage.py runserver
```
---
## Documentación

Para mantener el README principal más limpio, la documentación detallada se encuentra en los siguientes archivos:

- [Modelos del Sistema](docs/modelos.md)
- [URLS del Sistema](docs/url.md)

---

## Tecnologías
- **Framework:** Django (Python)
- **Base de datos:** SQLite
- **ORM:** Django Models

---

## Autor
**Manuel Avecilla 2ºDAW.**
