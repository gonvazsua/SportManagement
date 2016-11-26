# -*- encoding: utf-8 -*-
from Core.models import *
from django.shortcuts import *
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import BadHeaderError

import logging

#Instancia del log
logger = logging.getLogger(__name__)

def comprueba_usuario_administrador(id_usuario, request):
    user = ""
    perfil = ""
    try:
        if request.user.is_authenticated() and request.user.id == int(id_usuario):
            perfil = Perfil.objects.get(user = request.user)

            #Se anade comprobacion para evitar que no se pierda la sesion de demo
            if not "es_demo" in request.session and request.user.username == settings.USERNAME_DEMO:
                request.session["es_demo"] = True

            if not PerfilRolClub.objects.filter(perfil = perfil, rol_id = settings.ROL_ADMINISTRADOR).exists():
                raise Http404
            if not request.user.is_authenticated():
                raise Http404
        else:
            raise Http404

    except User.DoesNotExist:
        logger.debug("util/utils - Método comprueba_usuario_administrador: No existe usuario " + str(id_usuario))
        raise Http404
    except Exception, e:
        logger.debug("util/utils - Método comprueba_usuario_administrador: id_usuario " + str(id_usuario))
        raise Http404
    return perfil


def comprueba_usuario_logado_no_administrador(id_usuario, request):
    user = ""
    perfil = ""
    try:
        if request.user.is_authenticated() and request.user.id == int(id_usuario):
            user = User.objects.get(id = id_usuario)
            perfil = Perfil.objects.get(user = user)
        else:
            raise Http404
    except User.DoesNotExist:
        raise Http404
    except Exception:
        logger.debug("util/utils - Método comprueba_usuario_logado_no_administrador: id_usuario " + str(id_usuario))
        raise Http404
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


#Cargar tipos de notificaciones desde settings
def cargar_tipos_notificaciones_settings(data):

    data["TIPO_NOTIF_UNIRSE_A_PARTIDO"] = settings.TIPO_NOTIF_UNIRSE_A_PARTIDO
    data["TIPO_NOTIF_INSCRIPCION_CLUB"] = settings.TIPO_NOTIF_INSCRIPCION_CLUB
    data["TIPO_NOTIF_JUEGA_PARTIDO"] = settings.TIPO_NOTIF_JUEGA_PARTIDO
    data["TIPO_NOTIF_COMENTARIO_PARTIDO"] = settings.TIPO_NOTIF_COMENTARIO_PARTIDO

    return data


#Generar notificaciones de nuevo partido
def generarNotificacionesPartidoPerfiles(nuevo_partido):

    try:
        #Consultar club
        club = nuevo_partido.pista.club

        #Se genera notificacion para jugadores
        for jugador in nuevo_partido.perfiles.all():

            #Si el perfil es el mismo que crea el partido, no se crea notificacion
            if nuevo_partido.creado_por.id == jugador.id:
                continue

            #Si no existe notificacion generada para este partido y este jugador, se crea
            notificacion = Notificacion.objects.filter(
                tipo = settings.TIPO_NOTIF_JUEGA_PARTIDO,
                destino = settings.NOTIF_JUGADOR,
                partido = nuevo_partido,
                club = club,
                jugador = jugador
            ).exists()

            if(notificacion == False):

                Notificacion.objects.create(
                    tipo = settings.TIPO_NOTIF_JUEGA_PARTIDO,
                    destino = settings.NOTIF_JUGADOR,
                    leido = settings.ESTADO_NO,
                    partido = nuevo_partido,
                    club = club,
                    jugador = jugador
                )

    except Exception, e:
        logger.debug("utils.py - Método generarNotificacionesPartidoPerfiles. " + e.message)

    return ""

#Comprobar si un usuario pertenece a un club
def compruebaUsuarioPerteneceAClub(id_perfil, id_club):

    pertenece = False

    try:
        pertenece = PerfilRolClub.objects.filter(perfil__id = id_perfil, club__id = id_club).exists()

        if pertenece == False:
            raise 404

    except Exception, e:
        logger.debug("utils.py - Método compruebaUsuarioPerteneceAClub. " + e.message)
        raise 404