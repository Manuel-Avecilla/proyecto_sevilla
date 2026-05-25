# ============================================================
# region Importaciones
# ============================================================

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone

# endregion
# ============================================================

# python manage.py migrate          <-- Comando para generar la base de datos
# python manage.py generar_grupos   <-- Comando para generar los grupos y permisos
# python manage.py generar_datos    <-- Comando para generar los datos y rellenar la base de datos

# python manage.py dumpdata --indent 4 > examen/fixtures/datos.json   <-- Comando para guardar los datos


class Command(BaseCommand):
    help = 'Generando datos usando Faker'

    def handle(self, *args, **kwargs):
        fake = Faker('es_ES')  # Faker en español

        self.stdout.write("Generando usuarios...")

        self.stdout.write(self.style.SUCCESS("Datos generados correctamente."))