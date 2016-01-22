# -*- encoding: utf-8 -*-
from django.shortcuts import *
from django.contrib.auth.forms import *
from django.contrib import auth
from Core.forms import *
from Core.views import *
import json
from django.conf import settings
import logging

#Instancia del log
logger = logging.getLogger(__name__)


def inicio(request):

    login_form = formulario_login()
    registro_form = formulario_registro()
    if request.user.is_authenticated():
        try:
            perfil = Perfil.objects.get(user=request.user)
            perfilRolClub = PerfilRolClub.objects.filter(perfil=perfil, rol__id=settings.ROL_ADMINISTRADOR)
            if perfilRolClub.count() > 0:
                return HttpResponseRedirect("/administrador/"+str(request.user.id))
            else:
                return HttpResponseRedirect("/usuario/"+str(request.user.id))
        except Exception:
            logger.debug("inicio/views - Método inicio")

    else:
        datos = {
            'login_form' : login_form,
            'registro_form' : registro_form
        }
    return render_to_response('inicio/index.html', datos, context_instance=RequestContext(request))

def login(request):
    error = ""
    id = ""
    rol_id = ""
    if request.method == "POST":
        usernameEmail = request.POST.get('usuario')
        password = request.POST.get('password')
        if usernameEmail and password:
            #Comprobamos si tiene arroba, si no, es username
            if '@' in usernameEmail:
                username = User.objects.values_list('username', flat=True).get(email=usernameEmail)
            else:
                username = usernameEmail
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                id = user.id
                auth.login(request, user)
                try:
                    perfil = Perfil.objects.get(user = user)
                    num = PerfilRolClub.objects.filter(perfil_id = perfil.id, rol_id = settings.ROL_ADMINISTRADOR).count()
                    rol_id = settings.ROL_JUGADOR #Rol de usuario
                    if num > 0:
                        rol_id = settings.ROL_ADMINISTRADOR #Rol administrador
                except Perfil.DoesNotExist:
                    error = "Usuario o contraseña incorrecto."
                except Exception:
                    logger.debug("inicio/views - Método login")
            else:
                error = "Usuario o contraseña incorrecto."
        else:
            error = "Rellene correctamente todos los campos"
    data = {'error' : error, 'id' : id, 'rol_id' : rol_id}
    return HttpResponse(json.dumps(data))

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect("/")

def registro(request):
    error = ""
    perfil = ""
    id = ""
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        username = request.POST.get('username')
        if nombre and apellidos and email and password1 and password2 and username:
            if password1 != password2:
                error = "Las contraseñas no coinciden"
            else:
                try:
                    if(User.objects.filter(username=username).count() == 0 or User.objects.filter(email=email).count() == 0):
                        user = User.objects.create_user(username, email, password1)
                        user.first_name = nombre
                        user.last_name = apellidos
                        perfil = Perfil.objects.create(user = user)
                        if perfil and user:
                            user.save()
                            perfil.save()
                            id = user.id
                            acceso = authenticate(username=user.username, password=user.password)
                            if acceso is not None:
                                auth.login(request, acceso)

                    else:
                        error = "El email o el nombre de usuario seleccionado no está disponible"
                except Exception:
                    error = "Disculpe las molestias, inténtelo de nuevo más tarde"
                    logger.debug("inicio/views - Método registro")
        else:
            error = "Debe rellenar todos los campos"
    data = {'id':id, 'error':error}
    return HttpResponse(json.dumps(data))
