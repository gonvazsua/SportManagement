# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from datetime import date,datetime
import json
from django.conf import settings
from Core.forms import *
import logging
from django.contrib.auth.decorators import login_required

#Instancia del log
logger = logging.getLogger(__name__)

ruta_administracion_jugadores = 'administracion/jugadores/jugadores.html'
ruta_administracion_perfil_jugador = 'administracion/jugadores/perfil_jugador.html'
ruta_administracion_nuevo_jugador = 'administracion/jugadores/nuevo_jugador.html'

@login_required()
def administrador_jugadores(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=settings.ROL_ADMINISTRADOR))
    data = {}
    jugadores = PerfilRolClub.objects.filter(club = club).exclude(perfil=perfil).order_by("perfil__user__first_name")
    data = {'perfil':perfil, 'club':club, 'jugadores':jugadores}

    return render_to_response(ruta_administracion_jugadores, data, context_instance=RequestContext(request))

@login_required()
def administrador_perfil_jugador(request, id_usuario, id_jugador):
    perfil = comprueba_usuario_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")
    perfil_jugador = ""
    try:
        perfil_jugador = Perfil.objects.get(id=id_jugador)
    except Perfil.DoesNotExist:
        return administrador_jugadores(request, id_usuario)
    partidos_mes = {}
    #partidos = Partido.objects.extra(select={'year':"strftime('%%Y, fecha')"}).values('year').order_by().annotate(Count('id'))
    #partidos = Partido.objects.extra(select={'month': 'extract( month from fecha )'}).values('id').annotate(dcount=Count('fecha'))
    current_year = date.today().year
    for mes in range(1,13):
        partidos_mes[mes] = Partido.objects.filter(fecha__year = current_year, fecha__month=mes, perfiles=perfil_jugador).count()
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=1))
    data = {'perfil':perfil, 'club':club, 'perfil_jugador':perfil_jugador, 'partidos_mes':partidos_mes}
    return render_to_response(ruta_administracion_perfil_jugador, data, context_instance=RequestContext(request))

@login_required()
def baja_jugador_club(request):
    res = ""
    if "club_id" in request.GET and "jugador_id" in request.GET:
        club_id = request.GET["club_id"]
        perfil_id = request.GET["jugador_id"]
        perfilRolClub = PerfilRolClub.objects.get(perfil__id = perfil_id, club__id=club_id)
        perfilRolClub.delete()
        res = "OK"
    else:
        res = "Ha habido un error al dar de baja al jugador"
        logger.debug("administracion/jugadores - Método baja_jugador_club")
    return HttpResponse(json.dumps({'res':res}))

@login_required()
def administrador_nuevo_jugador(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")
    error = ""
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=settings.ROL_ADMINISTRADOR))
    provincias = Provincias.objects.all()
    municipios = []
    niveles = Nivel.objects.filter(club=club)
    perfil_nuevo = ""
    user_nuevo = ""

    #Alta de jugador
    if request.POST:
        nombre = request.POST.get("nombre", '');
        apellidos = request.POST.get("apellidos", '');
        password = request.POST.get("password", '');
        username = request.POST.get("username", '');
        email = request.POST.get("email", '');

        user_nuevo = ""
        if nombre and apellidos and password and username:
            try:
                un = User.objects.get(username = username)
                error = "Ya existe un usuario con ese nombre de usuario"
            except User.DoesNotExist:
                user_nuevo = User.objects.create_user(username, email, password)
                user_nuevo.first_name = nombre
                user_nuevo.last_name = apellidos

                rol_jugador = Rol.objects.get(id=settings.ROL_JUGADOR)
                perfil_nuevo = Perfil.objects.create(user = user_nuevo)
                perfil_rol_club = PerfilRolClub.objects.create(perfil = perfil_nuevo, club = club, rol = rol_jugador)

                if perfil_nuevo and perfil_rol_club:
                    perfil_nuevo.user = user_nuevo
                    perfil_nuevo.telefono = request.POST.get("telefono",'');
                    try:
                        m = Municipios.objects.get(id=request.POST.get("municipio", ''))
                        perfil_nuevo.municipio = m;
                        if "imagen" in request.FILES:
                            formImagen = FormImagen(request.POST, request.FILES)
                            if formImagen.is_valid():
                                perfil_nuevo.imagen = formImagen.cleaned_data["imagen"]
                            else:
                                perfil_nuevo.imagen = ""
                        else:
                            perfil_nuevo.imagen = ""

                        #Guardar perfil nuevo
                        user_nuevo.save()
                        perfil_nuevo.save()
                        perfil_rol_club.save()

                    except Municipios.DoesNotExist:
                        logger.debug("administracion/jugadores - Método administrador_nuevo_jugador: id_usuario" + str(id_usuario))
                        error = "Ha habido un error al crear al usuario. Si el problema persiste, póngase en contacto con el administrador."

                    #Asignarle los niveles de los deportes
                    niveles = []
                    for nivel_id in request.POST["nivel"]:
                        nivel = Nivel.objects.get(id=nivel_id)
                        niveles.append(nivel)

                    perfil_nuevo.deporteNivel = niveles
                    perfil_nuevo.save()

                    return HttpResponseRedirect("/administrador/"+str(perfil.user.id)+"/jugadores/"+str(perfil_nuevo.id))
                else:
                    logger.debug("administracion/jugadores - Método administrador_nuevo_jugador: id_usuario" + str(id_usuario))
                    error = "Lo sentimos, ha habido un error al crear el jugador. Si el problema persiste, póngase en contacto con el administrador"
        else:
            logger.debug("administracion/jugadores - Método administrador_nuevo_jugador: id_usuario" + str(id_usuario))
            error = "Lo sentimos, ha habido un error al crear el jugador. Si el problema persiste, póngase en contacto con el administrador"

    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=settings.ROL_ADMINISTRADOR))
    data = {'perfil':perfil, 'club':club, 'error':error, 'provincias':provincias, 'municipios':municipios,
    'niveles':niveles}
    return render_to_response(ruta_administracion_nuevo_jugador, data, context_instance=RequestContext(request))