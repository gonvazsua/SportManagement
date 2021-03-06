# -*- encoding: utf-8 -*-
from argparse import _ActionsContainer
from Core.views import *
from Core.utils import *
from datetime import date,datetime
import json
import logging
from django.contrib.auth.decorators import login_required

#Instancia del log
logger = logging.getLogger(__name__)

ruta_partido_usuarios = 'usuarios/partidos/usuarios_partido.html'
ruta_mis_partidos_usuarios = 'usuarios/partidos/usuarios_mis_partidos.html'
ruta_buscador_partidos_usuarios = 'usuarios/partidos/usuarios_buscador_partidos.html'

@login_required()
def usuario_partido(request, id_usuario, id_partido):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario, request)
    if perfil == None:
        return HttpResponseRedirect("/")

    bloqueo_usuario = False
    bloqueo_notificaciones = False
    try:
        partido = Partido.objects.get(id=id_partido)

        if(not esPartidoDeClubDeUsuario(perfil, partido)):
            return HttpResponseRedirect("/")

        #comprobar si tiene notificaciones de partidos asociadas y marcarlas como leidas
        try:
            notificaciones = []
            if not bloqueo_notificaciones:

                notificaciones = Notificacion.objects.filter(
                    tipo = settings.TIPO_NOTIF_UNIRSE_A_PARTIDO,
                    jugador = perfil,
                    partido = partido,
                    destino = settings.NOTIF_JUGADOR
                ).update(leido = settings.ESTADO_SI)

        except Exception:
            notificaciones = []

        nivel_medio = calcular_nivel_medio(partido)
        if perfil in partido.perfiles.all():
            bloqueo_usuario = True

        if notificaciones > 0:
            bloqueo_notificaciones = True

        comentarios = ComentarioPartido.objects.filter(partido = partido).order_by("-fecha")[:30]

    except Exception:
        partido = None
        nivel_medio = ""

    data = {'perfil': perfil, 'partido':partido, 'nivel_medio':nivel_medio, 'bloqueo_usuario':bloqueo_usuario, 'bloqueo_notificaciones':bloqueo_notificaciones,
            'comentarios':comentarios}

    #Establecer direccion de retorno
    if request.method == "GET":
        origen = request.GET.get("origen")
        if origen == "partidos":
            retorno = "/usuario/"+str(perfil.user.id)+"/partidos"
            data["retorno"] = retorno
            data["texto_retorno"] = "Mis partidos"
        elif origen == "buscador":
            #Valores del buscador
            id_club = request.GET.get("id_club")
            id_fh = request.GET.get("id_fh")
            fecha = request.GET.get("fecha")

            retorno = "/usuario/"+str(perfil.user.id)+"/partidos/buscador?id_club="+str(id_club)+"&id_fh="+str(id_fh)+"&fecha="+str(fecha)
            data["retorno"] = retorno
            data["texto_retorno"] = "Buscador de partidos"

    return render_to_response(ruta_partido_usuarios, data, context_instance=RequestContext(request))


def calcular_nivel_medio(partido):
    ocurrencias = {}
    for p in partido.perfiles.all():
        for n in p.deporteNivel.all():
            if n.club.id == partido.pista.club.id and partido.pista.deporte.id == n.deporte.id:
                if n.nivel in ocurrencias:
                    ocurrencias[n.nivel] = ocurrencias[n.nivel] + 1
                else:
                    ocurrencias[n.nivel] = 1
    resultado = ""
    contador = 0
    for nivel, total in ocurrencias.iteritems():
        if total > contador:
            contador = total
            resultado = nivel

    return resultado

@login_required()
def inscripcion_partidos(request):
    error = ""
    if request.method == "POST":
        partido_id = request.POST.get("partido")
        perfil_id = request.POST.get("perfil")
        if partido_id and perfil_id:
            try:
                partido = Partido.objects.get(id=partido_id)
                perfil = Perfil.objects.get(id=perfil_id)
                club = Club.objects.get(id = partido.pista.id)

                if not perfil in partido.perfiles.all():

                    #Crear notificacion para inscripcion
                    notificacion = Notificacion.objects.create(
                        partido = partido,
                        jugador = perfil,
                        estado = settings.ESTADO_NULL,
                        tipo = settings.TIPO_NOTIF_UNIRSE_A_PARTIDO,
                        leido = settings.ESTADO_NO,
                        destino = settings.NOTIF_CLUB,
                        club = partido.pista.club
                    )

                    if notificacion:
                        notificacion.save()
                    else:
                        logger.debug("usuarios/partidos - Método inscripcion_partidos.")
                        error = "Ha habido un error. Por favor, actualice la página y vuelva a intentarlo."
                else:
                    error = "Ya está inscrito en este partido"
            except Exception, e:
                logger.debug("usuarios/partidos - Método inscripcion_partidos." + e.message)
                error = "No hemos podido generar su petición, inténtelo de nuevo más tarde"
    data = {"error":error}
    return HttpResponse(json.dumps(data))

@login_required()
def usuario_mis_partidos(request, id_usuario):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario, request)
    if perfil == None:
        return HttpResponseRedirect("/")

    try:
        mis_partidos = []
        partidos = Partido.objects.filter(pista__club__id__in=PerfilRolClub.objects.values_list('club_id',flat=True).filter(perfil=perfil, rol__id=settings.ROL_JUGADOR)).order_by("-fecha")
        for partido in partidos:
            for p in partido.perfiles.all():
                if perfil.id == p.id:
                    mis_partidos.append(partido)
                    break
    except Exception, e:
        logger.debug("usuarios/partidos - Método usuario_mis_partidos. id_usuario " + str(id_usuario) +". " + e.message)
        partidos = []
        mis_partidos = []

    data = {'perfil': perfil, 'partidos':mis_partidos}
    return render_to_response(ruta_mis_partidos_usuarios, data, context_instance=RequestContext(request))

@login_required()
def usuario_buscador_partido(request, id_usuario):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario, request)
    if perfil == None:
        return HttpResponseRedirect("/")

    try:
        clubes = Club.objects.filter(id__in=PerfilRolClub.objects.values_list('club_id',flat=True).filter(perfil=perfil, rol__id=settings.ROL_JUGADOR))

    except Exception, e:
        logger.debug("usuarios/partidos - Método usuario_buscador_partido. id_usuario " + str(id_usuario) +". " + e.message)
        clubes = []

    data = {'perfil': perfil, 'clubes':clubes}

    if request.method == "GET":
        data["fecha"] = datetime.now().date()

    if request.method == "POST":
        id_club = request.POST.get("id_club")
        id_fh = request.POST.get("franja_horaria")
        fecha = request.POST.get("fecha")
        queryset = Q()
        if id_club:
            data["id_club"] = int(id_club)
            queryset.add(Q(pista__club__id = id_club), Q.AND)

            try:
                franjas_horas = FranjaHora.objects.filter(club__id = id_club)
                data["franjas_horas"] = franjas_horas
            except Exception, e:
                logger.debug("usuarios/partidos - Método usuario_buscador_partido. id_usuario " + str(id_usuario) +". " + e.message)
                franjas_horas = []

        else:
            queryset.add(Q(pista__club__in=clubes), Q.AND)

        if id_fh and int(id_fh) != 0:
            queryset.add(Q(franja_horaria__id = id_fh), Q.AND)
            data["id_fh"] = id_fh

        if fecha:
            date = datetime.strptime(fecha, '%d/%m/%Y').date()
            queryset.add(Q(fecha__startswith = date), Q.AND)
            data["fecha"] = fecha
        else:
            date = datetime.now().date()
            queryset.add(Q(fecha__gt = date), Q.AND)

        try:
            #Campos comunes de busqueda
            queryset.add(Q(visible=settings.ESTADO_SI), Q.AND)

            partidos = Partido.objects.filter(queryset).order_by("-fecha")

        except Exception, e:
            logger.debug("usuarios/partidos - Método usuario_buscador_partido. id_usuario " + str(id_usuario) +". " + e.message)
            partidos = []
        data["partidos"] = partidos

    return render_to_response(ruta_buscador_partidos_usuarios, data, context_instance=RequestContext(request))

@login_required()
def actualizar_franjas_club_ajax(request):
    id_club = request.GET['club_id']
    franjas_horas = FranjaHora.objects.filter(club__id = id_club)
    data = serializers.serialize('json', franjas_horas,
		fields=('id', 'inicio', 'fin'))
    return HttpResponse(data, mimetype='application/json')


def esPartidoDeClubDeUsuario(perfil, partido):

    esPartidoDeClub = False

    if partido:
        esPartidoDeClub = PerfilRolClub.objects.filter(
            club__id = partido.pista.club.id,
            perfil__id = perfil.id,
            rol = Rol.objects.get(id = settings.ROL_JUGADOR)
        ).exists()

    return esPartidoDeClub