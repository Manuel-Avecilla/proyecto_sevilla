from django.contrib import admin
from .models import Usuario, Investigador, Paciente, Farmaco, EnsayoClinico 

admin.site.register(Usuario)
admin.site.register(Investigador)
admin.site.register(Paciente)
admin.site.register(Farmaco)
admin.site.register(EnsayoClinico)