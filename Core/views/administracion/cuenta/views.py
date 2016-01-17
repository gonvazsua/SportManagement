# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from Core.forms import *
from django.conf import settings
import logging
from django.contrib.auth.decorators import login_required

#Instancia del log
logger = logging.getLogger(__name__)

#Rutas de la vista
ruta_administracion_cuenta = "administracion/cuenta/administracion_cuenta.html"

@login_required()
def administracion_cuenta(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    if perfil == None:
        return HttpResponseRedirect("/")
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=1))
    provincias = Provincias.objects.all()
    municipios = []
    data = {}

    if request.POST:
        try:
            if request.POST["nombre"] != "":
                perfil.user.first_name = request.POST["nombre"];
            if request.POST["apellidos"] != "":
                perfil.user.last_name = request.POST["apellidos"];
            if request.POST["email"] != "":
                perfil.user.email = request.POST["email"];
            if request.POST["username"] != "":
                perfil.user.username = request.POST["username"];
            if request.POST["password"] != "":
                perfil.user.set_password(request.POST["password"]);
            if request.POST["telefono"] != "":
                perfil.telefono = request.POST["telefono"];
            if request.POST["municipio"] != "":
                m = Municipios.objects.get(id=request.POST["municipio"])
                perfil.municipio = m;
            if request.FILES.get("imagen") != None:
                #(settings.MEDIA_ROOT + "/" + request.FILES["imagen"], content, save=True);
                formImagen = FormImagen(request.POST, request.FILES)
                perfil.imagen = formImagen.cleaned_data["imagen"]
            else:
                perfil.imagen = ""

            perfil.user.save()
            perfil.save()
        except Exception:
            municipios = []
            logger.debug("administracion/cuenta - Método administracion_cuenta: id_usuario " + str(id_usuario))
    try:
        if perfil.municipio != "" and perfil.municipio != None:
            municipios = Municipios.objects.filter(provincia = perfil.municipio.provincia)
    except Exception:
        municipios = []
        logger.debug("administracion/cuenta - Método administracion_cuenta: id_usuario " + str(id_usuario))

    data = {'perfil':perfil, 'club':club, 'provincias':provincias, 'municipios':municipios}
    return render_to_response(ruta_administracion_cuenta, data, context_instance=RequestContext(request))
