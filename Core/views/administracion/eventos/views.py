# -*- encoding: utf-8 -*-
from Core.views import *
from django.core import serializers
from Core.utils import *
from Core.forms import *
from datetime import datetime, time
from array import array
import logging
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from Core.plantillas_mail import *
import os

#Instancia del log
logger = logging.getLogger(__name__)

#Rutas de la vista
ruta_eventos = "administracion/eventos/eventos.html"
ruta_nuevo_evento = "administracion/eventos/nuevo_evento.html"
ruta_editar_evento = "administracion/eventos/editar_evento.html"

@login_required()
def eventos(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    data = {}
    error = ""

    data = {
        'perfil':perfil, 'club':club, 'error':error
    }

    try:
        if request.method == "POST":
            fecha = request.POST.get("fecha")
            if fecha:
                fecha_ajustada = datetime.strptime(fecha, '%d/%m/%Y').date()
                eventos = Evento.objects.filter(club = club, fecha = fecha_ajustada).order_by("-fecha")
            else:
                eventos = Evento.objects.filter(club = club).order_by("-fecha")[:20]

            data["fecha"] = fecha
        else:
            eventos = Evento.objects.filter(club = club).order_by("-fecha")[:20]

        data["eventos"] = eventos

    except Exception, e:
        logger.debug("administracion/eventos - Método eventos: id_usuario " + str(id_usuario) + e.message)

    return render_to_response(ruta_eventos, data, context_instance=RequestContext(request))

@login_required()
def nuevo_evento(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    data = {}
    errores = []
    success = ""
    horas = cargar_horas()
    minutos = cargar_minutos()
    data = {
        'perfil':perfil, 'club':club, 'horas':horas, 'minutos':minutos
    }

    try:
        eventos = Evento.objects.filter(club = club).order_by("-fecha")
        data["eventos"] = eventos

        pistas = Pista.objects.filter(club = club).order_by("orden")
        data["pistas"] = pistas

        franjas_horarias = FranjaHora.objects.filter(club = club).order_by("inicio")
        data["franjas_horarias"] = franjas_horarias

    except Exception, e:
        logger.debug("administracion/eventos - Método nuevo_evento: id_usuario " + str(id_usuario) + e.message)

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        minuto = request.POST.get("minutos")
        imagen = request.POST.get("imagen")
        descripcion = request.POST.get("descripcion")
        partido_publico = request.POST.get("partido_publico")
        if nombre and fecha and hora and minutos and descripcion and partido_publico:
            try:
                hora_ajustada = time(int(hora), int(minuto))
                fecha_ajustada = datetime.strptime(fecha, '%d/%m/%Y').date()

                imagen_ajustada = None
                if request.FILES.get("imagen"):
                    imagen_ajustada = request.FILES.get("imagen")

                partido_publico_ajustado = bool(int(partido_publico))

                #Partidos del evento
                partidos_evento = []

                #Recorremos las franjas horarias para sacar las seleccionadas:
                fh_eventos = []
                fh_eventos_id = []
                for fh in franjas_horarias.all():
                    fh_valor = bool(int(request.POST.get("fh_"+str(fh.id))))
                    if fh_valor:
                        fh_eventos.append(fh)
                        fh_eventos_id.append(fh.id)

                #Recorremos las pistas para sacar las seleccionadas:
                mapa_franja_horaria_pista = {}
                pistas_eventos_id = []
                for p in pistas.all():
                    pista_valor = bool(int(request.POST.get("pista_"+str(p.id))))
                    pistas_seleccionadas = []
                    if pista_valor:
                        try:
                            pista = Pista.objects.get(id = p.id)
                            pistas_eventos_id.append(pista.id)
                            #Comprobar pista disponible en cada franja horaria
                            for franja in fh_eventos:
                                disponible = comprueba_pista_disponible(franja.id, pista.id, fecha_ajustada)
                                if disponible:
                                    if franja in mapa_franja_horaria_pista:
                                        lista_aux = mapa_franja_horaria_pista[franja]
                                        if not pista in lista_aux:
                                            lista_aux.append(pista)
                                            mapa_franja_horaria_pista[franja] = lista_aux
                                        lista_aux = []
                                    else:
                                        if not pista in pistas_seleccionadas:
                                            pistas_seleccionadas.append(pista)
                                        mapa_franja_horaria_pista[franja] = pistas_seleccionadas
                                else:
                                    error = "Pista " + str(pista.nombre) + " ya estaba reservada en la franja horaria " + str(franja.inicio) + "\n"
                                    errores.append(error)

                        except Exception, e:
                            logger.debug("administracion/eventos - Método nuevo_evento (method:post buscando pista "+str(p.id)+"): id_usuario " + str(id_usuario) + e.message)
                            break

                #Si no hay errores, se guardan los datos
                if len(errores) == 0:

                    #Por cada pista en la franja horaria, se crea el partido asociado
                    for franja_horaria, lista_pistas in mapa_franja_horaria_pista.iteritems():

                        for pista in lista_pistas:
                            partido_evento = Partido.objects.create(
                                franja_horaria = franja_horaria,
                                pista = pista,
                                creado_por = perfil,
                                visible = partido_publico_ajustado,
                                fecha = fecha_ajustada
                            )
                            partidos_evento.append(partido_evento)

                    evento_nuevo = Evento.objects.create(
                        nombre = nombre,
                        club = club,
                        fecha = fecha_ajustada,
                        hora = hora_ajustada,
                        imagen = imagen_ajustada,
                        descripcion = descripcion.strip(),
                        creado_por = perfil
                    )

                    evento_nuevo.partidos = partidos_evento
                    evento_nuevo.save()
                    success = "Se ha creado el evento correctamente"

                data["nombre"] = nombre
                data["fecha"] = fecha_ajustada
                data["hora"] = int(hora)
                data["minuto"] = int(minuto)
                data["imagen"] = evento_nuevo.imagen
                data["descripcion"] = descripcion
                data["pistas_eventos_id"] = pistas_eventos_id
                data["fh_eventos_id"] = fh_eventos_id
                data["hora_evento"] = int(hora)
                data["minuto_evento"] = int(minuto)

            except Exception, e:
                logger.debug("administracion/eventos - Metodo nuevo_evento (method:post): id_usuario " + str(id_usuario) + e.message)
                error = "Ha habido un error al crear el evento"
                errores.append(error)
        else:
            error = "Debe rellenar todos los campos"
            errores.append(error)

        data["errores"] = errores
        data["success"] = success

    return render_to_response(ruta_nuevo_evento, data, context_instance=RequestContext(request))


@login_required()
def editar_evento(request, id_usuario, id_evento):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    data = {}
    errores  = []
    horas = cargar_horas()
    minutos = cargar_minutos()
    error = ""
    success = ""

    data = {
        'perfil':perfil, 'club':club, 'errores':errores, 'horas': horas, 'minutos':minutos
    }

    try:

        pistas = Pista.objects.filter(club = club).order_by("orden")
        data["pistas"] = pistas

        franjas_horarias = FranjaHora.objects.filter(club = club).order_by("inicio")
        data["franjas_horarias"] = franjas_horarias

        evento_editar = Evento.objects.get(id = id_evento)
        data["evento_editar"] = evento_editar

        data["nombre"] = evento_editar.nombre
        data["fecha"] = evento_editar.fecha
        data["imagen"] = evento_editar.imagen
        data["descripcion"] = evento_editar.descripcion

        #Sacamos pistas
        pistas_eventos_id = evento_editar.partidos.all().values_list('pista_id', flat = True)
        data["pistas_eventos_id"] = pistas_eventos_id

        fh_eventos_id = evento_editar.partidos.all().values_list('franja_horaria_id', flat=True)
        data["fh_eventos_id"] = fh_eventos_id

        data["hora_evento"] = evento_editar.hora.hour
        data["minuto_evento"] = evento_editar.hora.minute

        #Si el evento esta bloqueado, se informa al usuario
        if evento_editar.bloqueado():
            errores.append("No puedes editar este evento porque tiene fecha anterior a hoy.")
            data["errores"] = errores


        #Si viene del formulario
        if request.method == "POST":
            nombre = request.POST.get("nombre")
            fecha = request.POST.get("fecha")
            hora = request.POST.get("hora")
            minuto = request.POST.get("minutos")
            imagen = request.POST.get("imagen")
            descripcion = request.POST.get("descripcion")
            if nombre and fecha and hora and minutos and descripcion:
                try:
                    hora_ajustada = time(int(hora), int(minuto))
                    fecha_ajustada = datetime.strptime(fecha, '%d/%m/%Y').date()

                    imagen_ajustada = None
                    if request.FILES.get("imagen"):
                        imagen_ajustada = request.FILES.get("imagen")
                        if imagen_ajustada and evento_editar.imagen:
                            borrar_imagen_anterior(evento_editar.imagen.path)
                    else:
                        imagen_ajustada = evento_editar.imagen

                    #Partidos del evento
                    partidos_evento = []

                    #Recorremos las franjas horarias para sacar las seleccionadas:
                    fh_eventos = []
                    fh_eventos_id = []
                    for fh in franjas_horarias.all():
                        fh_valor = bool(int(request.POST.get("fh_"+str(fh.id))))
                        if fh_valor:
                            fh_eventos.append(fh)
                            fh_eventos_id.append(fh.id)

                    #Recorremos las pistas para sacar las seleccionadas:
                    mapa_franja_horaria_pista = {}
                    mapa_franja_horaria_pista_anterior = {}

                    #Rellenamos el mapa con las franjas y partidos que ya tiene
                    for partido in evento_editar.partidos.all():
                        if partido.franja_horaria in mapa_franja_horaria_pista_anterior:
                            mapa_franja_horaria_pista_anterior[partido.franja_horaria].append(partido.pista)
                        else:
                            lista_pistas = []
                            lista_pistas.append(partido.pista)
                            mapa_franja_horaria_pista_anterior[partido.franja_horaria] = lista_pistas

                    #Borramos los partidos que tenia asociados para que no salten como no disponibles
                    evento_editar.partidos.all().delete()

                    pistas_eventos_id = []
                    for p in pistas.all():
                        pista_valor = bool(int(request.POST.get("pista_"+str(p.id))))
                        pistas_seleccionadas = []
                        if pista_valor:
                            try:
                                pista = Pista.objects.get(id = p.id)
                                pistas_eventos_id.append(pista.id)
                                #Comprobar pista disponible en cada franja horaria
                                for franja in fh_eventos:
                                    disponible = comprueba_pista_disponible(franja.id, pista.id, fecha_ajustada)
                                    if disponible:
                                        if franja in mapa_franja_horaria_pista:
                                            mapa_franja_horaria_pista[franja].append(pista)
                                        else:
                                            if not pista in pistas_seleccionadas:
                                                pistas_seleccionadas.append(pista)
                                                mapa_franja_horaria_pista[franja] = pistas_seleccionadas
                                    else:
                                        error = "Pista " + str(pista.nombre) + " ya estaba reservada en la franja horaria " + str(franja.inicio) + "\n"
                                        errores.append(error)

                            except Exception, e:
                                logger.debug("administracion/eventos - Método editar_evento (method:post buscando pista "+str(p.id)+"): id_usuario " + str(id_usuario) + e.message)
                                break

                    #Si no hay errores, se guardan los datos
                    if len(errores) == 0:

                        #Por cada pista en la franja horaria, se crea el partido asociado
                        for franja_horaria, lista_pistas in mapa_franja_horaria_pista.iteritems():

                            for pista in lista_pistas:
                                partido_evento = Partido.objects.create(
                                    franja_horaria = franja_horaria,
                                    pista = pista,
                                    creado_por = perfil,
                                    visible = settings.ESTADO_NO,
                                    fecha = fecha_ajustada
                                )
                                partidos_evento.append(partido_evento)

                        #Se asignan nuevos campos
                        evento_editar.nombre = nombre
                        evento_editar.club = club
                        evento_editar.fecha = fecha_ajustada
                        evento_editar.imagen = imagen_ajustada
                        evento_editar.hora = hora_ajustada
                        evento_editar.descripcion = descripcion.strip()

                        evento_editar.partidos = partidos_evento
                        evento_editar.save()
                        success = "Se ha guardado el evento correctamente"

                    else:
                        #Recuperamos partidos que tenia antes y guardamos
                        partidos_evento_editar = []
                        for franja_horaria, lista_pistas in mapa_franja_horaria_pista.iteritems():
                            for pista in lista_pistas:
                                partido_evento = Partido.objects.create(
                                    franja_horaria = franja_horaria,
                                    pista = pista,
                                    creado_por = perfil,
                                    visible = settings.ESTADO_NO,
                                    fecha = fecha_ajustada
                                )
                                partidos_evento_editar.append(partido_evento)
                        evento_editar.partidos = partidos_evento_editar
                        evento_editar.save()

                    data["nombre"] = nombre
                    data["fecha"] = fecha_ajustada
                    data["hora"] = hora
                    data["minuto"] = minuto
                    data["imagen"] = evento_editar.imagen
                    data["descripcion"] = descripcion
                    data["pistas_eventos_id"] = pistas_eventos_id
                    data["fh_eventos_id"] = fh_eventos_id
                    data["hora_evento"] = int(hora)
                    data["minuto_evento"] = int(minuto)

                except Exception, e:
                    logger.debug("administracion/eventos - Metodo editar_evento (method:post): id_usuario " + str(id_usuario) + e.message)
                    error = "Ha habido un error al editar el evento"
                    errores.append(error)
            else:
                error = "Debe rellenar todos los campos"
                errores.append(error)

            data["errores"] = errores
            data["success"] = success

    except Exception, e:
        logger.debug("administracion/eventos - Método editar_evento: id_usuario " + str(id_usuario) + e.message)

    return render_to_response(ruta_editar_evento, data, context_instance=RequestContext(request))


@login_required()
def difundir_evento(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    titulo = "Nuevo evento en el club " + club.nombre
    data = {}
    error = ""
    success = ""
    eventos = []

    data = {
        'perfil':perfil, 'club':club, 'error':error
    }

    try:

        eventos = Evento.objects.filter(club = club).order_by("-fecha")[:20]

        if request.method == "POST":
            evento_id = request.POST.get("evento")
            if evento_id:
                evento = Evento.objects.get(id = evento_id)
                jugadores = PerfilRolClub.objects.filter(club = club, perfil__user__is_active = True)
                for jugador in jugadores.all():
                    texto = plantilla_email_difundir_evento(jugador.perfil.user.first_name, evento)
                    if not enviar_email(titulo, settings.EMAIL_HOST_USER, jugador.perfil.user.email, texto):
                        error = "No se ha podido difundir el evento para todos los jugadores."
                    else:
                        success = "Se ha difundido el evento entre todos los jugadores"

    except Exception, e:
        logger.debug("administracion/eventos - Método difundir_evento: id_usuario " + str(id_usuario) + e.message)
        error = "Ha habido un error al difundir el evento. Actualiz la página e inténtalo de nuevo"

    data["eventos"] = eventos
    data["success"] = success
    data["error"] = error

    return render_to_response(ruta_eventos, data, context_instance=RequestContext(request))

@login_required()
def eliminar_evento(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    data = {}
    error = ""
    success = ""

    data = {
        'perfil':perfil, 'club':club
    }

    try:
        if request.method == "POST":
            evento_id = request.POST.get("evento")
            if evento_id:
                try:
                    evento = Evento.objects.get(id = evento_id)
                    evento.partidos.all().delete()
                    evento.delete()
                    success = "Se ha eliminado el evento correctamente"
                except Evento.DoesNotExist:
                    error = "Ha habido un error al eliminar el evento. Inténtelo de nuevo"
            else:
                error = "Ha habido un error al eliminar el evento. Inténtelo de nuevo"

        eventos = Evento.objects.filter(club = club).order_by("-fecha")[:20]

    except Exception, e:
        logger.debug("administracion/eventos - Método eliminar_evento: id_usuario " + str(id_usuario) + e.message)
        error = "Ha habido un error al eliminar el evento. Inténtelo de nuevo"

    data["eventos"] = eventos
    data["success"] = success
    data["error"] = error

    return render_to_response(ruta_eventos, data, context_instance=RequestContext(request))

##############################################################
####### FUNCIONES AUXILIARES
##############################################################

def cargar_horas():
    horas = range(0, 24)
    return horas

def cargar_minutos():
    return range(0, 60, 5)

def estaDisponible(club, pista, fecha, hora, eventos):
        disponible = True
        try:
            num_partidos = Partido.objects.filter(
                Q(franja_horaria__inicio__gte=hora) | Q(franja_horaria__fin__lte=hora),
                pista__id = pista.id, fecha = fecha).count()
            if num_partidos > 0:
                disponible = False
            else:
                for e in eventos:
                    if e["pista"] == pista.id:
                        disponible = False
                        break

        except Exception, e:
            logger.debug("administracion/eventos - Método estaDisponible : pista " + str(pista.id) + e.message)
            disponible = False
        return disponible


def comprueba_pista_disponible(franja_horaria_id, pista_id, fecha):
    disponible = True
    try:
        if Partido.objects.filter(pista__id = pista_id, fecha__startswith=fecha, franja_horaria__id = franja_horaria_id).exists():
            disponible = False
    except Exception, e:
        logger.debug("administracion/eventos - Método comprueba_pista_disponible : Franja " + str(franja_horaria_id) + ". Pista" + str(pista_id) + e.message)
        disponible = False
    return disponible


def borrar_imagen_anterior(url_imagen):
    try:
        if os.path.isfile(url_imagen):
            os.remove(url_imagen)
    except Exception:
        print "Imagen no encontrada:" +url_imagen
        logger.debug("administracion/eventos - Método borrar_imagen_anterior url: " + url_imagen)
