# Ruleta Sevillana en Django

Este proyecto es una migración completa de la aplicación **Ruleta Sevillana** de Node.js + MySQL a **Django + SQLite**, integrando el sistema de autenticación de Django, vistas nativas para clasificaciones y una API JSON para el funcionamiento del juego.

---

## Instalación y ejecución en local

#### 1. Clonar el repositorio:
```bash
git clone https://github.com/Manuel-Avecilla/proyecto_sevilla.git
```
#### 2. Acceder al directorio del proyecto:
```bash
cd proyecto_sevilla/app/
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
python manage.py loaddata examen/fixtures/preguntas.json
```
#### 9. Iniciar el servidor de desarrollo:
```bash
python manage.py runserver
```

---

## 🛠️ Tecnologías y Estructura
- **Backend:** Django 5.x (Python 3)
- **Base de datos:** SQLite (con `PRAGMA journal_mode=WAL;` y carga optimizada de datos)
- **Autenticación:** Sesiones nativas de Django + endpoints JSON compatibles con el frontend.
- **Frontend:** HTML5, CSS3, JavaScript (adaptado con Bootstrap y sistema de plantillas Django).

---

## 📊 Modelos del Sistema (Base de Datos)
- **Usuario:** Cuenta de usuario que registra la puntuación total acumulada (`total_score`).
- **Pregunta:** Almacena los paneles del concurso (`category`, `phrase` y `clue`).
- **Partida (Match):** Registra cada partida finalizada por los usuarios (`usuario`, `score` y `played_at`).
