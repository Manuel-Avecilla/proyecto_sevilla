from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import MiLoginView

urlpatterns = [
    #---HOME---
    path('', views.home, name='home'),
    
    #---GAME PAGE---
    path('jugar/', views.jugar_ruleta, name='jugar_ruleta'),

    #---REGISTRO-LOGIN---
    path('registro/usuario', views.registrar_usuario, name='registrar_usuario'),
    path('accounts/login/', MiLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='logout'),

    #---APIs for Ruleta Sevillana (Fetch SPA compatible)---
    path('api/register', views.api_register, name='api_register'),
    path('api/login', views.api_login, name='api_login'),
    path('api/questions', views.api_questions, name='api_questions'),
    path('api/save-score', views.api_save_score, name='api_save_score'),
    path('api/ranking', views.api_ranking, name='api_ranking'),
]