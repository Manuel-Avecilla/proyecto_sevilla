from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

#------------------------------- USUARIO ------------------------------------------
class Usuario(AbstractUser):
    total_score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.username} ({self.total_score} pts)"

#------------------------------- PREGUNTA ------------------------------------------
class Pregunta(models.Model):
    category = models.CharField(max_length=100)
    phrase = models.CharField(max_length=120, unique=True)
    clue = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.category}: {self.phrase}"

#------------------------------- PARTIDA (MATCH) ------------------------------------------
class Partida(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='partidas')
    score = models.IntegerField()
    played_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.usuario.username} - {self.score} pts ({self.played_at})"
