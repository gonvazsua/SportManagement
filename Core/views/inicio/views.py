# -*- encoding: utf-8 -*-
from django.shortcuts import *
from django.contrib.auth.forms import *
from django.contrib import auth
from Core.forms import *
from Core.views import *
import json
from django.conf import settings
import logging
from random import choice
from Core.utils import *
from Core.plantillas_mail import *
from django.db.models import Q

#Instancia del log
logger = logging.getLogger(__name__)


def inicio(request):

    login_form = formulario_login()
    registro_form = formulario_registro()
    '''
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
    '''

    #Modificacion para que no se inice sesion automaticamente
    if request.user.is_authenticated():
        auth.logout(request)

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
            try:
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

                         #Se desactiva la demo por si no se hubiera limpiado la sesión
                        if "es_demo" in request.session:
                            request.session["es_demo"] = False

                    except Perfil.DoesNotExist:
                        error = "Usuario o contraseña incorrecto."
                    except Exception:
                        logger.debug("inicio/views - Método login")
                else:
                    error = "Usuario o contraseña incorrecto."
            except User.DoesNotExist:
                error = "El usuario no está dado de alta"
        else:
            error = "Rellene correctamente todos los campos"
    data = {'error' : error, 'id' : id, 'rol_id' : rol_id}
    return HttpResponse(json.dumps(data))

def logout(request):

    #Limpiamos la sesion
    for key in request.session.keys():
        del request.session[key]

	auth.logout(request)
	return HttpResponseRedirect("/")

def registro(request):
    error = ""
    perfil = ""
    id = ""
    titulo = "Registro en SportClick"
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

                #Cambiar a minusculas algunos datos
                username = username.lower()
                email = email.lower()

                try:
                    userOld = User.objects.get(Q(username=username) | Q(email=email))
                    if userOld.is_active:
                        if userOld.username == username:
                            error = "El nombre de usuario ya está en uso"
                        elif userOld.email == email:
                            error = "El email ya está en uso"
                    else:
                        if userOld.username == username and userOld.email == email:
                            userOld.is_active = True
                            userOld.save()
                            id = userOld.id
                        else:
                            if userOld.username == username:
                                error = "El nombre de usuario ya está en uso"
                            elif userOld.email == email:
                                error = "El email ya está en uso"

                except User.DoesNotExist:

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

                        #Notificar con email
                        texto = plantilla_email_registro(user.first_name, user.username, password1)
                        if enviar_email(titulo, settings.EMAIL_HOST_USER, user.email, texto):
                            error = ""
                        else:
                            error = "Te has registrado correctamente, pero no hemos podido enviarte el email"

                except Exception:
                    error = "Disculpe las molestias, inténtelo de nuevo más tarde"
                    logger.debug("inicio/views - Método registro")
        else:
            error = "Debe rellenar todos los campos"
    data = {'id':id, 'error':error}
    return HttpResponse(json.dumps(data))

def recuperar_pass(request):
    error = ""
    id = ""
    cambio_contras = "Cambio de contraseña"

    if request.method == "POST":
        usernameEmail = request.POST.get('email_pass')
        if usernameEmail:
            try:
                #Comprobamos si el usuario existe

                #Comprobamos si tiene arroba, si no, es username
                if '@' in usernameEmail:
                    user = User.objects.get(email=usernameEmail)
                else:
                    user = User.objects.get(username=usernameEmail)

                if user:
                    clave_nueva = generar_clave_aleatoria()
                    clave_antigua = user.password
                    if clave_nueva:
                        user.set_password(clave_nueva)
                        user.save()
                        texto = plantilla_email_pass(user.username, clave_nueva)
                        if enviar_email(cambio_contras, settings.EMAIL_HOST_USER, user.email, texto):
                            error = ""

            except User.DoesNotExist, e:
                error = "El usuario no existe"

            except Exception, e:
                error = "Disculpe las molestias, inténtelo de nuevo más tarde"
                logger.debug("inicio/views - Método recuperar_pass: " + e.message)
        else:
            error = "Rellene correctamente todos los campos"

    data = {'error' : error}
    return HttpResponse(json.dumps(data))


def demo(request):

    try:
        #Obtener usuario de demo
        user = authenticate(username=settings.USERNAME_DEMO, password=settings.PASS_DEMO)
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

        #Metemos en sesion que es una demo
        if not "es_demo" in request.session:
            request.session["es_demo"] = True

        return HttpResponseRedirect("/administrador/" + str(user.id))

    except Exception, e:
        logger.debug("inicio/views - Método demo: " + e.message)

    return HttpResponseRedirect("/administrador/" + str(user.id))


######################################################
#Metodo que genera claves aleatorias para los usuarios
######################################################
def generar_clave_aleatoria():

    longitud = 10
    valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    clave = ""
    clave = clave.join([choice(valores) for i in range(longitud)])

    return clave