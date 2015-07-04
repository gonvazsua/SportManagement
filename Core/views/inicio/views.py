# -*- encoding: utf-8 -*-
from django.shortcuts import *
from django.contrib.auth.forms import *
from django.contrib import auth
from Core.forms import *
from Core.views import *
import json

def inicio(request):
    login_form = formulario_login()
    registro_form = formulario_registro()
    if request.user.is_authenticated():
        perfil = Perfil.objects.get(user=request.user)
        perfilRolClub = PerfilRolClub.objects.filter(perfil=perfil, rol__id=1)
        if perfilRolClub.count() > 0:
            return perfil_administrador(request, id_usuario = request.user.id)
        #else:
        #    return perfil_usuario(request, id_usuario = request.user.id)

    else:
        datos = {
            'login_form' : login_form,
            'registro_form' : registro_form
        }
    return render_to_response('inicio/index.html', datos, context_instance=RequestContext(request))

def login(request):
    error = ""
    id = ""
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            id = user.id
            auth.login(request, user)
            try:
                perfil = Perfil.objects.get(user = user)
                num = PerfilRolClub.objects.filter(perfil_id = perfil.id, rol_id = 1).count()
                rol_id = 0 #Rol de usuario
                if num > 0:
                    rol_id = 1 #Rol administrador
            except Perfil.DoesNotExist:
                error = "Usuario o contraseña incorrecto."
        else:
            error = "Usuario o contraseña incorrecto."
    data = {'error' : error, 'id' : id, 'rol_id' : rol_id}
    return HttpResponse(json.dumps(data))

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect("/")

def registro(request):
    error = ""
    perfil = ""
    if request.method == "POST":
        nombre = request.POST['nombre']
        apellidos = request.POST['apellidos']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        username = request.POST['username']
        if password1 != password2:
            error = "Las contraseñas no coinciden"
        elif nombre == "" or apellidos == "" or password1 == "" or password2 == "":
            error = "Debe rellenar todos los campos"
        else:
            user = User.objects.create_user(nombre, apellidos, password1)
            user.save()
            rol_administrador = Rol.objects.get(id=1)
            perfil = Perfil.objects.create(user = user, rol = rol_administrador)
            perfil.save()
    data = {'id':perfil.id, 'error':error}
    return HttpResponse(json.dumps(data))

