# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from datetime import date,datetime
import json
import logging
from django.contrib.auth.decorators import login_required

#Instancia del log
logger = logging.getLogger(__name__)

ruta_usuarios_mis_clubes = 'usuarios/clubes/usuarios_mis_clubes.html'
ruta_usuarios_buscador_clubes = 'usuarios/clubes/usuarios_buscador_clubes.html'
ruta_usuarios_club = 'usuarios/clubes/usuarios_club.html'

@login_required()
def usuario_mis_clubes(request, id_usuario):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario, request)
    if perfil == None:
        return HttpResponseRedirect("/")

    clubes = Club.objects.filter(id__in=PerfilRolClub.objects.values_list('club_id', flat=True).filter(perfil=perfil, rol__id=settings.ROL_JUGADOR))

    #Comprobar si existen notificaciones de club para marcar como leídas
    try:
        notificaciones = Notificacion.objects.filter(jugador = perfil, tipo = settings.TIPO_NOTIF_INSCRIPCION_CLUB, destino=settings.NOTIF_JUGADOR).update(leido = settings.ESTADO_SI)

    except Exception:
        notificaciones = []

    data = {'perfil': perfil, 'clubes':clubes}
    return render_to_response(ruta_usuarios_mis_clubes, data, context_instance=RequestContext(request))

@login_required()
def usuario_buscador_clubes(request, id_usuario):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario, request)
    if perfil == None:
        return HttpResponseRedirect("/")
    try:
        provincias = Provincias.objects.all()
        municipios = []
        if perfil.municipio:
            municipios = Municipios.objects.filter(provincia = perfil.municipio.provincia)

    except Exception:
        provincias = ""

    data = {'perfil': perfil, 'provincias':provincias, 'municipios':municipios}

    #Se ha utilizado el buscador
    if request.method == "POST":
        provincia_id = request.POST.get('provincia')
        municipio_id = request.POST.get('municipio')
        clubes_excluir = [settings.ID_CLUB_PRUEBAS, settings.ID_CLUB_DEMO]

        try:
            #Buscar clubes a los que ya pertenece el jugador o ha enviado peticiones para que no pueda
            #volverlas a enviar.
            clubes_ya_pertenece = PerfilRolClub.objects.values_list('club_id',flat=True).filter(perfil=perfil)
            clubes_ya_peticion_enviada = Notificacion.objects.values_list('club_id',flat=True).filter(tipo = settings.TIPO_NOTIF_INSCRIPCION_CLUB, jugador=perfil, estado=settings.ESTADO_NULL)

            if municipio_id  and int(municipio_id) != 0:
                clubes = Club.objects.filter(municipio__id = municipio_id).exclude(id__in = clubes_excluir)
            elif provincia_id and int(provincia_id) != 0:
                clubes = Club.objects.filter(municipio__provincia__id = provincia_id).exclude(id__in = clubes_excluir)
            else:
                clubes = []

            data["clubes"] = clubes
            data["clubes_ya_pertenece"] = clubes_ya_pertenece
            data["clubes_ya_peticion_enviada"] = clubes_ya_peticion_enviada

        except Exception, e:
            data["clubes"] = []
            data["clubes_ya_pertenece"] = []
            data["clubes_ya_peticion_enviada"] = clubes_ya_peticion_enviada

    return render_to_response(ruta_usuarios_buscador_clubes, data, context_instance=RequestContext(request))

@login_required()
def usuario_club_inscripcion(request):
    error = ""
    if request.method == "POST":
        club_id = request.POST.get("club_id")
        perfil_id = request.POST.get("perfil_id")
        if club_id and perfil_id:
            try:
                perfil = Perfil.objects.get(id=perfil_id)
                club = Club.objects.get(id=club_id)
                if(PerfilRolClub.objects.filter(perfil=perfil, club=club).count() == 0):

                    #Crear notificacion para el club
                    notificacion = Notificacion.objects.create(
                        leido = settings.ESTADO_NO,
                        fecha=datetime.now().date(),
                        tipo = settings.TIPO_NOTIF_INSCRIPCION_CLUB,
                        destino=settings.NOTIF_CLUB,
                        club = club,
                        jugador = perfil,
                        estado = settings.ESTADO_NULL
                    )
                    notificacion.save()
                else:
                    error = "Ya está inscrito en este club"
            except Exception, e:
                logger.debug("usuarios/clubes - Método usuario_club_inscripcion." + e.message)
                error = "No hemos podido generar su petición, inténtelo de nuevo más tarde"
    data = {"error":error}
    return HttpResponse(json.dumps(data))

@login_required()
def usuario_club_baja(request):
    error = ""
    if request.method == "POST":
        club_id = request.POST.get("club_id")
        perfil_id = request.POST.get("perfil_id")
        if club_id and perfil_id:
            try:
                perfil = Perfil.objects.get(id=perfil_id)
                club = Club.objects.get(id=club_id)

                #Borrar notificaciones
                Notificacion.objects.filter(
                    (Q(club = club) | Q(partido__pista__club = club)) & Q(jugador = perfil)
                ).delete()

                #Borrar niveles de juego del jugador en el club
                for dn in perfil.deporteNivel.all():
                    if dn.club.id == club.id:
                        perfil.deporteNivel.remove(dn)

                PerfilRolClub.objects.get(perfil=perfil, club=club).delete()

            except Exception, e:
                logger.debug("usuarios/clubes - Método usuario_club_baja." + e.message)
                error = "No hemos podido generar su petición, actualice la página e inténtelo de nuevo."
    data = {"error":error}
    return HttpResponse(json.dumps(data))


@login_required()
def usuario_clubes_club(request, id_usuario, id_club):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario, request)
    if perfil == None:
        return HttpResponseRedirect("/")
    else:
        data = {'perfil': perfil}

    compruebaUsuarioPerteneceAClub(perfil.id, id_club)

    try:

        club = Club.objects.get(id = id_club)
        data["club"] = club

        #Eventos
        eventos = Evento.objects.filter(club = club).order_by("-creado_el")[:20]
        data["eventos"] = eventos

        #Partidos
        partidos = Partido.objects.filter(
            Q(fecha = datetime.today(), franja_horaria__inicio__gt=datetime.now()) | Q(fecha__gt=datetime.today()),
            pista__club=club, visible = settings.ESTADO_SI
        ).order_by('fecha', 'franja_horaria__inicio')[:10]

        data["partidos"] = partidos

    except Exception, e:
        logger.debug("usuarios/clubes - Método usuario_clubes_club." + e.message)

    return render_to_response(ruta_usuarios_club, data, context_instance=RequestContext(request))