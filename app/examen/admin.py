from django.contrib import admin
from .models import Usuario, Pregunta, Partida, PartidaMultijugador, JugadorPartida

admin.site.register(Usuario)
admin.site.register(Pregunta)
admin.site.register(Partida)
admin.site.register(PartidaMultijugador)
admin.site.register(JugadorPartida)