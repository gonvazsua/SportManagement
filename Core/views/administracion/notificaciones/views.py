# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from datetime import date,datetime
import json
from django.db.models import Q
import logging
from django.contrib.auth.decorators import login_required

#Instancia del log
logger = logging.getLogger(__name__)

ruta_administracion_notificaciones = 'administracion/notificaciones/notificaciones.html'

@login_required()
def notificaciones(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)

    #Notificaciones
    try:
        inscripciones_club_id = InscripcionesEnClub.objects.values_list('id', flat=True).filter(club=club)
        inscripciones_partido_id = InscripcionesEnPartido.objects.values_list('id', flat=True).filter(partido__pista__club=club)
        notificaciones = Notificacion.objects.filter(Q(inscripcionEnClub__id__in=inscripciones_club_id) | Q(inscripcionEnPartido__id__in=inscripciones_partido_id), destino=settings.NOTIF_CLUB).order_by("-fecha","-id")
    except Exception:
        notificaciones = []

    data = {'perfil':perfil, 'club':club, 'notificaciones':notificaciones}
    return render_to_response(ruta_administracion_notificaciones, data, context_instance=RequestContext(request))

@login_required()
def marcar_como_leida(request):
    error = ""
    if request.method == "GET":
        notificacion_id = request.GET.get("notificacion_id")
        if notificacion_id:
            try:
                notificacion = Notificacion.objects.get(id=notificacion_id)
                notificacion.leido = settings.ESTADO_SI
                notificacion.save()
            except Exception:
                logger.debug("administracion/notificaciones - Método marcar_como_leida")
                error = "Ha sucedido un error, inténtelo de nuevo más tarde"
        else:
            logger.debug("administracion/notificaciones - Método marcar_como_leida")
            error = "Ha sucedido un error, inténtelo de nuevo más tarde"
    data = {'error':error}
    return HttpResponse(json.dumps(data))

@login_required()
def aceptar_denegar_inscripcion(request):
    error = ""
    if request.method == "POST":
        notificacion_id = request.POST.get("inscripcion_id")
        estado = request.POST.get("estado")
        club_id = request.POST.get("club_id")
        jugador_id = request.POST.get("jugador_id")
        if notificacion_id and estado and club_id and jugador_id:
            try:
                #Convertir a boolean el estado
                estado = bool(int(estado))

                #Crear PerfilRolClub
                rol = Rol.objects.get(id=settings.ROL_JUGADOR)
                jugador = Perfil.objects.get(id=jugador_id)
                club = Club.objects.get(id=club_id)

                notificacion = Notificacion.objects.get(id=notificacion_id)
                #Generar notificacion para el jugador
                notificacion_jugador = Notificacion.objects.create(
                    leido = settings.ESTADO_NO,
                    destino = settings.NOTIF_JUGADOR,
                    fecha = notificacion.fecha
                )

                notificacion.leido = settings.ESTADO_SI

                if notificacion.inscripcionEnClub:
                    notificacion.inscripcionEnClub.estado = estado
                    notificacion_jugador.inscripcionEnClub = notificacion.inscripcionEnClub
                    notificacion.inscripcionEnClub.save()
                    notificacion.save()

                    if estado != settings.ESTADO_NO:
                        perfilRolClub = PerfilRolClub.objects.create(rol=rol, perfil=jugador, club=club)
                        perfilRolClub.save()

                elif notificacion.inscripcionEnPartido:
                    notificacion.inscripcionEnPartido.estado = estado
                    if estado:
                        partido = Partido.objects.get(id=notificacion.inscripcionEnPartido.partido.id)
                        if partido.num_perfiles() >= partido.max_perfiles():
                            error = "El partido ya tiene el máximo de jugadores"
                        elif partido.bloqueado():
                            error = "Este partido tiene fecha anterior a hoy"
                        else:
                            partido_perfil = Partido_perfiles.objects.create(
                                partido = partido,
                                perfil = jugador,
                                pago = None,
                                fecha_pago = None
                            )
                    notificacion.inscripcionEnPartido.save()
                    notificacion_jugador.inscripcionEnPartido = notificacion.inscripcionEnPartido
                    notificacion.save()

                if error == "" and notificacion and notificacion_jugador:
                    notificacion_jugador.save()
                else:
                    notificacion.save()

            except Exception, e:
                logger.debug("administracion/notificaciones - Método aceptar_denegar_inscripcion:" + e.message)
                error = "Ha sucedido un error, actualice la página e inténtelo de nuevo"
        else:
            logger.debug("administracion/notificaciones - Método aceptar_denegar_inscripcion")
            error = "Ha sucedido un error, actualice la página e inténtelo de nuevo"
    else:
        logger.debug("administracion/notificaciones - Método aceptar_denegar_inscripcion")
        error = "Ha sucedido un error, actualice la página e inténtelo de nuevo"
    data = {'error':error}
    return HttpResponse(json.dumps(data))


@login_required()
def comprobar_notificaciones(request):
    num_nofiticaciones = 0
    club_id = None
    try:
        club_id = request.session["club_id"]
        if club_id:
            inscripciones_club_id = InscripcionesEnClub.objects.values_list('id', flat=True).filter(club__id=club_id)
            inscripciones_partido_id = InscripcionesEnPartido.objects.values_list('id', flat=True).filter(partido__pista__club__id=club_id)
            num_notificaciones = Notificacion.objects.filter(Q(inscripcionEnClub__id__in=inscripciones_club_id) | Q(inscripcionEnPartido__id__in=inscripciones_partido_id), destino=settings.NOTIF_CLUB,leido = settings.ESTADO_NO).count()

    except Exception, e:
        num_notificaciones = 0

    data = {'num_notificaciones':num_notificaciones}
    return HttpResponse(json.dumps(data))