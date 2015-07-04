# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from django.db.models import *
from datetime import date,datetime
import collections
import json

ruta_administracion_estadisticas = 'administracion/estadisticas/estadisticas.html'

def administrador_estadisticas(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=1))
    error = ""
    mes_buscar = date.today().month
    ano_buscar = date.today().year
    lista_meses = cargar_meses()
    lista_anos = range(ano_buscar, ano_buscar+6)
    mes_comparar = 0
    ano_comparar = 0
    fecha_comparar = ""
    data = {'perfil':perfil, 'club':club, 'lista_meses':lista_meses, 'lista_anos':lista_anos}

    if request.POST:
        #Partidos en la fecha seleccionada
        if "mes_comparar" in request.POST and "ano_comparar" in request.POST:
            mes_comparar = request.POST["mes_comparar"]
            ano_comparar = request.POST["ano_comparar"]
        if "mes_buscar" in request.POST and "ano_buscar" in request.POST:
            mes_buscar = request.POST["mes_buscar"]
            ano_buscar = request.POST["ano_buscar"]

    if mes_buscar == 0 or ano_buscar == 0:
        mes_buscar = date.today().month
        ano_buscar = date.today().year

    data['ano_comparar'] = ano_comparar
    data['mes_comparar'] = mes_comparar
    data['ano_buscar'] = ano_buscar
    data['mes_buscar'] = mes_buscar

    #Partidos en el mes actual
    partidos_mes_actual_comparar = None
    try:
        partidos_mes_actual = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(pista__club=club, fecha__month=mes_buscar, fecha__year=ano_buscar, num_perfiles=4).count()
        if mes_comparar != 0 and ano_comparar != 0:
            partidos_mes_actual_comparar = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(pista__club=club, fecha__month=mes_comparar, fecha__year=ano_comparar, num_perfiles=4).count()
    except Partido.DoesNotExist:
        partidos_mes_actual = 0
    data['partidos_mes_actual'] = partidos_mes_actual
    data['partidos_mes_actual_comparar'] = partidos_mes_actual_comparar

    #Jugadores nuevos este mes
    jugadores_nuevos_comparar = None
    try:
        jugadores_nuevos = Perfil.objects.filter(user__date_joined__month = mes_buscar).count()
        if mes_comparar != 0 and ano_comparar != 0:
            jugadores_nuevos_comparar = Perfil.objects.filter(user__date_joined__month = mes_comparar, user__date_joined__year = ano_comparar).count()
    except Perfil.DoesNotExist:
        jugadores_nuevos = 0
    data['jugadores_nuevos'] = jugadores_nuevos
    data['jugadores_nuevos_comparar'] = jugadores_nuevos_comparar

    #Partidos en cada franja horaria
    try:
        franjas_horarias = FranjaHora.objects.filter(club = club)
        partidos_franja_horaria = {}
        partidos_franja_horaria_comparar = {}
        for fh in franjas_horarias:
            try:
               partidos_franja_horaria[fh] = Partido.objects.filter(pista__club = club, franja_horaria__id = fh.id, fecha__month = mes_buscar, fecha__year = ano_buscar).count()
               if mes_comparar != 0 and ano_comparar != 0:
                   partidos_franja_horaria_comparar[fh] = Partido.objects.filter(pista__club = club, franja_horaria__id = fh.id, fecha__month = mes_comparar, fecha__year = ano_comparar).count()
            except Partido.DoesNotExist:
                partidos_franja_horaria[fh] = 0
                if mes_comparar != 0 and ano_comparar != 0:
                    partidos_franja_horaria_comparar[fh] = 0
    except FranjaHora.DoesNotExist:
        partidos_franja_horaria = {}
        partidos_franja_horaria_comparar = {}
    data['partidos_franja_horaria'] = partidos_franja_horaria
    data['partidos_franja_horaria_comparar'] = partidos_franja_horaria_comparar

    #Jugador del mes
    jugador_mes_comparar = None
    try:
        #Sacamos todos los Ids de los perfiles de los partidos del club, y despues sacamos el id del perfil que mas se repite en esta lista con most_common(0)
        c = collections.Counter(Partido.objects.values_list('perfiles', flat=True).filter(pista__club = club, fecha__month=mes_buscar, fecha__year=ano_buscar)).most_common(1)
        partidos_jugados_jugador_mes = c[0][1]
        jugador_mes_id = c[0][0]
        jugador_mes = Perfil.objects.get(id=int(jugador_mes_id))
        if mes_comparar != 0 and ano_comparar != 0:
            c = collections.Counter(Partido.objects.values_list('perfiles', flat=True).filter(pista__club = club, fecha__month=mes_comparar, fecha__year=ano_comparar)).most_common(1)
            if len(c) != 0:
                partidos_jugados_jugador_mes_comparar = c[0][1]
                jugador_mes_id_comparar = c[0][0]
                jugador_mes_comparar = Perfil.objects.get(id=int(jugador_mes_id_comparar))
            else:
                jugador_mes_comparar = None
    except Partido.DoesNotExist:
        jugador_mes = ""
        jugador_mes_comparar = None
    except Perfil.DoesNotExist:
        jugador_mes = ""
        jugador_mes_comparar = None

    data['jugador_mes'] = jugador_mes
    data['jugador_mes_comparar'] = jugador_mes_comparar

    #Partidos abiertos este mes
    num_partidos_abiertos_mes_comparar = None
    try:
        num_partidos_abiertos_mes = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(
            fecha__month=mes_buscar, fecha__year=ano_buscar, num_perfiles__lt=4, num_perfiles__gt=0, pista__in=Pista.objects.filter(club=club)).count()
        if mes_comparar != 0 and ano_comparar != 0:
            num_partidos_abiertos_mes_comparar = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(
                fecha__month=mes_comparar, fecha__year=ano_comparar, num_perfiles__lt=4, num_perfiles__gt=0, pista__in=Pista.objects.filter(club=club)).count()

    except Partido.DoesNotExist:
        num_partidos_abiertos_mes = 0
        num_partidos_abiertos_mes = None
    data['num_partidos_abiertos_mes'] = num_partidos_abiertos_mes
    data['num_partidos_abiertos_mes_comparar'] = num_partidos_abiertos_mes_comparar

    #Numero de partidos por mes
    try:
        partidos_por_mes = {}
        partidos_por_mes_comparar = {}
        for mes in range(1,13):
            partidos_por_mes[mes] = Partido.objects.filter(fecha__year = ano_buscar, fecha__month=mes, pista__club=club).count()
            if mes_comparar != 0 and ano_comparar != 0:
                partidos_por_mes_comparar[mes] = Partido.objects.filter(fecha__year = ano_comparar, fecha__month=mes, pista__club=club).count()
    except Partido.DoesNotExist:
        partidos_por_mes = {}
    data["partidos_por_mes"] = partidos_por_mes
    data["partidos_por_mes_comparar"] = partidos_por_mes_comparar

    return render_to_response(ruta_administracion_estadisticas, data, context_instance=RequestContext(request))


def cargar_meses():
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    return meses