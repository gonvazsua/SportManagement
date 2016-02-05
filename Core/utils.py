# -*- encoding: utf-8 -*-
from Core.models import *
from django.shortcuts import *
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import BadHeaderError

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
            raise Http404
        if not user.is_authenticated():
            raise Http404
    except User.DoesNotExist:
        logger.debug("util/utils - Método comprueba_usuario_administrador: No existe usuario " + str(id_usuario))
        raise Http404
    except Exception, e:
        logger.debug("util/utils - Método comprueba_usuario_administrador: id_usuario " + str(id_usuario))
        raise Http404
    return perfil


def comprueba_usuario_logado_no_administrador(id_usuario):
    user = ""
    perfil = ""
    try:
        user = User.objects.get(id = id_usuario)
        perfil = Perfil.objects.get(user = user)
        if not user.is_authenticated():
            raise Http404
    except User.DoesNotExist:
        raise Http404
    except Exception:
        logger.debug("util/utils - Método comprueba_usuario_logado_no_administrador: id_usuario " + str(id_usuario))
    return perfil

#Metodo que obtiene el club a partir del id
#Si es none, se busca el primero que aparezca en la lista
def obtener_club_de_sesion_administrador(club_id, perfil_id):
    try:

        club = Club.objects.get(id = club_id)

    except Exception:

        clubes = Club.objects.filter(
            id__in = PerfilRolClub.objects.values_list('club_id',flat=True).filter(
                perfil__id = perfil_id, rol__id=settings.ROL_ADMINISTRADOR))

        if clubes.count() > 0:
            club = clubes.first()

    return club

def enviar_email(titulo, de, para, texto):

    enviado = False

    try:

        msg = EmailMultiAlternatives(titulo,'' , de, [para])
        msg.attach_alternative(texto, "text/html")
        msg.send()
        enviado = True

    except BadHeaderError, e:
        logger.debug("util/views - Método send_email." + e)
        enviado = False

    except Exception, e:
        logger.debug("util/views - Método send_email." + e)
        enviado = False

    return enviado