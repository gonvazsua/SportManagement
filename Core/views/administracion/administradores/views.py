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
ruta_administradores = "administracion/administradores/administradores.html"

@login_required()
def administradores_club(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=1))
    data = {}
    jugadores = []

    data = {
        'perfil':perfil, 'club':club, 'jugadores':jugadores
    }

    try:
        if request.POST:
            action = request.POST.get('action')

            if action == "eliminar":
                id_administrador = request.POST.get('id_administrador_seleccionado')
                if id_administrador:
                    prc = PerfilRolClub.objects.filter(id=id_administrador, club=club).update(rol=settings.ROL_JUGADOR)

            elif action == "buscar":
                email = request.POST.get('email')
                usuario = request.POST.get('usuario')
                lista_consultas = []

                if email:
                    lista_consultas.append(Q(email=email))
                if usuario:
                    lista_consultas.append(Q(username=usuario))

                if lista_consultas:
                    user = User.objects.filter(reduce(operator.and_, lista_consultas))
                    jugadores = Perfil.objects.filter(user__in=user)
                else:
                    perfilRolClub = PerfilRolClub.objects.values_list('perfil').filter(club=club, rol = settings.ROL_JUGADOR)
                    if perfilRolClub:
                        jugadores = Perfil.objects.filter(id__in=perfilRolClub)

            elif action == "asignar":
                id_jugador = request.POST.get('id_jugador_asignado')
                if id_jugador:
                    jugador = Perfil.objects.get(id=id_jugador)
                    perfilRolClubJugador = PerfilRolClub.objects.filter(perfil=jugador, club=club).update(rol=settings.ROL_ADMINISTRADOR)

            data['jugadores'] = jugadores

        administradores = PerfilRolClub.objects.filter(club=club, rol=settings.ROL_ADMINISTRADOR)
        data['administradores'] = administradores

    except Exception:
        logger.debug("administracion/administradores - Método administradores_club: id_usuario " + str(id_usuario))

    return render_to_response(ruta_administradores, data, context_instance=RequestContext(request))