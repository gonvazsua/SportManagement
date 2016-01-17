# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from datetime import date,datetime
import json
import logging
from django.contrib.auth.decorators import login_required

#Instancia del log
logger = logging.getLogger(__name__)

ruta_administracion_nuevo_partido = 'administracion/partidos/nuevo_partido.html'
ruta_administracion_editar_partido = 'administracion/partidos/editar_partido.html'
ruta_administracion_buscador_partidos = 'administracion/partidos/buscador_partidos.html'
ruta_administracion_ver_partido = 'administracion/partidos/ver_partido.html'

@login_required()
def administrador_crear_partido(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=1))
    error = ""
    pistas = Pista.objects.filter(club=club).order_by('deporte__deporte', 'orden')

    #Recogemos posibles parámetros en caso de que vengan en la URL
    pista = ""
    franja_horaria = ""
    if "pista_id" in  request.GET and "fh_id" in request.GET:
        pista = int(request.GET["pista_id"])
        franja_horaria = int(request.GET["fh_id"])

    franjas_horarias = FranjaHora.objects.filter(club = club)
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
                        jugadores = PerfilRolClub.objects.filter(club = club).exclude(perfil__in = list(jug_no_disponibles))
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
    perfil = comprueba_usuario_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=1))
    partido = ""
    error = ""
    try:
        partido = Partido.objects.get(id=id_partido)
    except Partido.DoesNotExist:
        logger.debug("administracion/partidos - Método administrador_editar_partido - id_usuario " + str(id_usuario) + ", id_partido " + str(id_partido))
        error = "Ha habido un error al editar el partido."
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
    jugadores = PerfilRolClub.objects.filter(club = club).exclude(perfil__in = list(jug_no_disponibles)).order_by("perfil__user__last_name")

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

    data = {
        'perfil':perfil, 'error':error, 'partido':partido, 'club':club, 'pistas':pistas, 'franjas_horarias':franjas_horarias, 'jugadores':jugadores,
        'map_jugadores':map_jugadores, "niveles" : niveles, 'ids_jugadores_seleccionados':ids_jugadores_seleccionados
    }
    return render_to_response(ruta_administracion_editar_partido, data, context_instance=RequestContext(request))

@login_required()
def buscador_partidos(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=1))
    franjas_horarias = FranjaHora.objects.filter(club = club)
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
    fecha = datetime.strptime(request.POST["fecha"], '%d/%m/%Y').date()
    id_pista = request.POST["pista"]
    id_franja_hora = request.POST["franja_horaria"]
    club_id = request.POST["club"]
    disponible = True
    if Partido.objects.filter(pista__id = id_pista, fecha__startswith=fecha, franja_horaria__id = id_franja_hora, pista__club__id=club_id).exists():
        disponible = False
    data = {'disponible':disponible}
    return HttpResponse(json.dumps(data))

@login_required()
def crear_partido_ajax(request):
    error = ""
    if request.method == "POST":
        nuevo_partido = None
        fh = None
        fecha_partido = None
        error = ""
        jugadores = []
        max_jugadores = 0
        if request.POST.get("fecha") and request.POST.get("hora") and request.POST.get("pista") and request.POST.get("user") and request.POST.get("visible"):

            try:
                creado_por = Perfil.objects.get(user__id = request.POST["user"])
                fh = FranjaHora.objects.get(id=request.POST["hora"])
                fecha_partido = datetime.strptime(request.POST["fecha"], '%d/%m/%Y').date()
                pista_partido = Pista.objects.get(id=request.POST["pista"])
                visible = bool(request.POST.get("visible"))
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
            if max_jugadores != 0 and error == "":
                for i in range(1,max_jugadores+1):
                    id = request.POST["jugador"+str(i)]
                    if id != "":
                        try:
                            jugador = Perfil.objects.get(id=id)
                            jugadores.append(jugador)
                        except Perfil.DoesNotExist, e:
                            logger.debug("administracion/partidos - Método crear_partido_ajax. " + e)
                            error = "¡Ups! Ha habido un error al crear el partido."

            if error == "" and len(jugadores) <= max_jugadores and nuevo_partido.fecha != "" and nuevo_partido.franja_horaria is not None:
                nuevo_partido.save()
                if len(jugadores) >= 1:
                    nuevo_partido.perfiles = jugadores
                    nuevo_partido.save()
                error = "OK"
            else:
                if error == "":
                    logger.debug("administracion/partidos - Método crear_partido_ajax. ")
                    error = "¡Ups! ha habido un error al crear el partido"
        else:
            error = "Debe seleccionar, fecha, hora y pista."
        data = {'error':error}
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseRedirect("/")

@login_required()
def editar_partido_ajax(request):
    error = ""
    if request.method == "POST":
        partido = None
        fh = None
        fecha_partido = None
        error = ""
        jugadores = []
        max_jugadores = 0
        if request.POST["partido_id"] and request.POST["fecha"] and request.POST["hora"] and request.POST["pista"] and request.POST["user"] and request.POST["visible"]:

            try:
                partido = Partido.objects.get(id=request.POST["partido_id"])
                fh = FranjaHora.objects.get(id=request.POST["hora"])
                fecha_partido = datetime.strptime(request.POST["fecha"], '%d/%m/%Y').date()
                pista_partido = Pista.objects.get(id=request.POST["pista"])
                visible = bool(request.POST["visible"])
                if pista_partido.id != partido.pista.id:
                    if comprueba_pista_disponible(fh.id, pista_partido.id, fecha_partido):
                        #Actualizar valor max_jugadores
                        max_jugadores = pista_partido.deporte.num_jugadores
                    else:
                        error = "La pista seleccionada no está disponible"

            except Partido.DoesNotExist, e:
                logger.debug("administracion/partidos - Método editar_partido_ajax. " + e)
                error = "¡Ups! Ha habido un error al crear el partido"
            except FranjaHora.DoesNotExist, e:
                logger.debug("administracion/partidos - Método editar_partido_ajax. " + e)
                error = "¡Ups! Ha habido un error al crear el partido"
            except Pista.DoesNotExist, e:
                logger.debug("administracion/partidos - Método editar_partido_ajax. " + e)
                error = "¡Ups! Ha habido un error al crear el partido"
            if max_jugadores != 0 and error == "":
                partido.franja_horaria = fh
                partido.pista = pista_partido
                partido.fecha = fecha_partido
                partido.visible = visible
                for i in range(1,max_jugadores+1):
                    id = request.POST["jugador"+str(i)]
                    if id != "":
                        try:
                            jugador = Perfil.objects.get(id=id)
                            jugadores.append(jugador)
                        except Perfil.DoesNotExist, e:
                            logger.debug("administracion/partidos - Método editar_partido_ajax. " + e)
                            error = "¡Ups! Ha habido un error al crear el partido."

            if error == "" and len(jugadores) <= 4 and len(jugadores) >= 1 and partido.fecha != "" and partido.franja_horaria is not None:
                partido.save()
                partido.perfiles = jugadores
                partido.save()
                error = "OK"
            else:
                if error == "":
                    logger.debug("administracion/partidos - Método editar_partido_ajax. ")
                    error = "¡Ups! ha habido un error al crear el partido"
        else:
            error = "Debe seleccionar, fecha, hora y pista."
        data = {'error':error}
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseRedirect("/")