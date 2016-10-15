# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from datetime import date,datetime
import json
import logging
from django.contrib.auth.decorators import login_required

#Instancia del log
logger = logging.getLogger(__name__)

ruta_usuarios_notificaciones = 'usuarios/notificaciones/notificaciones.html'

@login_required()
def usuario_notificaciones(request, id_usuario):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario, request)

    try:
        #Notificaciones
        try:
            notificaciones = Notificacion.objects.filter(
                jugador = perfil,
                destino=settings.NOTIF_JUGADOR
            ).order_by("leido","-fecha")

        except Exception:
            notificaciones = []

        data = {'perfil': perfil, 'notificaciones':notificaciones}

        data = cargar_tipos_notificaciones_settings(data)

    except Exception, e:
        logger.debug("usuarios/notificaciones - Método usuario_notificaciones. " + e.message)
        raise 404

    return render_to_response(ruta_usuarios_notificaciones, data, context_instance=RequestContext(request))