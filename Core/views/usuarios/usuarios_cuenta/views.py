# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from datetime import date,datetime
import os
import json
import logging
from django.contrib.auth.decorators import login_required

#Instancia del log
logger = logging.getLogger(__name__)

ruta_cuenta_usuarios = 'usuarios/cuenta/usuarios_cuenta.html'

@login_required()
def usuario_mi_cuenta(request, id_usuario):
    perfil = comprueba_usuario_logado_no_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")
    try:
        provincias = Provincias.objects.all()
        if perfil.municipio:
            municipios = Municipios.objects.filter(provincia = perfil.municipio.provincia)
    except Exception, e:
        logger.debug("usuarios/cuenta - Método usuario_mi_cuenta. id_usuario " + str(id_usuario) +". " + e)
        provincias = None
        municipios = None

    #Formulario
    error = None
    success = None
    if request.method == "POST":
        if request.POST.get("action") and request.POST.get("action") == "niveles":
            perfil_id = request.POST.get("perfil_id")
            nivel_id = request.POST.get("nivel")
            club_id = request.POST.get("club")
            deporte_id = request.POST.get("deporte")
            if perfil_id and nivel_id and club_id and deporte_id:
                try:
                    if not existe_nivel(perfil.deporteNivel.all(), nivel_id, club_id, deporte_id):
                        nivel = Nivel.objects.get(id=nivel_id)
                        perfil.deporteNivel.add(nivel)
                        perfil.save()
                        success = "Se ha agregado correctamente el deporte y el nivel."
                    else:
                        error = "Ya existe un nivel para ese deporte en el club seleccionado."
                except Exception, e:
                    logger.debug("usuarios/cuenta - Método usuario_mi_cuenta. id_usuario " + str(id_usuario) +". " + e.message)
                    error = "Ha habido un error al guardar los niveles. Actualice la página y vuelva a intentarlo."
            else:
                logger.debug("usuarios/cuenta - Método usuario_mi_cuenta. id_usuario " + str(id_usuario) +". ")
                error = "Ha habido un error al guardar los niveles. Actualice la página y vuelva a intentarlo."
        else:
            try:
                if request.POST.get("nombre"):
                    perfil.user.first_name = request.POST.get("nombre")
                if request.POST.get("apellidos"):
                    perfil.user.last_name = request.POST.get("apellidos")
                if request.POST.get("email"):
                    perfil.user.email = request.POST.get("email")
                if request.POST.get("username"):
                    perfil.user.username = request.POST.get("username")
                if request.POST.get("password"):
                    perfil.user.set_password(request.POST["password"])

                perfil.user.save()

                if request.POST.get("telefono"):
                    perfil.telefono = request.POST["telefono"]
                if request.POST.get("municipio"):
                    municipio = Municipios.objects.get(id=request.POST.get("municipio"))
                    perfil.municipio = municipio
                if request.FILES.get("imagen"):
                    if not perfil.imagen == "":
                        borrar_imagen_anterior(perfil.imagen.path)
                    perfil.imagen = request.FILES.get("imagen")

                perfil.save()
                success = "Sus datos se han guardado correctamente."
            except Exception, e:
                logger.debug("usuarios/cuenta - Método usuario_mi_cuenta. id_usuario " + str(id_usuario) +". " + e)
                error = "Ha habido un error al guardar sus datos."

    data = {'perfil': perfil, 'provincias':provincias, 'municipios':municipios, 'error':error, 'success':success}

    return render_to_response(ruta_cuenta_usuarios, data, context_instance=RequestContext(request))

def borrar_imagen_anterior(url_imagen):
    try:
        if os.path.isfile(url_imagen):
            os.remove(url_imagen)
    except Exception, e:
        logger.debug("usuarios/cuenta - Método borrar_imagen_anterior. URL_IMAGEN:" + str(url_imagen) +". " + e)

@login_required()
def clubes_niveles_cuenta(request):
    id_club = request.GET.get('club_id')
    if id_club:
        deportes = Deporte.objects.filter(id__in = Nivel.objects.values_list('deporte_id', flat=True).filter(club__id = id_club))
        data = serializers.serialize('json', deportes, fields=('id', 'deporte'))
    else:
        data = ""
    return HttpResponse(data, mimetype='application/json')

@login_required()
def clubes_deportes_cuenta(request):
    id_deporte = request.GET.get('deporte_id')
    id_club = request.GET.get('club_id')
    if id_deporte and id_club:
        niveles = Nivel.objects.filter(deporte__id = id_deporte, club__id = id_club)
        data = serializers.serialize('json', niveles, fields=('id', 'nivel'))
    else:
        data = ""
    return HttpResponse(data, mimetype='application/json')


def existe_nivel(lista, nivel_id, club_id, deporte_id):
    existe = False
    for n in lista:
        if n.club.id == int(club_id) and n.deporte.id == int(deporte_id):
            existe = True
            break

    return existe

@login_required()
def eliminar_niveles_club_cuenta(request):
    error = None
    if request.method == "POST":
        club_id = request.POST.get("club")
        deporte_id = request.POST.get("deporte")
        nivel_id = request.POST.get("nivel")
        perfil_id = request.POST.get("perfil")
        if club_id and deporte_id and nivel_id and perfil_id:
            try:
                perfil = Perfil.objects.get(id=perfil_id)
                nivel = perfil.deporteNivel.get(deporte__id = deporte_id, club__id = club_id)
                perfil.deporteNivel.remove(nivel)
                perfil.save()
            except Exception, e:
                logger.debug("usuarios/cuenta - Método eliminar_niveles_club_cuenta." + e)
                error = "Ha habido un error al eliminar el nivel. Actualice la página e inténtelo de nuevo."
    data = {"error":error}
    return HttpResponse(json.dumps(data))

@login_required()
def eliminar_cuenta_usuario(request, id_usuario):
    error = ""
    try:
        perfil = comprueba_usuario_logado_no_administrador(id_usuario)

        #Desactivamos al jugador y hacemos logout
        if not PerfilRolClub.objects.filter(perfil = perfil, rol = settings.ROL_ADMINISTRADOR).exists():
            perfil.user.is_active = False
            perfil.user.save()
        else:
            error = "No puede eliminar su cuenta siendo administrador del club"
            provincias = Provincias.objects.all()
            if perfil.municipio:
                municipios = Municipios.objects.filter(provincia = perfil.municipio.provincia)
            return render_to_response(ruta_cuenta_usuarios, {'error':error,'perfil': perfil, 'provincias':provincias, 'municipios':municipios}, context_instance=RequestContext(request))

    except Exception, e:
        logger.debug("usuarios/cuenta - Método eliminar_cuenta_usuario." + e)

    return HttpResponseRedirect("/logout")