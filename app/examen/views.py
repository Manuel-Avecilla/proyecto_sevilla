# ============================================================
# region Importaciones
# ============================================================

from django.shortcuts import render, redirect
from examen.models import *
from examen.forms import *

from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.decorators import permission_required

from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib import messages

from django.db.models import Q
from datetime import datetime

from django.shortcuts import render
from django.views.defaults import page_not_found

# endregion
# ============================================================

#---HOME---
def home(request):
    return render(request, 'pages/home.html')

#region---USUARIO---

#region --- Detalles Usuario ---
#@permission_required('examen.view_usuario', raise_exception=True)
def dame_usuario(request, id_usuario):
    
    usuario = (
        Usuario.objects
        .get(id=id_usuario)
    )
    
    return render(request, 'models/usuario/detalles_usuario.html',{'Usuario_Mostrar':usuario})
# endregion

#region --- Lista Usuario ---
#@permission_required('examen.view_usuario', raise_exception=True)
def usuarios_listar(request):
    
    usuarios = (
        Usuario.objects
        .all()
    )
    
    return render(request, 'models/usuario/lista_usuario.html',{'Usuarios_Mostrar':usuarios})
# endregion

# endregion

#region---ENSAYO-CLINICO---

#region --- Detalles Ensayo Clinico ---
@permission_required('examen.view_ensayoclinico', raise_exception=True)
def dame_ensayoclinico(request, id_ensayoclinico):
    
    ensayoclinico = (
        EnsayoClinico.objects
        .select_related('farmaco','creado_por')
        .prefetch_related('pacientes')
        .get(id=id_ensayoclinico)
    )
    
    #---Segun-la-Sesion---
    
    #Restricción por usuario logueado: 
    #  Investigador: solo ve los ensayos que haya creado (0,5 puntos)  
    #  Paciente: solo ve ensayos en los que está incluido (0,5 puntos)
    
    mensaje=""
    
    if (request.user.rol == 2): # Investigador
        
        if(ensayoclinico.creado_por.id != request.user.investigador.id):
            messages.error(request, 'Solo puedes ver los Detalles de tus Propios Ensayos Clinicos.')
            return redirect('ensayosclinicos_listar')
        
    elif (request.user.rol == 3): # Paciente
        if not ensayoclinico.pacientes.filter(id=request.user.paciente.id).exists():
            messages.error(request, 'Solo puedes ver los Detalles de los Ensayos Clinicos en los que estás asignado.')
            return redirect('ensayosclinicos_listar')
    
    else: # Administrador
        mensaje="Permisos para ver detalles de cualquier Ensayo Clinico del Sistema."
        pass
    
    
    return render(request, 'models/ensayoclinico/detalles_ensayoclinico.html',{'EnsayoClinico_Mostrar':ensayoclinico, 'Mensaje_Busqueda':mensaje})
# endregion

#region --- Lista Ensayo Clinico ---
@permission_required('examen.view_ensayoclinico', raise_exception=True)
def ensayosclinicos_listar(request):
    
    ensayosclinicos = (
        EnsayoClinico.objects
        .select_related('farmaco','creado_por')
        .prefetch_related('pacientes')
    )
    
    #---Segun-la-Sesion---
    
    #Restricción por usuario logueado: 
    #  Investigador: solo ve los ensayos que haya creado (0,5 puntos)  
    #  Paciente: solo ve ensayos en los que está incluido (0,5 puntos)
    
    mensaje=""
    
    if (request.user.rol == 2): # Investigador
        
        ensayosclinicos = ensayosclinicos.filter(creado_por = request.user.investigador).all()
        mensaje += "· Lista de (Tus Ensayos Clinicos creados)"
        
    elif (request.user.rol == 3): # Paciente
        
        ensayosclinicos = ensayosclinicos.filter(pacientes = request.user.paciente).all()
        mensaje += "· Lista de (Tus Ensayos Clinicos asignados)"
        
    else: # Administrador
        
        ensayosclinicos = ensayosclinicos.all()
        mensaje += "· Lista de (Todos los Ensayos Clinicos del Sistema)"
    
    #-----------------------
    
    return render(request, 'models/ensayoclinico/lista_ensayoclinico.html',{'EnsayosClinicos_Mostrar':ensayosclinicos, 'Mensaje_Busqueda':mensaje})
# endregion

# endregion



# ============================================================
# region CRUD (Create, Read, Update, Delete)
# ============================================================

#region --- CREATE ---
@permission_required('examen.add_ensayoclinico', raise_exception=True)
def ensayoclinico_create(request): #Metodo que controla el tipo de formulario
        
    # Si la petición es GET se creará el formulario Vacío
    # Si la petición es POST se creará el formulario con Datos.
    datosFormulario = None
    
    if request.method == "POST":
        datosFormulario = request.POST
    
    formulario = EnsayoClinicoForm(datosFormulario)
    
    if (request.method == "POST"):
        
        ensayoclinico_creado = crear_ensayoclinico_modelo(formulario, request.user)
        
        if(ensayoclinico_creado):
            messages.success(request, 'Se ha creado el Ensayo Clinico: [ '+formulario.cleaned_data.get('nombre')+" ] correctamente.")
            return redirect('ensayosclinicos_listar')

    return render(request, 'models/ensayoclinico/crud/create_ensayoclinico.html',{'formulario':formulario})

def crear_ensayoclinico_modelo(formulario, usuario): #Metodo que interactua con la base de datos
    
    ensayoclinico_creado = False
    # Comprueba si el formulario es válido
    if formulario.is_valid():
        try:
            # Almacena el Ensayo Clinico
            ensayoclinico = formulario.save(commit=False)

            # asignar creador
            if usuario.rol == Usuario.INVESTIGADOR:
                ensayoclinico.creado_por = usuario.investigador
            else:
                # En caso de que el usuario no sea investigador, no se le permite crear el ensayo clinico
                raise Exception("Solo los Investigadores pueden crear Ensayos Clinicos.")
                # Y la excepcion se captura por el try-except
            
            # Guarda el Ensayo Clinico en la base de datos
            ensayoclinico.save()
            # Guardar las relaciones ManyToMany
            formulario.save_m2m()
            
            
            ensayoclinico_creado = True
            
        except Exception as error:
            print(error)
    return ensayoclinico_creado
#endregion

#region --- READ ---
@permission_required('examen.view_ensayoclinico', raise_exception=True)
def ensayoclinico_buscar_avanzado(request): #Busqueda Avanzada
    
    if(len(request.GET) > 0):
        formulario = EnsayoClinicoBuscarAvanzada(request.GET)
        if formulario.is_valid():
            mensaje_busqueda = 'Filtros Aplicados:\n'
            
            QsEnsayoClinico = (
                EnsayoClinico.objects
                .select_related('farmaco','creado_por')
                .prefetch_related('pacientes')
            )
            
            #Obtenemos los filtros
            texto_contiene = formulario.cleaned_data.get('texto_contiene')
            fecha_desde = formulario.cleaned_data.get('fecha_desde')
            fecha_hasta = formulario.cleaned_data.get('fecha_hasta')
            nivel_seguimiento_mayor = formulario.cleaned_data.get('nivel_seguimiento_mayor')
            pacientes = formulario.cleaned_data.get('pacientes')
            ensayos_activos = formulario.cleaned_data.get('ensayos_activos')
            
            #---Nombre Descripcion---
            if(texto_contiene!=''):
                texto_contiene = texto_contiene.strip()
                QsEnsayoClinico = QsEnsayoClinico.filter(Q(descripcion__icontains=texto_contiene)|Q(nombre__icontains=texto_contiene))
                mensaje_busqueda += '· Nombre o Descripcion contiene "'+texto_contiene+'"\n'
            else:
                mensaje_busqueda += '· Cualquier Nombre o Descripcion \n'
            
            #---Fechas---
            if (not fecha_desde is None):
                QsEnsayoClinico = QsEnsayoClinico.filter(fecha_inicio__gte=fecha_desde)
                mensaje_busqueda += '· Fecha Ensayo Clinico desde '+datetime.strftime(fecha_desde,'%d-%m-%Y')+'\n'
            else:
                mensaje_busqueda += '· Fecha Ensayo Clinico desde: Cualquier fecha \n'
            
            if (not fecha_hasta is None):
                QsEnsayoClinico = QsEnsayoClinico.filter(fecha_final__lte=fecha_hasta)
                mensaje_busqueda += '· Fecha Ensayo Clinico hasta '+datetime.strftime(fecha_hasta,'%d-%m-%Y')+'\n'
            else:
                mensaje_busqueda += '· Fecha Ensayo Clinico hasta: Cualquier fecha \n'
            
            #---Nivel de Seguimiento---
            if (not nivel_seguimiento_mayor is None):
                QsEnsayoClinico = QsEnsayoClinico.filter(nivel_seguimiento__gt=nivel_seguimiento_mayor)
                mensaje_busqueda += f'· Nivel de Seguimiento mayor a {nivel_seguimiento_mayor}\n'
            else:
                mensaje_busqueda += '· Cualquier Nivel de Seguimiento \n'
                        
            #---Pacientes---
            if pacientes and len(pacientes) > 0:
                
                QsEnsayoClinico = QsEnsayoClinico.filter(pacientes__id__in=pacientes)
                
                # Recorre los nombres y los separa con ,
                nombres_pacientes = ", ".join([p.usuario.username for p in pacientes])
                mensaje_busqueda += f'· Pacientes: {nombres_pacientes}\n'
                
            else:
                mensaje_busqueda += '· Cualquier Paciente \n'
            
            #---Ensayos Activos---
            if ensayos_activos:
                QsEnsayoClinico = QsEnsayoClinico.filter(activo=True)
                mensaje_busqueda += '· Solo Ensayos Activos \n'
            else:
                mensaje_busqueda += '· Cualquier Ensayo (Activo o Inactivo) \n'
            
            
            #Ejecutamos la querySet y enviamos los usuarios
            ensayoclinico = QsEnsayoClinico.all()
            
            return render(request, 'models/ensayoclinico/lista_ensayoclinico.html',
                        {'EnsayosClinicos_Mostrar':ensayoclinico,
                        'Mensaje_Busqueda':mensaje_busqueda}
                        )
    else:
        formulario = EnsayoClinicoBuscarAvanzada(None)
    return render(request, 'models/ensayoclinico/crud/buscar_avanzada_ensayoclinico.html',{'formulario':formulario})
#endregion

#region --- UPDATE ---
@permission_required('examen.change_ensayoclinico', raise_exception=True)
def ensayoclinico_editar(request, id_ensayoclinico): # Editar Perfil
    
    ensayoclinico = EnsayoClinico.objects.get(id = id_ensayoclinico)
    
    if ensayoclinico.creado_por.id != request.user.investigador.id:
        messages.error(request, 'Solo puedes editar tus Propios Ensayos Clinicos.')
        return redirect('ensayosclinicos_listar')
    
    # Si la petición es GET se creará el formulario Vacío
    # Si la petición es POST se creará el formulario con Datos.
    datosFormulario = None
    
    if request.method == "POST":
        datosFormulario = request.POST
    
    formulario = EnsayoClinicoForm(datosFormulario,instance=ensayoclinico)
    
    if (request.method == "POST"):
        
        ensayoclinico_creado = crear_ensayoclinico_modelo(formulario, request.user)
        
        if(ensayoclinico_creado):
            messages.success(request, 'Se ha actualizado el Ensayo Clinico: [ '+formulario.cleaned_data.get('nombre')+" ] correctamente.")
            return redirect('ensayosclinicos_listar')
    
    return render(request, 'models/ensayoclinico/crud/actualizar_ensayoclinico.html', {'formulario':formulario,'ensayoclinico':ensayoclinico})
#endregion

#region --- DELETE ---
@permission_required('examen.delete_ensayoclinico', raise_exception=True)
def ensayoclinico_eliminar(request, id_ensayoclinico): # Eliminar Perfil
    ensayoclinico = EnsayoClinico.objects.get(id = id_ensayoclinico)
    nombre = ensayoclinico.nombre
    try:
        
        if ensayoclinico.creado_por.id != request.user.investigador.id:
            messages.error(request, 'Solo puedes eliminar tus Propios Ensayos Clinicos.')
            return redirect('ensayosclinicos_listar')
        
        ensayoclinico.delete()
        messages.success(request, 'Se ha eliminado el Ensayo Clinico [ '+nombre+' ] correctamente.')
    except Exception as error:
        print(error)
    return redirect('ensayosclinicos_listar')
#endregion

# endregion
# ============================================================


# ============================================================
# region Registro
# ============================================================


def registrar_usuario(request):
    
    if request.user.is_authenticated:
        messages.info(request, 'Debe Cerrar Sesion para poder volver a Registrarse')
        return redirect('home')
    
    if request.method == 'POST':
        formulario = RegistroUsuarioForm(request.POST)
        
        if formulario.is_valid():
            
            rol = int(formulario.cleaned_data.get('rol'))
            
            user = formulario.save(commit=False)
            user.save()
            
            if(rol == Usuario.PACIENTE):
                
                # Agregar el usuario a los grupos
                grupo_usuario = Group.objects.get(name='Paciente')
                grupo_usuario.user_set.add(user)
                
                # Crear el Objeto tecnico con la fk del usuario, y añadir el campo adicional
                u_edad = formulario.cleaned_data.get('edad')
                paciente = Paciente.objects.create(usuario = user, edad=u_edad)
                paciente.save()
                
            elif(rol == Usuario.INVESTIGADOR):
                
                # Agregar el usuario a los grupos
                grupo_usuario = Group.objects.get(name='Investigador')
                grupo_usuario.user_set.add(user)
                
                # Crear el Objeto tecnico con la fk del usuario, y añadir el campo adicional
                investigador = Investigador.objects.create(usuario = user)
                investigador.save()
            
            
            # Hacer el Login Automatico
            login(request, user)
            
            # 2 Variables en la Sesion Ejemplo----------------------------------------------
            
            # Nombre Usuario
            request.session['usuario'] = user.username
            
            # Hora Login
            request.session['hora_login'] = timezone.now().strftime("%d/%m/%Y %H:%M")
            
            #-------------------------------------------------------------------------------
            
            return redirect('home')
    else:
        formulario = RegistroUsuarioForm()
        
    return render(request, 'registration/signup_usuario.html', {'formulario': formulario})


# endregion
# ============================================================


# ============================================================
# region Login
# ============================================================


class MiLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user
        
        # 2 Variables en la Sesion Ejemplo----------------------------------------------
        
        # Nombre Usuario
        self.request.session['usuario'] = user.username
        
        # Hora Login
        self.request.session['hora_login'] = timezone.now().strftime("%d/%m/%Y %H:%M")

        #-------------------------------------------------------------------------------

        return response


# endregion
# ============================================================


# ============================================================
# region Errores personalizados (400, 403, 404, 500)
# ============================================================

def mi_error_404(request,exception=None):
    return render(request,'error/404.html',None,None,404)

def mi_error_403(request,exception=None):
    return render(request,'error/403.html',None,None,403)

def mi_error_400(request,exception=None):
    return render(request,'error/400.html',None,None,400)

def mi_error_500(request,exception=None):
    return render(request,'error/500.html',None,None,500)

# endregion
# ============================================================