# -*- encoding: utf-8 -*-
from Core.models import *
from django.shortcuts import *
from django.conf import settings

import logging

#Instancia del log
logger = logging.getLogger(__name__)

def comprueba_usuario_administrador(id_usuario):
    user = ""
    perfil = ""
    try:
        user = User.objects.get(id = id_usuario)
        perfil = Perfil.objects.get(user = user)
        if not PerfilRolClub.objects.filter(perfil = perfil, rol_id = settings.ROL_ADMINISTRADOR).exists():
            return None
        if not user.is_authenticated():
            return None
    except User.DoesNotExist:
        logger.debug("util/utils - Método comprueba_usuario_administrador: No existe usuario " + str(id_usuario))
        return None
    except Exception, e:
        logger.debug("util/utils - Método comprueba_usuario_administrador: id_usuario " + str(id_usuario))
        return None
    return perfil


def comprueba_usuario_logado_no_administrador(id_usuario):
    user = ""
    perfil = ""
    try:
        user = User.objects.get(id = id_usuario)
        perfil = Perfil.objects.get(user = user)
        if not user.is_authenticated():
            perfil = None
        else:
            if PerfilRolClub.objects.filter(perfil=perfil, rol__id = settings.ROL_ADMINISTRADOR).count() > 0:
                perfil = None
    except User.DoesNotExist:
        perfil = None
    except Exception:
        logger.debug("util/utils - Método comprueba_usuario_logado_no_administrador: id_usuario " + str(id_usuario))
    return perfil
