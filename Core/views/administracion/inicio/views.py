# -*- encoding: utf-8 -*-
from Core.utils import *
from django.db.models import *
from datetime import date,datetime
from django.conf import settings
from django.db.models import Q
import logging
from django.contrib.auth.decorators import login_required
from Core.utils import cargar_tipos_notificaciones_settings

#Instancia del log
logger = logging.getLogger(__name__)

ruta_pagina_principal = 'administracion/inicio/pagina_principal.html'
ruta_imprimir_planificacion = 'administracion/inicio/imprimir.html'

@login_required()
def perfil_administrador(request, id_usuario):

    perfil = comprueba_usuario_administrador(id_usuario, request)

    #Esto solo se hace en la pagina principal
    #Cargamos datos en sesion, si fuera necesario

    #Guardamos en sesion una lista de pares {nombre_club, club_id} en los que el jugador es administrador, nos quedamos con el primero para que sea el inicial en mostrarse:
    if not "nombre_club_id" in request.session or not "club_id" in request.session:
        clubes_administrador = Club.objects.filter(
            id__in = PerfilRolClub.objects.values_list('club_id', flat=True).filter(perfil = perfil, rol_id = settings.ROL_ADMINISTRADOR)
        ).order_by('nombre')

        es_primer_club = True
        club_id = None
        nombre_club_id = {}
        for c in clubes_administrador:
            if es_primer_club:
                club_id = c.id
                es_primer_club = False
            nombre_club_id[c.nombre] = c.id

        request.session["club_id"] = club_id
        request.session["nombre_club_id"] = nombre_club_id
    else:
        club_id = request.session["club_id"]

    club = Club.objects.get(id = club_id)

    try:
        rutaTiempo = ""#RutaTiempo.objects.get(municipio=club.municipio)
    except Exception:
        rutaTiempo = ""

    num_jugadores = PerfilRolClub.objects.filter(club = club, perfil__user__is_active = True).count()

    num_partidos_hoy = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(pista__club=club, fecha__startswith=date.today(), num_perfiles=4).count()

    num_partidos_abiertos_hoy = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(
        fecha__startswith=date.today(), num_perfiles__lt=4, num_perfiles__gt=0, pista__in=Pista.objects.filter(club=club)).count()

    if request.method == "POST":
        franja_horaria_id = request.POST.get('franja_horaria')
        if franja_horaria_id:
            franja_horaria_actual = FranjaHora.objects.get(id = franja_horaria_id)
        else:
            franja_horaria_actual = FranjaHora.objects.filter(club = club, inicio__lt=datetime.now().time(), fin__gt=datetime.now().time()).first()
    else:
        franja_horaria_actual = FranjaHora.objects.filter(club = club, inicio__lt=datetime.now().time(), fin__gt=datetime.now().time()).first()

    #Sacamos franjas horarias para el listado
    franjas_horarias = FranjaHora.objects.filter(club = club).order_by('inicio')

    if franja_horaria_actual:
        num_partidos_en_juego = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(
            pista__in=Pista.objects.filter(club=club),
            franja_horaria=franja_horaria_actual,
            num_perfiles=4,
            fecha=date.today()).count()
    else:
        num_partidos_en_juego = 0
        franja_horaria_actual = FranjaHora.objects.filter(club = club).order_by('inicio').first()
    #Partidos de la franja horaria
    partidos_ahora = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(
        pista__in = Pista.objects.filter(club=club), franja_horaria=franja_horaria_actual,
        num_perfiles = 4
    )
    pistas = Pista.objects.filter(club = club).order_by("deporte", "orden", "nombre")
    #Pistas y partidos de la franja horaria
    pistas_partidos = {}
    for p in pistas:
        try:
            partido = Partido.objects.get(pista = p, franja_horaria = franja_horaria_actual, fecha__startswith=date.today())
            pistas_partidos[p] = partido
        except Partido.DoesNotExist:
            pistas_partidos[p] = ""

    #Notificaciones
    try:
        campos_fijos_query = Q(estado = settings.ESTADO_NULL, tipo__in = (settings.TIPO_NOTIF_UNIRSE_A_PARTIDO, settings.TIPO_NOTIF_INSCRIPCION_CLUB),
                               destino=settings.NOTIF_CLUB, leido = settings.ESTADO_NO)
        notificaciones = Notificacion.objects.filter(
            (Q(club = club) | Q(partido__pista__club = club)) & campos_fijos_query
        ).order_by("-fecha")

    except Exception:
        notificaciones = []

    municipio_guiones = separa_guiones(club.municipio.municipio)

    data = {'perfil':perfil, 'club':club, 'num_jugadores':num_jugadores, 'num_partidos_hoy':num_partidos_hoy,
            'num_partidos_abiertos_hoy':num_partidos_abiertos_hoy,
            'num_partidos_en_juego':num_partidos_en_juego, 'franja_horaria_actual':franja_horaria_actual,
            'pistas_partidos':pistas_partidos, 'pistas':pistas,
            'rutaTiempo':rutaTiempo, 'notificaciones':notificaciones,
            'franjas_horarias':franjas_horarias, 'municipio_guiones':municipio_guiones
    }

    data = cargar_tipos_notificaciones_settings(data)

    return render_to_response(ruta_pagina_principal, data, context_instance=RequestContext(request))



#Vista que intercambia el club que esta vigente en sesion
@login_required()
def cambio_club_administrador(request, id_usuario, club_id):

    request.session["club_id"] = club_id

    return HttpResponseRedirect("/administrador/"+id_usuario)


def separa_guiones(cadena):
    res = ""
    split_cadena = cadena.split(" ")
    for index, s in enumerate(split_cadena):
        res += s
        if index != len(split_cadena)-1:
            res += "-"

    return res

def separa_comas(lista_perfiles):
    res = ""
    if len(lista_perfiles) > 0:
        cont = 0
        for user in lista_perfiles:
            if cont != 0:
                res = res + ", "
            res = res + str(user)
            cont = cont + 1

    return res


#Imprimir planificacion diaria
@login_required()
def imprimir_planificacion(request, club_id):

    mapa_franjas_pista = {}
    mapa_pista_partido = {}
    data = {}

    try:
        hoy = date.today()
        pistas = Pista.objects.filter(club__id = club_id).order_by("orden")
        franjas = FranjaHora.objects.filter(club__id = club_id).order_by("inicio")

        for fh in franjas.all():
            mapa_pista_partido = {}
            for pista in pistas.all():

                try:
                    #Se busca partido de esa pista y esa FH
                    partido = Partido.objects.filter(fecha = hoy, franja_horaria__id = fh.id, pista__id = pista.id)[:1].get()
                    perfiles = []
                    for perfil in partido.perfiles.all():
                        perfiles.append(perfil.user.username)
                except Partido.DoesNotExist:
                    partido = None
                    perfiles = []

                #Se actualiza el mapa de pista y partido
                mapa_pista_partido[pista] = separa_comas(perfiles)

            #Para cada franja horaria, se actualizan las pistas
            mapa_franjas_pista[fh] = mapa_pista_partido

            data["mapa_franjas_pistas"] = mapa_franjas_pista

    except Exception, e:
        error = "Ha habido un error al imprimir la planificación"
        data["error"] = error

    data["hoy"] = hoy

    return render_to_response(ruta_imprimir_planificacion, data, context_instance=RequestContext(request))