import json
import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Usuario, Pregunta, Partida, PartidaMultijugador, JugadorPartida
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
# API ENDPOINTS (FOR SINGLEPLAYER MODE)
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


# ============================================================
# API ENDPOINTS (FOR MULTIPLAYER MODE)
# ============================================================

def generate_lobby_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = "".join(random.choice(chars) for _ in range(6))
        if not PartidaMultijugador.objects.filter(codigo=code).exists():
            return code

def pass_turn(lobby):
    jugadores = list(lobby.jugadores.order_by('orden'))
    if not jugadores:
        return
    
    current_user = lobby.jugador_actual_turno
    current_index = 0
    for i, j in enumerate(jugadores):
        if j.usuario == current_user:
            current_index = i
            break
            
    next_index = (current_index + 1) % len(jugadores)
    lobby.jugador_actual_turno = jugadores[next_index].usuario
    lobby.valor_ruleta_actual = None
    lobby.fase_turno = 'GIRAR'
    lobby.save()

@csrf_exempt
def api_mp_create(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión para crear una partida.'}, status=401)
    
    try:
        data = {}
        if request.body:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                pass
        
        num_paneles = int(data.get('num_paneles', 5))
        if num_paneles < 1 or num_paneles > 20:
            num_paneles = 5
            
        code = generate_lobby_code()
        questions = list(Pregunta.objects.order_by('?')[:num_paneles])
        if not questions:
            return JsonResponse({'error': 'No hay preguntas disponibles en la base de datos.'}, status=400)
            
        preguntas_ids = ",".join(str(q.id) for q in questions)
        
        with transaction.atomic():
            lobby = PartidaMultijugador.objects.create(
                codigo=code,
                creador=request.user,
                estado='ESPERANDO',
                preguntas_ids=preguntas_ids,
                panel_actual_index=0,
                letras_usadas='',
                jugador_actual_turno=request.user,
                fase_turno='GIRAR'
            )
            JugadorPartida.objects.create(
                partida=lobby,
                usuario=request.user,
                puntos_partida=0,
                orden=0
            )
            
        return JsonResponse({'ok': True, 'codigo': code})
    except Exception as e:
        return JsonResponse({'error': f'Error al crear la partida: {str(e)}'}, status=500)

@csrf_exempt
def api_mp_join(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión para unirse a una partida.'}, status=401)
        
    try:
        data = json.loads(request.body)
        codigo = str(data.get('codigo', '')).strip().upper()
        
        lobby = PartidaMultijugador.objects.filter(codigo=codigo).first()
        if not lobby:
            return JsonResponse({'error': 'La partida no existe.'}, status=404)
            
        if lobby.estado != 'ESPERANDO':
            return JsonResponse({'error': 'La partida ya ha comenzado o ha finalizado.'}, status=400)
            
        # Comprobar si ya está en la sala
        jugador = lobby.jugadores.filter(usuario=request.user).first()
        if not jugador:
            player_count = lobby.jugadores.count()
            if player_count >= 8:
                return JsonResponse({'error': 'La sala está llena (máximo 8 jugadores).'}, status=400)
                
            JugadorPartida.objects.create(
                partida=lobby,
                usuario=request.user,
                puntos_partida=0,
                orden=player_count
            )
            
        return JsonResponse({'ok': True, 'codigo': codigo})
    except Exception as e:
        return JsonResponse({'error': f'Error al unirse: {str(e)}'}, status=500)

@csrf_exempt
def api_mp_start(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión.'}, status=401)
        
    try:
        data = json.loads(request.body)
        codigo = str(data.get('codigo', '')).strip().upper()
        
        lobby = PartidaMultijugador.objects.filter(codigo=codigo).first()
        if not lobby:
            return JsonResponse({'error': 'La partida no existe.'}, status=404)
            
        if lobby.creador != request.user:
            return JsonResponse({'error': 'Solo el creador puede iniciar la partida.'}, status=403)
            
        if lobby.estado != 'ESPERANDO':
            return JsonResponse({'error': 'La partida ya ha comenzado.'}, status=400)
            
        # Validar mínimo de 2 jugadores para empezar
        player_count = lobby.jugadores.count()
        if player_count < 2:
            return JsonResponse({'error': 'Se necesitan al menos 2 jugadores para iniciar la partida.'}, status=400)
            
        # Poner estado JUGANDO y elegir el primer turno
        lobby.estado = 'JUGANDO'
        first_player = lobby.jugadores.order_by('orden').first()
        lobby.jugador_actual_turno = first_player.usuario if first_player else request.user
        lobby.fase_turno = 'GIRAR'
        lobby.save()
        
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': f'Error al iniciar partida: {str(e)}'}, status=500)

@csrf_exempt
def api_mp_status(request, codigo):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión.'}, status=401)
        
    try:
        lobby = PartidaMultijugador.objects.filter(codigo=codigo.upper()).first()
        if not lobby:
            return JsonResponse({'error': 'Partida no encontrada.'}, status=404)
            
        jugadores = lobby.jugadores.select_related('usuario').order_by('orden')
        players_list = [
            {
                'id': jp.usuario.id,
                'username': jp.usuario.username,
                'score': jp.puntos_partida,
                'is_turn': (jp.usuario == lobby.jugador_actual_turno)
            }
            for jp in jugadores
        ]
        
        # Obtener las preguntas ordenadas
        id_list = [int(x) for x in lobby.preguntas_ids.split(',') if x]
        preguntas = Pregunta.objects.filter(id__in=id_list)
        preguntas_dict = {p.id: p for p in preguntas}
        ordered_preguntas = [preguntas_dict[pid] for pid in id_list if pid in preguntas_dict]
        
        panels_json = [
            {
                'category': q.category,
                'phrase': q.phrase,
                'clue': q.clue
            }
            for q in ordered_preguntas
        ]
        
        letras_list = [x for x in lobby.letras_usadas.split(',') if x]
        
        val_ruleta = lobby.valor_ruleta_actual
        try:
            val_ruleta = int(val_ruleta)
        except (ValueError, TypeError):
            pass
            
        return JsonResponse({
            'ok': True,
            'codigo': lobby.codigo,
            'estado': lobby.estado,
            'creador_id': lobby.creador.id,
            'jugador_actual_turno_id': lobby.jugador_actual_turno.id if lobby.jugador_actual_turno else None,
            'jugador_actual_turno_username': lobby.jugador_actual_turno.username if lobby.jugador_actual_turno else '',
            'panel_actual_index': lobby.panel_actual_index,
            'letras_usadas': letras_list,
            'valor_ruleta_actual': val_ruleta,
            'fase_turno': lobby.fase_turno,
            'players': players_list,
            'panels': panels_json,
            'ultimo_mensaje_suceso': lobby.ultimo_mensaje_suceso
        })
    except Exception as e:
        return JsonResponse({'error': f'Error al obtener estado: {str(e)}'}, status=500)

@csrf_exempt
def api_mp_spin(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión.'}, status=401)
        
    try:
        data = json.loads(request.body)
        codigo = str(data.get('codigo', '')).strip().upper()
        
        lobby = PartidaMultijugador.objects.filter(codigo=codigo).first()
        if not lobby:
            return JsonResponse({'error': 'La partida no existe.'}, status=404)
            
        if lobby.jugador_actual_turno != request.user:
            return JsonResponse({'error': 'No es tu turno.'}, status=403)
            
        if lobby.fase_turno != 'GIRAR':
            return JsonResponse({'error': 'Ya has girado en este turno.'}, status=400)
            
        wheel_values = [100, 150, 200, 250, 300, 400, 500, "PIERDE TURNO", "QUIEBRA"]
        value = random.choice(wheel_values)
        lobby.valor_ruleta_actual = str(value)
        lobby.ultimo_mensaje_suceso = f"SPIN:{request.user.username}:{value}"
        
        if value == "PIERDE TURNO":
            pass_turn(lobby)
        elif value == "QUIEBRA":
            jp = lobby.jugadores.filter(usuario=request.user).first()
            if jp:
                jp.puntos_partida = 0
                jp.save()
            pass_turn(lobby)
        else:
            lobby.fase_turno = 'ADIVINAR'
            lobby.save()
            
        return JsonResponse({'ok': True, 'value': value})
    except Exception as e:
        return JsonResponse({'error': f'Error al girar: {str(e)}'}, status=500)

@csrf_exempt
def api_mp_guess(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión.'}, status=401)
        
    try:
        data = json.loads(request.body)
        codigo = str(data.get('codigo', '')).strip().upper()
        letter = str(data.get('letter', '')).strip().upper()
        
        lobby = PartidaMultijugador.objects.filter(codigo=codigo).first()
        if not lobby:
            return JsonResponse({'error': 'La partida no existe.'}, status=404)
            
        if lobby.jugador_actual_turno != request.user:
            return JsonResponse({'error': 'No es tu turno.'}, status=403)
            
        if lobby.fase_turno != 'ADIVINAR':
            return JsonResponse({'error': 'Primero debes girar la ruleta.'}, status=400)
            
        # Validaciones de letra
        if not letter or len(letter) != 1:
            return JsonResponse({'error': 'Letra no válida.'}, status=400)
            
        vowels = ["A","E","I","O","U"]
        if letter in vowels:
            return JsonResponse({'error': 'Las vocales se compran.'}, status=400)
            
        letters_used = [x for x in lobby.letras_usadas.split(',') if x]
        if letter in letters_used:
            return JsonResponse({'error': 'Esta letra ya se ha usado.'}, status=400)
            
        # Añadir a letras usadas
        letters_used.append(letter)
        lobby.letras_usadas = ",".join(letters_used)
        
        # Buscar pregunta
        id_list = [int(x) for x in lobby.preguntas_ids.split(',') if x]
        pregunta_id = id_list[lobby.panel_actual_index]
        pregunta = Pregunta.objects.get(id=pregunta_id)
        
        # Contar apariciones
        phrase_normalized = StringNormalize(pregunta.phrase)
        occurrences = phrase_normalized.count(letter)
        
        jp = lobby.jugadores.filter(usuario=request.user).first()
        
        if occurrences > 0:
            gained = occurrences * int(lobby.valor_ruleta_actual)
            if jp:
                jp.puntos_partida += gained
                jp.save()
            lobby.ultimo_mensaje_suceso = f"HIT:{request.user.username}:{letter}:{occurrences}"
            lobby.valor_ruleta_actual = None
            lobby.fase_turno = 'GIRAR' # Sigue jugando, vuelve a girar o resolver
            lobby.save()
        else:
            penalty = max(50, int(lobby.valor_ruleta_actual) // 2)
            if jp:
                jp.puntos_partida = max(0, jp.puntos_partida - penalty)
                jp.save()
            lobby.ultimo_mensaje_suceso = f"MISS:{request.user.username}:{letter}"
            pass_turn(lobby)
            
        # Comprobar si el panel se ha completado
        phrase_letters = set(ch for ch in phrase_normalized if ch.isalpha() and ch not in vowels)
        phrase_vowels = set(ch for ch in phrase_normalized if ch.isalpha() and ch in vowels)
        all_required_letters = phrase_letters.union(phrase_vowels)
        
        completed = all_required_letters.issubset(set(letters_used))
        if completed:
            if jp:
                jp.puntos_partida += 300
                jp.save()
            # El turno sigue siendo del jugador actual para que haga "Siguiente Panel"
            lobby.fase_turno = 'GIRAR'
            lobby.save()
            
        return JsonResponse({'ok': True, 'occurrences': occurrences, 'completed': completed})
    except Exception as e:
        return JsonResponse({'error': f'Error al adivinar: {str(e)}'}, status=500)

@csrf_exempt
def api_mp_buy_vowel(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión.'}, status=401)
        
    try:
        data = json.loads(request.body)
        codigo = str(data.get('codigo', '')).strip().upper()
        letter = str(data.get('letter', '')).strip().upper()
        
        lobby = PartidaMultijugador.objects.filter(codigo=codigo).first()
        if not lobby:
            return JsonResponse({'error': 'La partida no existe.'}, status=404)
            
        if lobby.jugador_actual_turno != request.user:
            return JsonResponse({'error': 'No es tu turno.'}, status=403)
            
        vowels = ["A","E","I","O","U"]
        if letter not in vowels:
            return JsonResponse({'error': 'Debes elegir una vocal para comprar.'}, status=400)
            
        letters_used = [x for x in lobby.letras_usadas.split(',') if x]
        if letter in letters_used:
            return JsonResponse({'error': 'Esta vocal ya se ha usado.'}, status=400)
            
        jp = lobby.jugadores.filter(usuario=request.user).first()
        if not jp or jp.puntos_partida < 50:
            return JsonResponse({'error': 'No tienes suficientes puntos (mínimo 50).'}, status=400)
            
        # Descontar puntos
        jp.puntos_partida -= 50
        jp.save()
        
        # Registrar letra
        letters_used.append(letter)
        lobby.letras_usadas = ",".join(letters_used)
        
        # Buscar pregunta
        id_list = [int(x) for x in lobby.preguntas_ids.split(',') if x]
        pregunta_id = id_list[lobby.panel_actual_index]
        pregunta = Pregunta.objects.get(id=pregunta_id)
        
        phrase_normalized = StringNormalize(pregunta.phrase)
        occurrences = phrase_normalized.count(letter)
        
        if occurrences > 0:
            lobby.ultimo_mensaje_suceso = f"HIT_VOWEL:{request.user.username}:{letter}:{occurrences}"
            # Mantiene el turno
            lobby.fase_turno = 'GIRAR'
            lobby.save()
        else:
            lobby.ultimo_mensaje_suceso = f"MISS_VOWEL:{request.user.username}:{letter}"
            pass_turn(lobby)
            
        # Comprobar si el panel se ha completado
        phrase_letters = set(ch for ch in phrase_normalized if ch.isalpha() and ch not in vowels)
        phrase_vowels = set(ch for ch in phrase_normalized if ch.isalpha() and ch in vowels)
        all_required_letters = phrase_letters.union(phrase_vowels)
        
        completed = all_required_letters.issubset(set(letters_used))
        if completed:
            jp.puntos_partida += 300
            jp.save()
            lobby.fase_turno = 'GIRAR'
            lobby.save()
            
        return JsonResponse({'ok': True, 'occurrences': occurrences, 'completed': completed})
    except Exception as e:
        return JsonResponse({'error': f'Error al comprar vocal: {str(e)}'}, status=500)

@csrf_exempt
def api_mp_solve(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión.'}, status=401)
        
    try:
        data = json.loads(request.body)
        codigo = str(data.get('codigo', '')).strip().upper()
        phrase_attempt = StringNormalize(str(data.get('phrase', '')))
        
        lobby = PartidaMultijugador.objects.filter(codigo=codigo).first()
        if not lobby:
            return JsonResponse({'error': 'La partida no existe.'}, status=404)
            
        if lobby.jugador_actual_turno != request.user:
            return JsonResponse({'error': 'No es tu turno.'}, status=403)
            
        # Buscar pregunta
        id_list = [int(x) for x in lobby.preguntas_ids.split(',') if x]
        pregunta_id = id_list[lobby.panel_actual_index]
        pregunta = Pregunta.objects.get(id=pregunta_id)
        
        correct_phrase = StringNormalize(pregunta.phrase)
        jp = lobby.jugadores.filter(usuario=request.user).first()
        
        if phrase_attempt == correct_phrase:
            if jp:
                jp.puntos_partida += 500
                jp.save()
            # Revelar todas las letras
            letters_used = list(set(ch for ch in correct_phrase if ch.isalpha()))
            lobby.letras_usadas = ",".join(letters_used)
            lobby.ultimo_mensaje_suceso = f"SOLVE:{request.user.username}"
            lobby.fase_turno = 'GIRAR'
            lobby.save()
            return JsonResponse({'ok': True, 'correct': True})
        else:
            if jp:
                jp.puntos_partida = max(0, jp.puntos_partida - 200)
                jp.save()
            lobby.ultimo_mensaje_suceso = f"FAIL_SOLVE:{request.user.username}"
            pass_turn(lobby)
            return JsonResponse({'ok': True, 'correct': False})
    except Exception as e:
        return JsonResponse({'error': f'Error al resolver: {str(e)}'}, status=500)

@csrf_exempt
def api_mp_next_panel(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión.'}, status=401)
        
    try:
        data = json.loads(request.body)
        codigo = str(data.get('codigo', '')).strip().upper()
        
        lobby = PartidaMultijugador.objects.filter(codigo=codigo).first()
        if not lobby:
            return JsonResponse({'error': 'La partida no existe.'}, status=404)
            
        if lobby.jugador_actual_turno != request.user:
            return JsonResponse({'error': 'No es tu turno para avanzar el panel.'}, status=403)
            
        id_list = [int(x) for x in lobby.preguntas_ids.split(',') if x]
        
        # Incrementar índice
        lobby.panel_actual_index += 1
        lobby.letras_usadas = ''
        lobby.valor_ruleta_actual = None
        lobby.fase_turno = 'GIRAR'
        
        if lobby.panel_actual_index >= len(id_list):
            lobby.estado = 'TERMINADA'
            # Guardar puntuaciones en la tabla global Matches y Users total score
            jugadores = lobby.jugadores.all()
            with transaction.atomic():
                for jp in jugadores:
                    Partida.objects.create(usuario=jp.usuario, score=jp.puntos_partida)
                    jp.usuario.total_score += jp.puntos_partida
                    jp.usuario.save()
                    
        lobby.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': f'Error al avanzar: {str(e)}'}, status=500)

@csrf_exempt
def api_mp_leave(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debe iniciar sesión.'}, status=401)
        
    try:
        data = json.loads(request.body)
        codigo = str(data.get('codigo', '')).strip().upper()
        
        lobby = PartidaMultijugador.objects.filter(codigo=codigo).first()
        if not lobby:
            return JsonResponse({'error': 'La partida no existe.'}, status=404)
            
        jp = lobby.jugadores.filter(usuario=request.user).first()
        if jp:
            with transaction.atomic():
                # Borrar al jugador
                jp.delete()
                
                # Re-ordenar el resto de jugadores
                rest = lobby.jugadores.order_by('orden')
                for idx, r in enumerate(rest):
                    r.orden = idx
                    r.save()
                
                # Si era su turno, pasar el turno
                if lobby.jugador_actual_turno == request.user:
                    pass_turn(lobby)
                
                # Comprobar cuántos quedan
                remaining_count = lobby.jugadores.count()
                if remaining_count == 0:
                    lobby.estado = 'TERMINADA'
                    lobby.save()
                elif remaining_count == 1:
                    if lobby.estado == 'JUGANDO':
                        # Queda solo 1 jugador en una partida activa. Finalizar sin guardar puntos
                        lobby.estado = 'TERMINADA'
                        last_player = lobby.jugadores.first()
                        lobby.jugador_actual_turno = last_player.usuario if last_player else None
                        lobby.save()
                    else:
                        # Si estaba en ESPERANDO, la sala sigue abierta
                        last_player = lobby.jugadores.first()
                        lobby.jugador_actual_turno = last_player.usuario if last_player else None
                        lobby.save()
                    
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': f'Error al abandonar la sala: {str(e)}'}, status=500)


def StringNormalize(text):
    import unicodedata
    return "".join(
        c for c in unicodedata.normalize('NFD', str(text).upper().strip())
        if unicodedata.category(c) != 'Mn' or c == 'Ñ'
    )


# --- CUSTOM ERROR HANDLERS ---
def mi_error_404(request, exception=None):
    return render(request, 'error/404.html', status=404)

def mi_error_403(request, exception=None):
    return render(request, 'error/403.html', status=403)

def mi_error_400(request, exception=None):
    return render(request, 'error/400.html', status=400)

def mi_error_500(request, exception=None):
    return render(request, 'error/500.html', status=500)