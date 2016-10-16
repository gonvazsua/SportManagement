# -*- encoding: utf-8 -*-
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import json
import logging
from django.core.mail import EmailMultiAlternatives
from Core.models import *
import hashlib

#Instancia del log
logger = logging.getLogger(__name__)

def send_email(request):
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    from_email = request.POST.get('from_email', '')
    error = ""
    if subject and message and from_email:
        try:
            texto = "<h5>Email enviado desde Sport Click:</h5> \n"
            texto += "<h5>De: </h5>" + from_email + "\n"
            texto += "<h5>Titulo: </h5>" + subject + "\n"
            texto += "<h5>Cuerpo: </h5>" + message + "\n"
            #send_mail(subject, texto, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            msg = EmailMultiAlternatives(subject,'' , settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            msg.attach_alternative(texto, "text/html")
            msg.send()
        except BadHeaderError, e:
            logger.debug("util/views - Método send_email." + e.message)
            error = "Ha habido un error en el proceso. Disculpe las molestias"
        except Exception, e:
            logger.debug("util/views - Método send_email." + e.message)
            error = "Ha habido un error en el proceso. Disculpe las molestias"
    else:
        error = "Rellene correctamente todos los campos"
    data = {'error':error}
    return HttpResponse(json.dumps(data))


def comentario_partido(request):

    direccionRedirect = "/"

    try:
        if request.method == "POST":

            partido_id = request.POST.get("partido_id")
            perfil_id = request.POST.get("perfil_id")
            comentario = request.POST.get("comentario")
            vieneDe = request.POST.get("vieneDe")

            if partido_id and perfil_id and comentario and vieneDe:

                #Se consultan objetos
                perfil = Perfil.objects.get(id = perfil_id)
                partido = Partido.objects.get(id = partido_id)

                if perfil and partido and comentario:

                    #Se crea el comentario
                    ComentarioPartido.objects.create(
                        creado_por = perfil,
                        texto = comentario,
                        partido = partido
                    )

                    generarNotificacionesComentarios(partido, perfil)

                    if vieneDe == "usuarios":
                        direccionRedirect = "/usuario/" + str(perfil.user.id) + "/partidos/" + str(partido.id)
                    elif vieneDe == "administrador":
                        direccionRedirect = "administrador/" + str(perfil.user.id) + "/partido/" + str(partido.id) + "/editar#fila_comentarios"

    except Exception, e:
        logger.debug("util/views - Metodo comentario_partido." + e.message)

    return HttpResponseRedirect(direccionRedirect)


def generarNotificacionesComentarios(partido, perfil):

    try:
        #Lista de perfiles que deben recibir notificacion
        lista_perfiles = []

        #Jugadores del partido
        for jugador in partido.perfiles.all():
            lista_perfiles.append(jugador)

        #Perfiles que habian comentado este partido
        perfiles_comentarios = ComentarioPartido.objects.values_list('creado_por', flat=True).filter(partido = partido).distinct()
        for pc in perfiles_comentarios:
            lista_perfiles.append(Perfil.objects.get(id = int(pc)))

        #Eliminar duplicados
        lista_perfiles = eliminarDuplicados(lista_perfiles)

        #Notificaciones para todos los jugadores excepto para el que crea el comentario
        for jugador in lista_perfiles:

            if perfil.id != jugador.id:
                Notificacion.objects.create(
                    leido = settings.ESTADO_NO,
                    tipo = settings.TIPO_NOTIF_COMENTARIO_PARTIDO,
                    destino = settings.NOTIF_JUGADOR,
                    partido = partido,
                    club = partido.pista.club,
                    jugador = jugador,
                    estado = settings.ESTADO_NULL
                )

    except Exception, e:
        lista_perfiles = []


def eliminarDuplicados(lista_perfiles):

    lista_res = []

    #Guardo en lista cada id distinto
    for perfil in lista_perfiles:
        if not perfil in lista_res:
            lista_res.append(perfil)

    return lista_res