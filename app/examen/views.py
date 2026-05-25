import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Usuario, Pregunta, Partida
from .forms import RegistroUsuarioForm

# --- HOME ---
def home(request):
    top_players = Usuario.objects.order_by('-total_score', 'username')[:20]
    return render(request, 'pages/home.html', {'ranking': top_players})

# --- GAME VIEW ---
def jugar_ruleta(request):
    return render(request, 'ruleta/jugar.html')

# --- REGISTRATION (DJANGO NATIVE) ---
def registrar_usuario(request):
    if request.user.is_authenticated:
        messages.info(request, 'Debe Cerrar Sesion para poder volver a Registrarse')
        return redirect('home')
    
    if request.method == 'POST':
        formulario = RegistroUsuarioForm(request.POST)
        if formulario.is_valid():
            user = formulario.save()
            login(request, user)
            request.session['usuario'] = user.username
            request.session['hora_login'] = timezone.now().strftime("%d/%m/%Y %H:%M")
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('home')
    else:
        formulario = RegistroUsuarioForm()
        
    return render(request, 'registration/signup_usuario.html', {'formulario': formulario})

# --- LOGIN (DJANGO NATIVE) ---
class MiLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        self.request.session['usuario'] = user.username
        self.request.session['hora_login'] = timezone.now().strftime("%d/%m/%Y %H:%M")
        return response

# ============================================================
# API ENDPOINTS (FOR FRONTEND FETCHING)
# ============================================================

@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = str(data.get('username', '')).strip()
        password = str(data.get('password', ''))
        
        if len(username) < 3 or len(username) > 40:
            return JsonResponse({'error': 'El usuario debe tener entre 3 y 40 caracteres.'}, status=400)
        
        if len(password) < 4:
            return JsonResponse({'error': 'La contraseña debe tener mínimo 4 caracteres.'}, status=400)
        
        if Usuario.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Ese usuario ya existe.'}, status=409)
            
        Usuario.objects.create_user(username=username, password=password)
        return JsonResponse({'ok': True, 'message': 'Usuario registrado correctamente.'})
    except Exception as e:
        return JsonResponse({'error': 'Error al registrar usuario.'}, status=500)

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
        
    try:
        data = json.loads(request.body)
        username = str(data.get('username', '')).strip()
        password = str(data.get('password', ''))
        
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Usuario o contraseña incorrectos.'}, status=401)
            
        login(request, user)
        request.session['usuario'] = user.username
        request.session['hora_login'] = timezone.now().strftime("%d/%m/%Y %H:%M")
        
        return JsonResponse({
            'ok': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'total_score': user.total_score
            }
        })
    except Exception as e:
        return JsonResponse({'error': 'Error al iniciar sesión.'}, status=500)

@csrf_exempt
def api_questions(request):
    if request.method == 'GET':
        try:
            questions = Pregunta.objects.order_by('?')
            questions_list = [
                {
                    'id': q.id,
                    'category': q.category,
                    'phrase': q.phrase,
                    'clue': q.clue
                }
                for q in questions
            ]
            return JsonResponse(questions_list, safe=False)
        except Exception as e:
            return JsonResponse({'error': 'Error al cargar preguntas.'}, status=500)
            
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            category = str(data.get('category', '')).strip()
            phrase = str(data.get('phrase', '')).strip().upper()
            clue = str(data.get('clue', '')).strip()
            
            if not category or not phrase or not clue:
                return JsonResponse({'error': 'Faltan datos de la pregunta.'}, status=400)
                
            if Pregunta.objects.filter(phrase=phrase).exists():
                return JsonResponse({'error': 'Esa frase ya existe.'}, status=409)
                
            Pregunta.objects.create(category=category, phrase=phrase, clue=clue)
            return JsonResponse({'ok': True, 'message': 'Pregunta guardada en SQLite.'})
        except Exception as e:
            return JsonResponse({'error': 'Error al guardar pregunta.'}, status=500)
            
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def api_save_score(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
        
    try:
        data = json.loads(request.body)
        user_id = data.get('userId')
        score = data.get('score')
        
        if user_id is None or score is None:
            return JsonResponse({'error': 'Datos de puntuación no válidos.'}, status=400)
            
        try:
            user_id = int(user_id)
            score = int(score)
        except ValueError:
            return JsonResponse({'error': 'Datos de puntuación no válidos.'}, status=400)
            
        with transaction.atomic():
            user = Usuario.objects.select_for_update().get(id=user_id)
            Partida.objects.create(usuario=user, score=score)
            user.total_score += score
            user.save()
            
        return JsonResponse({'ok': True, 'message': 'Puntuación guardada.'})
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Error al guardar puntuación.'}, status=500)

@csrf_exempt
def api_ranking(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
        
    try:
        users = Usuario.objects.order_by('-total_score', 'username')[:20]
        ranking_list = [
            {
                'username': u.username,
                'total_score': u.total_score
            }
            for u in users
        ]
        return JsonResponse(ranking_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Error al cargar ranking.'}, status=500)

# --- CUSTOM ERROR HANDLERS ---
def mi_error_404(request, exception=None):
    return render(request, 'error/404.html', status=404)

def mi_error_403(request, exception=None):
    return render(request, 'error/403.html', status=403)

def mi_error_400(request, exception=None):
    return render(request, 'error/400.html', status=400)

def mi_error_500(request, exception=None):
    return render(request, 'error/500.html', status=500)