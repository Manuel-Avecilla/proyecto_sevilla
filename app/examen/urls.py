# ============================================================
# region Importaciones
# ============================================================

from django.urls import path
from . import views
from .views import MiLoginView

# endregion
# ============================================================


urlpatterns = [
    
    #---HOME---
    path('',views.home, name='home'),
    
    
    #---REGISTRO-LOGIN---
    
    # Registro
    path('registro/usuario',views.registrar_usuario,name='registrar_usuario'),
    
    # Login
    path('accounts/login/', MiLoginView.as_view(), name='login'),


    #---Usuario---
    #---------Detalles-Lista---------
    path('usuario/listar', views.usuarios_listar, name='usuarios_listar'),
    path('usuario/<int:id_usuario>', views.dame_usuario, name='dame_usuario'),
    
    #---Ensayo-Clinico---
    #---------Detalles-Lista---------
    path('ensayoclinico/listar', views.ensayosclinicos_listar, name='ensayosclinicos_listar'),
    path('ensayoclinico/<int:id_ensayoclinico>', views.dame_ensayoclinico, name='dame_ensayoclinico'),
    #--------------CRUD--------------
    path('ensayoclinico/crear/',views.ensayoclinico_create, name='ensayoclinico_create'),
    path('ensayoclinico/buscar/avanzado/',views.ensayoclinico_buscar_avanzado, name='ensayoclinico_buscar_avanzado'),
    path('ensayoclinico/editar/<int:id_ensayoclinico>', views.ensayoclinico_editar, name="ensayoclinico_editar"),
    path('ensayoclinico/eliminar/<int:id_ensayoclinico>', views.ensayoclinico_eliminar, name="ensayoclinico_eliminar"),
    
    
    
    
    #---CRUD---
]