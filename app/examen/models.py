from django.db import models
from django.contrib.auth.models import AbstractUser

#------------------------------- USUARIO ------------------------------------------
class Usuario(AbstractUser):
    
    ADMINISTRADOR = 1
    INVESTIGADOR = 2
    PACIENTE = 3
    
    ROLES = (
        (ADMINISTRADOR, 'Administrador'),
        (INVESTIGADOR, 'Investigador'),
        (PACIENTE, 'Paciente'),
    )
    
    rol = models.PositiveSmallIntegerField(
        choices=ROLES,
        default=1,
    )
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

#------------------------------- INVESTIGADOR ------------------------------------------
class Investigador(models.Model):
    # Relacion 1:1 con Usuario
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='investigador')
    
    puesto = models.CharField(max_length=50,blank=True, null=True, default='No Definido')

    def __str__(self):
        return f"Investigador: {self.usuario.username}"

#------------------------------- PACIENTE ------------------------------------------
class Paciente(models.Model):
    # Relacion 1:1 con Usuario
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='paciente')
    
    edad = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Paciente: {self.usuario.username}"

#------------------------------- FARMACO ------------------------------------------
class Farmaco(models.Model): 
    
    nombre = models.CharField(max_length=100) 
    apto_para_ensayos = models.BooleanField()
    
    def __str__(self): 
        return self.nombre 


#------------------------------- ENSAYO-CLINICO ------------------------------------------
class EnsayoClinico(models.Model):
    
    nombre = models.CharField(max_length=100) 
    descripcion = models.TextField()
    # Relacion ManyToOne con Farmaco
    farmaco = models.ForeignKey(Farmaco, on_delete=models.CASCADE)
    # Relacion ManyToMany con Paciente
    pacientes = models.ManyToManyField('Paciente') 
    nivel_seguimiento = models.IntegerField() 
    fecha_inicio = models.DateField() 
    fecha_fin = models.DateField() 
    activo = models.BooleanField(default=True)
    # Relacion ManyToOne con Investigador
    creado_por = models.ForeignKey('Investigador', on_delete=models.CASCADE)
    
    def __str__(self): 
        return self.nombre
