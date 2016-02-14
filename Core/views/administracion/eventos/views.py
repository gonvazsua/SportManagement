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
import operator

#Instancia del log
logger = logging.getLogger(__name__)

#Rutas de la vista
ruta_eventos = "administracion/eventos/eventos.html"
ruta_nuevo_evento = "administracion/eventos/nuevo_evento.html"

@login_required()
def eventos(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    data = {}
    error = ""

    data = {
        'perfil':perfil, 'club':club, 'error':error
    }

    try:
        eventos = Evento.objects.filter(club = club).order_by("-fecha")
        data["eventos"] = eventos
    except Exception, e:
        logger.debug("administracion/eventos - Método eventos: id_usuario " + str(id_usuario) + e.message)

    return render_to_response(ruta_eventos, data, context_instance=RequestContext(request))

@login_required()
def nuevo_evento(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    data = {}
    error = ""
    success = ""
    horas = cargar_horas()
    minutos = cargar_minutos()
    data = {
        'perfil':perfil, 'club':club, 'horas':horas, 'minutos':minutos
    }

    try:
        eventos = Evento.objects.filter(club = club).order_by("-fecha")
        data["eventos"] = eventos

        pistas = Pista.objects.filter(club = club).values("id", "nombre").order_by("orden")
        data["pistas"] = pistas

    except Exception, e:
        logger.debug("administracion/eventos - Método nuevo_evento: id_usuario " + str(id_usuario) + e.message)

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
                if request.FILES.get("imagen") != None:
                    formImagen = FormImagen(request.POST, request.FILES)
                    imagen_ajustada = formImagen.cleaned_data["imagen"]

                #Sacar eventos para comprobar pistas
                eventos = Evento.objects.filter(club = club, fecha = fecha_ajustada).values("pistas")

                #Recorremos las pistas para sacar las seleccionadas:
                pistas_eventos = []
                pistas_eventos_id = []
                for p in pistas.all():
                    pista_valor = bool(int(request.POST.get("pista_"+str(p["id"]))))
                    if pista_valor:
                        try:
                            pista = Pista.objects.get(id = p["id"])
                            if estaDisponible(club, pista, fecha_ajustada, hora_ajustada, eventos):
                                pistas_eventos.append(pista)
                                pistas_eventos_id.append(pista.id)
                            else:
                                error = "La pista " + p["nombre"] + " está reservada para esa fecha y hora."
                        except Exception, e:
                            error = "La pista " + ["nombre"] + " está reservada para esa fecha y hora."
                            logger.debug("administracion/eventos - Método nuevo_evento (method:post buscando pista "+p["id"]+"): id_usuario " + str(id_usuario) + e.message)

                if error == "":
                    evento_nuevo = Evento.objects.create(
                        nombre = nombre,
                        club = club,
                        fecha = fecha_ajustada,
                        hora = hora_ajustada,
                        imagen = imagen_ajustada,
                        descripcion = descripcion.strip()
                    )
                    evento_nuevo.pistas = pistas_eventos
                    evento_nuevo.save()

                    error = ""
                    success = "Se ha creado el evento correctamente"
                    data["evento"] = evento_nuevo
                    data["pistas_eventos_id"] = pistas_eventos_id
                    data["hora_evento"] = hora
                    data["minuto_evento"] = minuto

            except Exception, e:
                logger.debug("administracion/eventos - Método nuevo_evento (method:post): id_usuario " + str(id_usuario) + e.message)
                error = "Ha habido un error al crear el evento"
        else:
            error = "Debe rellenar todos los campos"

        data["error"] = error
        data["success"] = success

    return render_to_response(ruta_nuevo_evento, data, context_instance=RequestContext(request))


def cargar_horas():
    horas = range(0, 24)
    return horas

def cargar_minutos():
    return range(0, 60, 5)

def estaDisponible(club, pista, fecha, hora, eventos):
        disponible = True
        try:
            num_partidos = Partido.objects.filter(pista__id = pista.id, fecha = fecha, franja_horaria__inicio__gte=hora, franja_horaria__fin__lte=hora).count()
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