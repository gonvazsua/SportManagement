# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from datetime import date,datetime
import json
import logging
from django.contrib.auth.decorators import login_required
from Core.plantillas_mail import *
from Core.utils import generarNotificacionesPartidoPerfiles

#Instancia del log
logger = logging.getLogger(__name__)

ruta_administracion_nuevo_partido = 'administracion/partidos/nuevo_partido.html'
ruta_administracion_editar_partido = 'administracion/partidos/editar_partido.html'
ruta_administracion_buscador_partidos = 'administracion/partidos/buscador_partidos.html'
ruta_administracion_ver_partido = 'administracion/partidos/ver_partido.html'
ruta_administracion_planificar = 'administracion/partidos/planificar.html'

@login_required()
def administrador_crear_partido(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    error = ""
    pistas = Pista.objects.filter(club=club).order_by('deporte__deporte', 'orden')

    #Recogemos posibles parámetros en caso de que vengan en la URL
    pista = ""
    franja_horaria = ""
    if "pista_id" in  request.GET and "fh_id" in request.GET:
        pista = int(request.GET["pista_id"])
        franja_horaria = int(request.GET["fh_id"])

    franjas_horarias = FranjaHora.objects.filter(club = club).order_by('inicio')
    data = {
        'perfil':perfil, 'club':club, 'pistas':pistas, 'franjas_horarias':franjas_horarias, 'pista':pista, 'franja_horaria':franja_horaria
    }
    if request.method == "POST":
        action = request.POST["action"]
        error = ""
        if action == "disponibilidad":
            if request.POST["franja_horaria"] != "" and request.POST["pista"] != "" and request.POST["club"] != "" and request.POST["fecha"] != "":
                data["fecha"] = request.POST["fecha"]
                data["franja_horaria"] = int(request.POST["franja_horaria"])
                data["pista"] = int(request.POST["pista"])
                fecha = datetime.strptime(request.POST["fecha"], '%d/%m/%Y').date()
                disponible = comprueba_pista_disponible(request.POST["franja_horaria"], request.POST["pista"], fecha)
                data["disponible"] = disponible
                if disponible:
                    try:
                        partidos = Partido.objects.filter(fecha__startswith=fecha, franja_horaria__id = request.POST["franja_horaria"])
                        jug_no_disponibles = []
                        for p in partidos:
                            for perfil in p.perfiles.all():
                                jug_no_disponibles.append(perfil.id)
                        jugadores = PerfilRolClub.objects.filter(club = club, perfil__user__is_active=True).exclude(perfil__in = list(jug_no_disponibles))
                        data["jugadores"] = jugadores
                        map_jugadores = {}
                        deporte_id = Pista.objects.values_list('deporte_id', flat=True).get(id=request.POST["pista"])
                        num_jugadores = Deporte.objects.values_list('num_jugadores', flat=True).get(id=deporte_id)
                        for i in range(1,num_jugadores+1):
                            map_jugadores[i] = ""
                        data["map_jugadores"] = map_jugadores
                        niveles = Nivel.objects.filter(club=club)
                        data["niveles"] = niveles
                        data["deporte_id"] = deporte_id
                    except Exception:
                        logger.debug("administracion/partidos - Método administrador_crear_partido - id_usuario " + str(id_usuario))
                        error = "Ha habido un error al comprobar la disponibilidad. Inténtelo de nuevo. <br> Si el problema persiste, contacte con el adminstrador."
            else:
                logger.debug("administracion/partidos - Método administrador_crear_partido - id_usuario " + str(id_usuario))
                error = "Ha habido un error al comprobar la disponibilidad. Inténtelo de nuevo. <br> Si el problema persiste, contacte con el adminstrador."
            data["error"] = error
            return render_to_response(ruta_administracion_nuevo_partido, data, context_instance=RequestContext(request))
    return render_to_response(ruta_administracion_nuevo_partido, data, context_instance=RequestContext(request))

@login_required()
def administrador_editar_partido(request, id_usuario, id_partido):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    partido = ""
    error = ""

    try:
        partido = Partido.objects.get(id=id_partido)

        map_jugadores = {}
        ids_jugadores = []
        count_jugadores = partido.perfiles.count()

        #Ids de jugadores seleccionados
        ids_jugadores_seleccionados = []

        #Sacar partidos con esa misma fecha y franja hora para quitar a los jugadores
        partidos = Partido.objects.filter(fecha__startswith=partido.fecha, franja_horaria__id = partido.franja_horaria.id).exclude(id=partido.id)
        jug_no_disponibles = []
        for p in partidos:
            for p2 in p.perfiles.all():
                jug_no_disponibles.append(p2.id)

        #Anadir jugadores del partido que se va a editar
        for perfil_actual in partido.perfiles.all():
            jug_no_disponibles.append(perfil_actual.id)

        jugadores = PerfilRolClub.objects.filter(club = club).order_by("perfil__user__last_name")

        #Se forma el mapa de jugadores del partido
        for i in range(1, partido.pista.deporte.num_jugadores + 1):
            if i <= count_jugadores:
                map_jugadores[i] = partido.perfiles.all()[i-1]
                ids_jugadores_seleccionados.append(partido.perfiles.all()[i-1].id)
            else:
                map_jugadores[i] = ""

        pistas = Pista.objects.filter(club=club).order_by('deporte__deporte', 'orden')
        franjas_horarias = FranjaHora.objects.filter(club = club)
        niveles = Nivel.objects.filter(club=club)

        #Deporte para el filtro de niveles
        deporte_id = partido.pista.deporte.id

        #Consultar comentarios del partido
        comentarios = ComentarioPartido.objects.filter(partido = partido).order_by("-fecha")[:30]

        data = {
            'perfil':perfil, 'error':error, 'partido':partido, 'club':club, 'pistas':pistas, 'franjas_horarias':franjas_horarias, 'jugadores':jugadores,
            'map_jugadores':map_jugadores, "niveles" : niveles, 'ids_jugadores_seleccionados':ids_jugadores_seleccionados,
            'comentarios': comentarios, 'deporte_id': deporte_id
        }

    except Partido.DoesNotExist:
        logger.debug("administracion/partidos - Método administrador_editar_partido - id_usuario " + str(id_usuario) + ", id_partido " + str(id_partido))
        error = "Ha habido un error al editar el partido."

    return render_to_response(ruta_administracion_editar_partido, data, context_instance=RequestContext(request))

@login_required()
def buscador_partidos(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    franjas_horarias = FranjaHora.objects.filter(club = club).order_by('inicio')
    data = {
        'perfil':perfil, 'club':club, 'franjas_horarias':franjas_horarias
    }
    if request.method == "POST":
        fecha = ""
        fh = ""
        partidos = ""
        if "fecha" in request.POST:
            fecha = datetime.strptime(request.POST["fecha"], '%d/%m/%Y').date()
        if "franja_horaria" in request.POST:
            fh = int(request.POST["franja_horaria"])
        if fh != 0 and fecha != "":
            partidos = Partido.objects.filter(pista__club = club, fecha__startswith=fecha, franja_horaria__id = fh)
        elif fh == 0 and fecha != "":
            partidos = Partido.objects.filter(pista__club = club, fecha__startswith=fecha)
        else:
            partidos = []
        data["fecha"] = fecha
        data["franja_hora"] = fh
        data["partidos"] = partidos

    return render_to_response(ruta_administracion_buscador_partidos, data, context_instance=RequestContext(request))

@login_required()
def planificar(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario, request)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)

    error = None
    success = None
    data = {
        'perfil':perfil, 'club':club
    }

    try:
        deportes = Deporte.objects.all()
        data["deportes"] = deportes
    except Exception, e:
        logger.debug("administracion/partidos - Método planificar. " + e.message)

    if request.method == "POST":
        try:
            mapa_franjas_partidos = {}
            fecha = request.POST.get("fecha")
            deporte_id = request.POST.get("deporte")
            accion = request.POST.get("accion")

            data["fecha"] = fecha
            data["deporte_id"] = int(deporte_id)

            if fecha and deporte_id:

                fecha = datetime.strptime(fecha, '%d/%m/%Y').date()

                #Se ha pulsado el boton continuar,se crean los partidos
                if accion == "":

                    franjas_horarias = FranjaHora.objects.filter(club = club).order_by('inicio')
                    pistas = Pista.objects.filter(club__id = club.id, deporte__id = deporte_id).order_by("orden")

                    if len(pistas) > 0:

                        #Sacamos los jugadores que ya juegan en este club a esta fecha
                        jugadores_excluir = Partido_perfiles.objects.values_list('perfil', flat=True).filter(partido__in = Partido.objects.filter(pista__club = club, fecha = fecha))

                        max_jugadores = Deporte.objects.values_list('num_jugadores', flat=True).get(id=deporte_id)
                        jugadores = PerfilRolClub.objects.filter(club = club, perfil__user__is_active=True)\
                            .exclude(perfil__id__in = jugadores_excluir)\
                            .order_by("perfil__user__last_name")

                        data["jugadores"] = jugadores
                        data["max_jugadores"] = range(0, max_jugadores)
                        data["franjas_horarias"] = franjas_horarias

                        #Por cada franja y pista, se crea el partido o se comprueba si ya existe.
                        for fh in franjas_horarias.all():
                            lista_partidos = []
                            for pista in pistas.all():
                                #Comprobamos si existe partido:
                                partido_comp = Partido.objects.filter(fecha = fecha, pista = pista, franja_horaria = fh)

                                if partido_comp.count() > 0:
                                    #Existe un partido con estos datos, se anade a la lista
                                    lista_partidos.append(partido_comp.first())
                                else:
                                    #Se crea el partido
                                    partido = Partido.objects.create(
                                        fecha = fecha, pista = pista, franja_horaria = fh, creado_por = perfil, visible = settings.ESTADO_NO
                                    )
                                    lista_partidos.append(partido)

                            #Se actualiza el mapa de partidos en franjas horarias
                            mapa_franjas_partidos[fh] = lista_partidos

                        data["mapa_franjas_partidos"] = mapa_franjas_partidos

                    else:
                        error = "No existen pistas para el deporte que has seleccionado"

                #Se ha pulsado sobre terminar, se eliminan partidos sin jugadores
                elif accion == "terminar":
                    partidos = Partido.objects.filter(pista__club = club, fecha = fecha)
                    for p in partidos:
                        if len(p.perfiles.all()) == 0:
                            p.delete()
                        else:
                            #Generar notificaciones a jugadores
                            generarNotificacionesPartidoPerfiles(p)

                    success = "Se ha guardado su planificación, puede verla en la página principal."

        except Exception, e:
            logger.debug("administracion/partidos - Método planificar. " + e.message)
            error = "Ha habido un error en el proceso que acaba de ejecutar"


        data["error"] = error
        data["success"] = success

    return render_to_response(ruta_administracion_planificar, data, context_instance=RequestContext(request))

#****************************************************************************************************
#FUNCIONES AUXILIARES
#****************************************************************************************************

def comprueba_pista_disponible(franja_horaria_id, pista_id, fecha):
    disponible = True
    if Partido.objects.filter(pista__id = pista_id, fecha__startswith=fecha, franja_horaria__id = franja_horaria_id).exists():
        disponible = False
    return disponible



#****************************************************************************************************
#FUNCIONES AJAX
#****************************************************************************************************

@login_required()
def comprueba_disponibilidad_partido_ajax(request):

    disponible = False
    if request.POST.get("fecha"):
        fecha = datetime.strptime(request.POST.get("fecha"), '%d/%m/%Y').date()
        id_pista = request.POST.get("pista")
        id_franja_hora = request.POST.get("franja_horaria")
        club_id = request.POST.get("club")
        disponible = True

        if id_pista and id_franja_hora and club_id:
            if Partido.objects.filter(pista__id = id_pista, fecha__startswith=fecha, franja_horaria__id = id_franja_hora, pista__club__id=club_id).exists():
                disponible = False

    data = {'disponible':disponible}
    return HttpResponse(json.dumps(data))

@login_required()
def crear_partido_ajax(request):
    error = ""
    titulo = "Nuevo partido en SportClick"
    if request.method == "POST":
        try:
            nuevo_partido = None
            fh = None
            fecha_partido = None
            error = ""
            jugadores = []
            max_jugadores = 0
            partidos_perfiles = []
            if request.POST.get("fecha") and request.POST.get("hora") and request.POST.get("pista") and request.POST.get("user") and request.POST.get("visible") and request.POST.get("notificar"):

                try:
                    creado_por = Perfil.objects.get(user__id = request.POST["user"])
                    fh = FranjaHora.objects.get(id=request.POST["hora"])
                    fecha_partido = datetime.strptime(request.POST["fecha"], '%d/%m/%Y').date()
                    pista_partido = Pista.objects.get(id=request.POST["pista"])
                    visible = bool(int(request.POST.get("visible")))
                    notificar = bool(int(request.POST.get("notificar")))
                    nuevo_partido = Partido(creado_por = creado_por, franja_horaria = fh, fecha = fecha_partido, pista = pista_partido, visible=visible)

                    if comprueba_pista_disponible(fh.id, pista_partido.id, fecha_partido):
                        #Actualizar valor max_jugadores
                        max_jugadores = pista_partido.deporte.num_jugadores
                    else:
                        error = "La pista seleccionada no está disponible"

                except FranjaHora.DoesNotExist, e:
                    logger.debug("administracion/partidos - Método crear_partido_ajax. " + e)
                    error = "¡Ups! Ha habido un error al crear el partido"
                except Pista.DoesNotExist, e:
                    logger.debug("administracion/partidos - Método crear_partido_ajax. " + e)
                    error = "¡Ups! Ha habido un error al crear el partido"

                if error == "" and len(jugadores) <= max_jugadores and nuevo_partido.fecha != "" and nuevo_partido.franja_horaria is not None:
                    nuevo_partido.save()

                    #Una vez guardado el partido, se guardan los jugadores
                    if max_jugadores != 0 and error == "":
                        for i in range(1,max_jugadores+1):
                            id = request.POST["jugador"+str(i)]
                            if id != "":
                                try:
                                    jugador = Perfil.objects.get(id=id)
                                    partido_perfil = Partido_perfiles.objects.create(
                                        partido = nuevo_partido,
                                        perfil = jugador
                                    )
                                    partido_perfil.save()
                                    jugadores.append(jugador)
                                except Perfil.DoesNotExist, e:
                                    logger.debug("administracion/partidos - Método crear_partido_ajax. " + e.message)
                                    error = "¡Ups! Ha habido un error al crear el partido."
                                except Exception, e:
                                    logger.debug("administracion/partidos - Método crear_partido_ajax. " + e.message)
                                    error = "¡Ups! Ha habido un error al crear el partido."

                    error = "OK"
                else:
                    if error == "":
                        logger.debug("administracion/partidos - Método crear_partido_ajax. ")
                        error = "¡Ups! ha habido un error al crear el partido"

                #Si es necesario, se envian emails
                try:
                    if notificar and len(jugadores) > 0 and error == "OK":
                        for jugador in jugadores:
                            texto = plantilla_email_partido(jugador.user.first_name, nuevo_partido)
                            if not enviar_email(titulo, settings.EMAIL_HOST_USER, jugador.user.email, texto):
                                error = "Se ha creado el partido correctamente, pero no se han podido enviar las notificaciones"
                except Exception, e:
                    error = "Se ha creado el partido correctamente, pero no se han podido enviar las notificaciones"


                #Se generan notificaciones a los perfiles
                generarNotificacionesPartidoPerfiles(nuevo_partido)

            else:
                error = "Debe seleccionar, fecha, hora y pista."

        except Exception:
            error = "¡Ups! Ha habido un error al crear el partido"

        data = {'error':error}
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseRedirect("/")

@login_required()
def editar_partido_ajax(request):
    error = ""
    titulo = "Modificación de partido en SportClick"

    if request.method == "POST":

        try:
            partido = None
            fh = None
            fecha_partido = None
            error = ""
            jugadores = []
            max_jugadores = 0
            notificar = None

            if request.POST["partido_id"] and request.POST["fecha"] and request.POST["hora"] and request.POST["pista"] and request.POST["user"] and request.POST["visible"] and request.POST.get("notificar"):

                try:
                    partido = Partido.objects.get(id=request.POST["partido_id"])
                    fh = FranjaHora.objects.get(id=request.POST["hora"])
                    fecha_partido = datetime.strptime(request.POST["fecha"], '%d/%m/%Y').date()
                    pista_partido = Pista.objects.get(id=request.POST["pista"])
                    visible = bool(request.POST["visible"])
                    notificar = bool(int(request.POST.get("notificar")))
                    if pista_partido.id != partido.pista.id:
                        if comprueba_pista_disponible(fh.id, pista_partido.id, fecha_partido):
                            #Actualizar valor max_jugadores
                            max_jugadores = pista_partido.deporte.num_jugadores
                        else:
                            error = "La pista seleccionada no está disponible"
                    else:
                        max_jugadores = pista_partido.deporte.num_jugadores

                except Partido.DoesNotExist, e:
                    logger.debug("administracion/partidos - Método editar_partido_ajax. " + e.message)
                    error = "¡Ups! Ha habido un error al crear el partido"
                except FranjaHora.DoesNotExist, e:
                    logger.debug("administracion/partidos - Método editar_partido_ajax. " + e.message)
                    error = "¡Ups! Ha habido un error al crear el partido"
                except Pista.DoesNotExist, e:
                    logger.debug("administracion/partidos - Método editar_partido_ajax. " + e.message)
                    error = "¡Ups! Ha habido un error al crear el partido"
                if max_jugadores != 0 and error == "":
                    partido.franja_horaria = fh
                    partido.pista = pista_partido
                    partido.fecha = fecha_partido
                    partido.visible = visible

                    #Eliminamos todos los jugadores y vamos anadiendo
                    Partido_perfiles.objects.filter(partido = partido).delete()

                    for i in range(1,max_jugadores+1):
                        id = request.POST["jugador"+str(i)]
                        if id != "":
                            try:
                                jugador = Perfil.objects.get(id=id)
                                if not jugador in partido.perfiles.all():
                                    partido_perfil = Partido_perfiles(
                                        partido = partido,
                                        perfil = jugador
                                    )
                                    partido_perfil.save()
                                jugadores.append(jugador)

                            except Perfil.DoesNotExist, e:
                                logger.debug("administracion/partidos - Método editar_partido_ajax. " + e.message)
                                error = "¡Ups! Ha habido un error al crear el partido."

                if error == "" and len(jugadores) <= max_jugadores and partido.fecha != "" and partido.franja_horaria is not None:
                    partido.save()
                    error = "OK"

                    #Se generan notificaciones a los perfiles
                    generarNotificacionesPartidoPerfiles(partido)

                else:
                    if error == "":
                        logger.debug("administracion/partidos - Método editar_partido_ajax. ")
                        error = "¡Ups! ha habido un error al crear el partido"
            else:
                error = "Debe seleccionar, fecha, hora y pista."

            #Si es necesario, se envian notificaciones
            try:
                if notificar and len(jugadores) > 0 and error == "OK":
                    for jugador in jugadores:
                        texto = plantilla_email_editar_partido(jugador.user.first_name, partido)
                        if not enviar_email(titulo, settings.EMAIL_HOST_USER, jugador.user.email, texto):
                            error = "Se ha creado el partido correctamente, pero no se han podido enviar las notificaciones"
            except Exception, e:
                error = "Se ha creado el partido correctamente, pero no se han podido enviar las notificaciones"
        except Exception, e:
            logger.debug("administracion/partidos - Método editar_partido_ajax. " + e.message)
            error = "¡Ups! ha habido un error al guardar el partido"

        data = {'error':error}
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseRedirect("/")


# Planificar partido: Guardar
@login_required()
def guardar_partido_planificar(request):

    jugador_texto = "jugador_"
    error = None

    try:
        if request.method == "POST":
            partido_id = request.POST.get("partido_id")

            if partido_id:

                partido = Partido.objects.get(id = partido_id)

                if partido:

                    #Eliminamos todos los jugadores y vamos anadiendo
                    Partido_perfiles.objects.filter(partido = partido).delete()

                    #Recorremos el mapa de request.POST en busca de jugadores.
                    for clave in request.POST:

                        #Si contiene la palabra jugador_, significa que es un jugador, y se anade al partido
                        if jugador_texto in clave:
                            perfil = Perfil.objects.get(id = int(request.POST.get(clave)))
                            partido_perfil = Partido_perfiles.objects.create(
                                partido = partido,
                                perfil = perfil
                            )

    except Exception, e:
        logger.debug("administracion/partidos - Método guardar_partido_planificar. " + e.message)
        error = "¡Ups! ha habido un error al guardar el partido"

    data = {'error':error}
    return HttpResponse(json.dumps(data))