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

@login_required()
def usuario_mis_clubes(request, id_usuario):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")

    clubes = Club.objects.filter(id__in=PerfilRolClub.objects.values_list('club_id', flat=True).filter(perfil=perfil, rol__id=settings.ROL_JUGADOR))

    #Comprobar si existen notificaciones de club para marcar como leídas
    try:
        inscripciones_club_ids = InscripcionesEnClub.objects.values_list('id', flat=True).filter(club__in = clubes, jugador = perfil)
        if inscripciones_club_ids.count() > 0:
            notificaciones = Notificacion.objects.filter(inscripcionEnClub__id__in=inscripciones_club_ids, destino=settings.NOTIF_JUGADOR).update(leido = settings.ESTADO_SI)

    except Exception:
        notificaciones = []

    data = {'perfil': perfil, 'clubes':clubes}
    return render_to_response(ruta_usuarios_mis_clubes, data, context_instance=RequestContext(request))

@login_required()
def usuario_buscador_clubes(request, id_usuario):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")
    try:
        provincias = Provincias.objects.all()
    except Exception:
        provincias = ""

    data = {'perfil': perfil, 'provincias':provincias}

    #Se ha utilizado el buscador
    if request.method == "POST":
        provincia_id = request.POST.get('provincia')
        municipio_id = request.POST.get('municipio')
        if municipio_id  and int(municipio_id) != 0:
            clubes = Club.objects.filter(municipio__id = municipio_id)
        elif provincia_id and int(provincia_id) != 0:
            clubes = Club.objects.filter(municipio__provincia__id = provincia_id)
        else:
            clubes = []
        data["clubes"] = clubes

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
                    inscripcion = InscripcionesEnClub.objects.create(club=club, jugador=perfil, estado=settings.ESTADO_NULL)
                    inscripcion.save()
                    #Asociar notificacion para el club
                    notificacion = Notificacion.objects.create(leido = settings.ESTADO_NO, fecha=datetime.now().date(), inscripcionEnClub = inscripcion, destino=settings.NOTIF_CLUB)
                    notificacion.save()
                else:
                    error = "Ya está inscrito en este club"
            except Exception, e:
                logger.debug("usuarios/clubes - Método usuario_club_inscripcion." + e)
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
                prc = PerfilRolClub.objects.get(perfil=perfil, club=club)
                prc.delete()
            except Exception, e:
                logger.debug("usuarios/clubes - Método usuario_club_baja." + e)
                error = "No hemos podido generar su petición, actualice la página e inténtelo de nuevo."
    data = {"error":error}
    return HttpResponse(json.dumps(data))