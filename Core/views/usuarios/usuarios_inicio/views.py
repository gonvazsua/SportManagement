# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from datetime import date,datetime
import json
import logging
from django.contrib.auth.decorators import login_required

#Instancia del log
logger = logging.getLogger(__name__)

ruta_inicio_usuarios = 'usuarios/inicio/pagina_principal.html'

@login_required()
def usuario_inicio(request, id_usuario):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario, request)

    try:
        provincias = Provincias.objects.all()
        clubes = Club.objects.filter(id__in=PerfilRolClub.objects.values_list('club_id', flat=True).filter(perfil=perfil, rol=settings.ROL_JUGADOR))
        clubes_pendientes_aceptar = Club.objects.filter(id__in=Notificacion.objects.values_list('club_id', flat=True).filter(jugador=perfil, estado=settings.ESTADO_NULL))
        club_partidos_disponibles = {}
        for c in clubes:
            try:
                partidos = Partido.objects.filter(
                    Q(fecha=datetime.today(), franja_horaria__inicio__gt=datetime.now()) | Q(fecha__gt=datetime.today()),
                    pista__club=c, visible = settings.ESTADO_SI
                ).order_by('fecha', 'franja_horaria__inicio')[:6]
                club_partidos_disponibles[c] = partidos
            except Exception:
                club_partidos_disponibles[c] = None

    except Exception, e:
        logger.debug("usuarios/inicio - Método usuario_inicio. id_usuario " + str(id_usuario) +". " + e.message)
        provincias = None
        clubes = None
        clubes_pendientes_aceptar = None

    #Notificaciones
    try:
        notificaciones = Notificacion.objects.filter(jugador = perfil, destino=settings.NOTIF_JUGADOR, leido=settings.ESTADO_NO).order_by("leido","-fecha")
    except Exception:
        notificaciones = []

    data = {'perfil': perfil, 'provincias':provincias, 'clubes':clubes, 'clubes_pendientes_aceptar':clubes_pendientes_aceptar,
            'club_partidos_disponibles':club_partidos_disponibles, 'notificaciones':notificaciones}

    data = cargar_tipos_notificaciones_settings(data)

    return render_to_response(ruta_inicio_usuarios, data, context_instance=RequestContext(request))

@login_required()
def completar_datos_inicio(request):
    error = ""
    if request.method == "POST":
        perfil_id = request.POST.get('perfil_id')
        telefono = request.POST.get('telefono')
        municipio = request.POST.get('municipio')
        try:
            if perfil_id:
                perfil = Perfil.objects.get(id=perfil_id)
            if perfil and telefono:
                perfil.telefono = telefono
            if perfil and municipio:
                m = Municipios.objects.get(id=municipio)
                perfil.municipio = m
            if perfil:
                perfil.save()
        except Exception, e:
            logger.debug("usuarios/inicio - Método completar_datos_inicio. " + e.message)
            error = "Ha habido un error al guardar sus datos, actualice la página y vuelva a intentarlo"
    data = {'error':error}
    return HttpResponse(json.dumps(data))
