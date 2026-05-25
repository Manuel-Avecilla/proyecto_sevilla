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

#--------------------------- PARTIDA MULTIJUGADOR --------------------------------------
class PartidaMultijugador(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='partidas_multijugador_creadas')
    estado = models.CharField(max_length=20, default='ESPERANDO') # ESPERANDO, JUGANDO, TERMINADA
    preguntas_ids = models.CharField(max_length=255, default='') # Comma-separated list of Pregunta IDs, e.g. "1,2,3"
    panel_actual_index = models.IntegerField(default=0) # Index in the list of questions
    letras_usadas = models.TextField(default='') # Comma-separated list of letters guessed
    jugador_actual_turno = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='turnos_multijugador_activos')
    valor_ruleta_actual = models.CharField(max_length=20, null=True, blank=True)
    fase_turno = models.CharField(max_length=30, default='GIRAR') # GIRAR, ADIVINAR
    ultimo_mensaje_suceso = models.CharField(max_length=255, default='', blank=True)
    creada_en = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Partida Multijugador {self.codigo} ({self.estado})"

#----------------------------- JUGADOR PARTIDA -----------------------------------------
class JugadorPartida(models.Model):
    partida = models.ForeignKey(PartidaMultijugador, on_delete=models.CASCADE, related_name='jugadores')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    puntos_partida = models.IntegerField(default=0)
    orden = models.IntegerField(default=0) # Turn order index (0, 1, 2...)

    class Meta:
        unique_together = ('partida', 'usuario')

    def __str__(self):
        return f"{self.usuario.username} en Partida {self.partida.codigo} ({self.puntos_partida} pts)"
