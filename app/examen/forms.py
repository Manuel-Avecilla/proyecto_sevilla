# ============================================================
# region Importaciones
# ============================================================

from django import forms
from django.forms import ModelForm
from examen.models import *
from django.contrib.auth.forms import UserCreationForm

from datetime import date

# endregion
# ============================================================


# ============================================================
# region Formulario Registro
# ============================================================
class RegistroUsuarioForm(UserCreationForm):
    roles = (
        (Usuario.PACIENTE, 'Paciente'),
        (Usuario.INVESTIGADOR, 'Investigador'),
    )   

    edad = forms.IntegerField(
        label="Edad (Solo para Pacientes)",
        required=False
    )

    rol = forms.ChoiceField(choices=roles)
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2','rol','edad')
    
    def clean(self):
        
        #Validamos con el modelo actual
        super().clean()
        
        # Obtener datos
        rol = self.cleaned_data.get('rol')
        edad = self.cleaned_data.get('edad')

        #Comprobamos
        if(rol == '3' and edad is None):
            self.add_error("edad", "Debes rellenar la Edad.")
        
        if(rol == '2' and edad is not None):
            self.add_error("edad", "Solo pueden rellenar los Pacientes.")


        #Siempre devolvemos el conjunto de datos.
        return self.cleaned_data
    
# endregion
# ============================================================






# ============================================================
# region Formulario Modelo
# ============================================================

class EnsayoClinicoForm(ModelForm):
    class Meta:
        model = EnsayoClinico
        fields = ["nombre","descripcion","farmaco","pacientes","nivel_seguimiento","fecha_inicio","fecha_fin","activo"]
        labels = {
            "nombre":("Nombre del Ensayo Clinico"),
            "descripcion":("Descripcion del Ensayo Clinico"),
            "farmaco":("Farmaco Asociado"),
            "pacientes":("Pacientes del Ensayo Clinico"),
            "nivel_seguimiento":("Nivel de Seguimiento"),
            "fecha_inicio":("Fecha de Inicio"),
            "fecha_fin":("Fecha Final"),
            "activo":("¿Ensayo Clinico Activo?")
        }
        help_texts = {
            "nombre":("50 caracteres como máximo"),
            "descripcion":("100 caracteres como máximo")
        }
        widgets = {
            "fecha_inicio": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "pacientes": forms.SelectMultiple(
                attrs={
                'class': 'form-select',
                'size': '6'
                }
            ),
        }

    def clean(self):
        #Validamos con el modelo actual
        super().clean()
        
        #Obtenemos los campos 
        nombre = self.cleaned_data.get("nombre")
        descripcion = self.cleaned_data.get("descripcion")
        farmaco = self.cleaned_data.get("farmaco")
        pacientes = self.cleaned_data.get("pacientes")
        nivel_seguimiento = self.cleaned_data.get("nivel_seguimiento")
        fecha_inicio = self.cleaned_data.get("fecha_inicio")
        fecha_fin = self.cleaned_data.get("fecha_fin")

        #Comprobamos
        #Nombre único: (0,5 puntos)
        if(not self.instance.pk and nombre and EnsayoClinico.objects.filter(nombre=nombre).exists()):
            self.add_error("nombre", "El nombre del Ensayo Clinico ya existe. Debe ser único.")
        
        #Descripción ≥ 100 caracteres: (0,2 puntos)
        if descripcion and len(descripcion) < 100:
            self.add_error("descripcion", "La descripción debe tener al menos 100 caracteres.")
            
        #Fármaco apto: (0,5 puntos)
        if farmaco and not farmaco.apto_para_ensayos:
            self.add_error("farmaco", "El fármaco seleccionado no es apto para ensayos clínicos.")
            
        #Pacientes mayores de edad: (0,5 puntos)
        if pacientes:
            pacientes_menores = pacientes.filter(edad__lt=18)
            if pacientes_menores.exists():
                self.add_error("pacientes", "Todos los pacientes deben ser mayores de edad (18 años o más).")
        
        #Nivel de seguimiento 0-10: (0,2 puntos)  
        if nivel_seguimiento is not None:
            if nivel_seguimiento < 0 or nivel_seguimiento > 10:
                self.add_error("nivel_seguimiento", "El nivel de seguimiento debe estar entre 0 y 10.")
        
        #Fecha inicio < fecha fin: (0,3 puntos)  
        if fecha_inicio and fecha_fin:
            if fecha_inicio >= fecha_fin:
                self.add_error("fecha_inicio", "La fecha de inicio debe ser anterior a la fecha de fin.")
        
        #Fecha fin ≥ hoy: (0,3 puntos)
        fechaHoy = date.today()
        if fecha_fin and fecha_fin <= fechaHoy:
            self.add_error("fecha_fin", "La fecha de fin debe ser hoy o una fecha futura.")

        #Siempre devolvemos el conjunto de datos.
        return self.cleaned_data

# endregion
# ============================================================




# ============================================================
# region Formulario Busqueda Avanzada
# ============================================================

class EnsayoClinicoBuscarAvanzada(forms.Form):

    # Que contenga un texto en nombre o descripción: (0,2 puntos)
    texto_contiene = forms.CharField(
        label='Nombre o Descripcion contiene',
        help_text="(Opcional)",
        required=False
    )
    
    # Fecha desde y fecha hasta del inicio del ensayo a la indicada: (0,3 puntos) 
    fecha_desde = forms.DateField(
        label='Fecha Ensayo Clinico desde',
        help_text="(Opcional)",
        required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    fecha_hasta = forms.DateField(
        label='Fecha Ensayo Clinico hasta',
        help_text="(Opcional)",
        required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    
    #Nivel de seguimiento mayo a un valor : (0,2 puntos) 
    nivel_seguimiento_mayor = forms.IntegerField(
        label='Nivel de Seguimiento mayor a',
        help_text="(Opcional)",
        required=False,
        min_value=0,
        max_value=10,
    )
    
    # Selección múltiple de pacientes:  (0,4 puntos)  
    pacientes = forms.ModelMultipleChoiceField(
        label='Pacientes',
        help_text="(Opcional)",
        required=False,
        queryset=Paciente.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-select',
                'size': '6'
            }
        ),
    )
    
    # Ensayos activos:  (0,4 puntos)  
    ensayos_activos = forms.BooleanField(
        label='Solo Ensayos Activos',
        help_text="(Opcional)",
        required=False,
    )
    
    
    def clean(self):
        
        super().clean()
        
        #Obtenemos los campos
        texto_contiene = self.cleaned_data.get('texto_contiene')
        fecha_desde = self.cleaned_data.get('fecha_desde')
        fecha_hasta = self.cleaned_data.get('fecha_hasta')
        nivel_seguimiento_mayor = self.cleaned_data.get('nivel_seguimiento_mayor')
        pacientes = self.cleaned_data.get('pacientes')
        ensayos_activos = self.cleaned_data.get('ensayos_activos')
        
        #Comprobamos
        
        if (
            texto_contiene == "" and
            fecha_desde is None and
            fecha_hasta is None and
            nivel_seguimiento_mayor is None and
            len(pacientes) == 0 and
            not ensayos_activos
        ):
            self.add_error('texto_contiene','Debes rellenar al menos un campo.')
            self.add_error('fecha_desde','Debes rellenar al menos un campo.')
            self.add_error('fecha_hasta','Debes rellenar al menos un campo.')
            self.add_error('nivel_seguimiento_mayor','Debes rellenar al menos un campo.')
            self.add_error('pacientes','Debes rellenar al menos un campo.')
            self.add_error('ensayos_activos','Debes rellenar al menos un campo.')
        
        if(
            not fecha_desde is None and
            not fecha_hasta is None and
            fecha_hasta < fecha_desde
            ):
            self.add_error('fecha_desde','Rango de fecha no valido.')
            self.add_error('fecha_hasta','Rango de fecha no valido.')
        
        #Siempre devolvemos el conjunto de datos.
        return self.cleaned_data

# endregion
# ============================================================