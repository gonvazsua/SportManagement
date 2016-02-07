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

#Instancia del log
logger = logging.getLogger(__name__)

#Rutas de la vista
ruta_administracion_club = "administracion/configuracion/administracion_club.html"

@login_required()
def administracion_club(request, id_usuario):
    municipio = ""
    provincia = ""
    form_admin_club = FormAdministracionClub()
    perfil = comprueba_usuario_administrador(id_usuario)
    club = obtener_club_de_sesion_administrador(request.session.get("club_id", None), perfil.id)
    provincias = Provincias.objects.all()
    try:
        if perfil.municipio != "" and perfil.municipio != None:
            municipio = Municipios.objects.get(id=perfil.municipio.id)
            provincia = Provincias.objects.get(id = municipio.provincia.id)
            municipios = Municipios.objects.filter(provincia = perfil.municipio.provincia)
        else:
            municipios = Municipios.objects.all()
    except Exception:
        municipios = []
        provincia = None
        municipio = None
        logger.debug("administracion/administracion - Método administracion_club: id_usuario " + str(id_usuario))

    franjas_horarias = FranjaHora.objects.filter(club = club).order_by("inicio")
    niveles_juego = Nivel.objects.filter(club=club).order_by('deporte__deporte')
    pistas = Pista.objects.filter(club=club).order_by('deporte__deporte', 'orden')
    deportes = Deporte.objects.all()
    horas = cargar_horas()
    minutos = cargar_minutos()
    data = {'perfil':perfil, 'club':club, 'form_admin_club':form_admin_club, 'provincias':provincias, 'municipio':municipio, 'pistas':pistas,
            'provincia':provincia, 'municipios':municipios, 'franjas_horarias':franjas_horarias, 'niveles_juego':niveles_juego,
            'deportes':deportes, 'horas':horas, 'minutos':minutos
    }
    return render_to_response(ruta_administracion_club, data, context_instance=RequestContext(request))

@login_required()
def guardar_administracion(request):
    id_usuario = request.POST.get('user_id')
    accion = request.POST.get('action')
    club_id=request.POST.get('club_id')
    club = Club.objects.get(id=club_id)
    error = ""
    if accion == "club":
        club.nombre = request.POST['nombre']
        club.direccion = request.POST['direccion']
        try:
            municipio = Municipios.objects.get(id=request.POST['municipio'])
            club.municipio = municipio
        except Municipios.DoesNotExist:
            return administracion_club(request, id_usuario)
        except Exception:
            logger.debug("administracion/administracion - Método guardar_administracion: id_usuario " + str(id_usuario) + ", accion: " + accion)
        club.descripcion = request.POST['descripcion']
        if request.FILES.get("imagen"):
            if not club.imagen == "":
                borrar_imagen_anterior(club.imagen.path)
            club.imagen = request.FILES.get("imagen")
        club.save()

    elif accion == "deporte":
        if not request.POST["deporte"] == "" and not request.POST["num_jugadores"] == "":
            new_deporte = Deporte.objects.create(deporte=request.POST["deporte"], num_jugadores = request.POST["num_jugadores"])
            new_deporte.save();

    elif accion == "pistas":
        ids_eliminados = request.POST["ids_pistas_eliminadas"]
        array_ids_eliminados = []
        if ids_eliminados != "":
            array_ids_eliminados = ids_eliminados.split(",", 1)
            for id in array_ids_eliminados:
                try:
                    #Borrar partidos asociados
                    try:
                        partidos_pistas = Partido.objects.filter(pista__id = id)
                    except Partido.DoesNotExist, e:
                        logger.debug("administracion/administracion - Método guardar_administracion: id_usuario " + str(id_usuario) + ", accion: " + accion + ". " + e)
                    for pp in partidos_pistas:
                        pp.delete()
                    p = Pista.objects.get(id = id)
                    p.delete()
                except Pista.DoesNotExist:
                    error = "No encontrada pista"
                except Exception, e:
                    logger.debug("administracion/administracion - Método guardar_administracion: id_usuario " + str(id_usuario) + ", accion: " + accion + ". " + e)
        if not request.POST["pista_orden"] == "" and not request.POST["pista_deporte"] == "" and not request.POST["pista_nombre"] == "":
            d = Deporte.objects.get(id=request.POST["pista_deporte"])
            new_p = Pista.objects.create(club = club, deporte=d, nombre = request.POST["pista_nombre"], orden = request.POST["pista_orden"])
            new_p.save();
    return administracion_club(request, id_usuario)



#****************************************************************************************************
#FUNCIONES AJAX
#****************************************************************************************************

@login_required()
def municipios_ajax(request):
    try:
        id_provincia = request.GET['provincia_id']
        municipios = Municipios.objects.filter(provincia__id = id_provincia)
    except Exception:
        municipios = {}
        logger.debug("administracion/administracion - Método municipios_ajax")
    data = serializers.serialize('json', municipios,
        fields=('id', 'municipio'))
    return HttpResponse(data, mimetype='application/json')

@login_required()
def guardar_franja_horaria_ajax(request):
    error = None
    try:
        fh_id = request.POST.get("fh_id")
        club_id = request.POST.get("club_id")
        accion = request.POST.get("action")
        if club_id and accion:

            if accion == "eliminar":
                if fh_id:
                    fh_eliminar = FranjaHora.objects.get(id=fh_id)
                    fh_eliminar.delete()
                else:
                    error = "Ha habido un error al borrar la franja horaria"
            else:
                if fh_id:
                    inicio_horas = request.POST.get("inicio_horas_"+fh_id)
                    inicio_minutos = request.POST.get("inicio_minutos_"+fh_id)
                    fin_horas = request.POST.get("fin_horas_"+fh_id)
                    fin_minutos = request.POST.get("fin_minutos_"+fh_id)
                else:
                    inicio_horas = request.POST.get("inicio_horas")
                    inicio_minutos = request.POST.get("inicio_minutos")
                    fin_horas = request.POST.get("fin_horas")
                    fin_minutos = request.POST.get("fin_minutos")

                inicio = None
                fin = None

                if es_inicio_menor_que_fin(inicio_horas, inicio_minutos, fin_horas, fin_minutos):
                    fin = fin_horas + ":" + fin_minutos
                    inicio = inicio_horas + ":" + inicio_minutos
                else:
                    error = "La hora de inicio no puede ser mayor que la hora de fin"

                if not error and inicio and fin:
                    if fh_id and accion == "editar":
                        franja_horaria_editar = FranjaHora.objects.filter(id=fh_id).update(inicio=inicio, fin=fin)
                    elif not fh_id and accion == "nuevo":
                        club = Club.objects.get(id=club_id)
                        franja_horaria_nueva = FranjaHora.objects.create(club = club, inicio=inicio, fin=fin)
                        franja_horaria_nueva.save()

        else:
            error = "Ha habido un error al guardar la franja horaria"
    except Exception, e:
        error = "Ha habido un error al guardar la franja horaria"
        logger.debug("administracion/administracion - Método guardar_franja_horaria_ajax: ")

    data = {'error':error}
    return HttpResponse(json.dumps(data))

@login_required()
def guardar_niveles_juego_ajax(request):
    error = None
    try:
        nj_id = request.POST.get("nj_id")
        club_id = request.POST.get("club_id")
        accion = request.POST.get("action")
        if club_id and accion:

            if accion == "eliminar":
                if nj_id:
                    nj_eliminar = Nivel.objects.get(id=nj_id)
                    nj_eliminar.delete()
                else:
                    error = "Ha habido un error al borrar el nivel de juego"
            else:
                #Viene de editar
                if nj_id:
                    nj_deporte = request.POST.get("nj_deporte_"+nj_id)
                    nj_nivel = request.POST.get("nj_nivel_"+nj_id)
                else:
                #Es un objeto nuevo
                    nj_deporte = request.POST.get("nj_deporte")
                    nj_nivel = request.POST.get("nj_nivel")

                if nj_id and accion == "editar":
                    deporte = Deporte.objects.get(id=nj_deporte)
                    nivel_juego_editar = Nivel.objects.filter(id=nj_id).update(deporte = deporte, nivel=nj_nivel)
                elif not nj_id and accion == "nuevo":
                    club = Club.objects.get(id=club_id)
                    deporte = Deporte.objects.get(id=nj_deporte)
                    nivel_juego_nuevo = Nivel.objects.create(club = club, deporte = deporte, nivel=nj_nivel)
                    nivel_juego_nuevo.save()
                else:
                    error = "Ha habido un error al guardar el nivel de juego"

        else:
            error = "Ha habido un error al guardar el nivel de juego"
    except Exception, e:
        error = "Ha habido un error al guardar el nivel de juego"
        logger.debug("administracion/administracion - Método guardar_nivel_juego_ajax: ")

    data = {'error':error}
    return HttpResponse(json.dumps(data))

@login_required()
def guardar_pistas_ajax(request):
    error = None
    try:
        pista_id = request.POST.get("pista_id")
        club_id = request.POST.get("club_id")
        accion = request.POST.get("action")
        if club_id and accion:

            if accion == "eliminar":
                if pista_id:
                    pista_eliminar = Pista.objects.get(id=pista_id)
                    pista_eliminar.delete()
                else:
                    error = "Ha habido un error al borrar la pista"
            else:
                #Viene de editar
                if pista_id:
                    pista_orden = request.POST.get("pista_orden_"+pista_id)
                    pista_deporte = request.POST.get("pista_deporte_"+pista_id)
                    pista_nombre = request.POST.get("pista_nombre_"+pista_id)
                else:
                #Es un objeto nuevo
                    pista_orden = request.POST.get("pista_orden")
                    pista_deporte = request.POST.get("pista_deporte")
                    pista_nombre = request.POST.get("pista_nombre")

                if pista_id and accion == "editar":
                    deporte = Deporte.objects.get(id=pista_deporte)
                    pista_editar = Pista.objects.filter(id=pista_id).update(deporte = deporte, orden = pista_orden, nombre = pista_nombre)
                elif not pista_id and accion == "nuevo":
                    club = Club.objects.get(id=club_id)
                    deporte = Deporte.objects.get(id=pista_deporte)
                    pista_nueva = Pista.objects.create(club = club, deporte = deporte, orden = pista_orden, nombre = pista_nombre)
                    pista_nueva.save()
                else:
                    error = "Ha habido un error al guardar la pista"

        else:
            error = "Ha habido un error al guardar la pista"
    except Exception, e:
        error = "Ha habido un error al guardar la pista"
        logger.debug("administracion/administracion - Método guardar_pista_ajax: ")

    data = {'error':error}
    return HttpResponse(json.dumps(data))


#****************************************************************************************************
#FUNCIONES AUXILIARES
#****************************************************************************************************

def borrar_imagen_anterior(url_imagen):
    try:
        if os.path.isfile(url_imagen):
            os.remove(url_imagen)
    except Exception:
        print "Imagen no encontrada:" +url_imagen
        logger.debug("administracion/administracion - Método borrar_imagen_anterior url: " + url_imagen)

def cargar_horas():
    horas = range(0, 24)
    return horas

def cargar_minutos():
    return range(0, 60, 5)

def es_inicio_menor_que_fin(inicio_horas, inicio_minutos, fin_horas, fin_minutos):
    esMenor = True
    try:
        ih = int(inicio_horas)
        im = int(inicio_minutos)
        fh = int(fin_horas)
        fm = int(fin_minutos)
        if ih > fh and (ih <= 23 and fh >= 2):
            esMenor = False
        elif ih >= fh  and (ih <= 23 and fh >= 2):
            if im > fm:
                esMenor = False
        else:
            esMenor = True
    except Exception, e:
        logger.debug("administracion/administracion - Método es_inicio_menor_que_fin")
    return esMenor