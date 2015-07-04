# -*- encoding: utf-8 -*-
from Core.utils import *
from django.db.models import *
from datetime import date,datetime

ruta_pagina_principal = 'administracion/inicio/pagina_principal.html'

def perfil_administrador(request, id_usuario):
    user = ""
    perfil = ""
    try:
        user = User.objects.get(id = id_usuario)
        perfil = Perfil.objects.get(user = user)
        if not PerfilRolClub.objects.filter(perfil = perfil, rol_id = 1).exists():
            return HttpResponse('/inicio')
        if not user.is_authenticated():
            return HttpResponse('/inicio')
    except User.DoesNotExist:
        return HttpResponse('/inicio')

    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil = perfil, rol_id = 1))
    rutaTiempo = RutaTiempo.objects.get(municipio=club.municipio)
    jugadores = PerfilRolClub.objects.filter(club = club).exclude(perfil=perfil).order_by("perfil__user__first_name")
    num_partidos_hoy = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(pista__club=club, fecha__startswith=date.today(), num_perfiles=4).count()
    num_partidos_abiertos_hoy = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(
        fecha__startswith=date.today(), num_perfiles__lt=4, num_perfiles__gt=0, pista__in=Pista.objects.filter(club=club)).count()
    franja_horaria_actual = FranjaHora.objects.filter(club = club, inicio__lt=datetime.now().time(), fin__gt=datetime.now().time()).first()
    if franja_horaria_actual:
        num_partidos_en_juego = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(
            pista__in=Pista.objects.filter(club=club),
            franja_horaria=franja_horaria_actual,
            num_perfiles=4,
            fecha=date.today()).count()
    else:
        num_partidos_en_juego = 0
        franja_horaria_actual = FranjaHora.objects.filter(club = club).first()
    #Partidos de la franja horaria
    partidos_ahora = Partido.objects.annotate(num_perfiles=Count('perfiles')).filter(
        pista__in = Pista.objects.filter(club=club), franja_horaria=franja_horaria_actual,
        num_perfiles = 4
    )
    pistas = Pista.objects.filter(club = club)
    #Pistas y partidos de la franja horaria
    pistas_partidos = {}
    for p in pistas:
        try:
            partido = Partido.objects.get(pista = p, franja_horaria = franja_horaria_actual, fecha__startswith=date.today())
            pistas_partidos[p] = partido
        except Partido.DoesNotExist:
            pistas_partidos[p] = ""

    data = {'perfil':perfil, 'club':club, 'jugadores':jugadores, 'num_partidos_hoy':num_partidos_hoy, 'num_partidos_abiertos_hoy':num_partidos_abiertos_hoy,
        'num_partidos_en_juego':num_partidos_en_juego, 'franja_horaria_actual':franja_horaria_actual, 'pistas_partidos':pistas_partidos, 'pistas':pistas,
        'rutaTiempo':rutaTiempo}
    return render_to_response(ruta_pagina_principal, data, context_instance=RequestContext(request))
