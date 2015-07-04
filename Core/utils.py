from Core.models import *
from django.shortcuts import *

def comprueba_usuario_administrador(id_usuario):
    user = ""
    perfil = ""
    try:
        user = User.objects.get(id = id_usuario)
        perfil = Perfil.objects.get(user = user)
        if not PerfilRolClub.objects.filter(perfil = perfil, rol_id = 1).exists():
            return HttpResponse('/inicio')
        if not user.is_authenticated():
            return HttpResponse('/inicio')
    except User.DoesNotExist:
        return HttpResponse('/inicio')
    return perfil
