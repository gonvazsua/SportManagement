# -*- encoding: utf-8 -*-
from Core.views import *
from Core.utils import *
from Core.forms import *
from django.conf import settings

#Rutas de la vista
ruta_administracion_cuenta = "administracion/cuenta/administracion_cuenta.html"

def administracion_cuenta(request, id_usuario):
    perfil = comprueba_usuario_administrador(id_usuario)
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=1))
    provincias = Provincias.objects.all()
    municipios = []
    data = {}

    if request.POST:
        if request.POST["nombre"] != "":
            perfil.user.first_name = request.POST["nombre"];
        if request.POST["apellidos"] != "":
            perfil.user.last_name = request.POST["apellidos"];
        if request.POST["email"] != "":
            perfil.user.email = request.POST["email"];
        if request.POST["password"] != "":
            perfil.user.set_password(request.POST["password"]);
        if request.POST["telefono"] != "":
            perfil.telefono = request.POST["telefono"];
        if request.POST["municipio"] != "":
            m = Municipios.objects.get(id=request.POST["municipio"])
            perfil.municipio = m;
        if request.FILES["imagen"] != "":
            #(settings.MEDIA_ROOT + "/" + request.FILES["imagen"], content, save=True);
            formImagen = FormImagen(request.POST, request.FILES)
            perfil.imagen = formImagen.cleaned_data["imagen"]
        else:
            perfil.imagen = ""

        perfil.user.save()
        perfil.save()

    if perfil.municipio != "":
        municipios = Municipios.objects.filter(provincia = perfil.municipio.provincia)

    data = {'perfil':perfil, 'club':club, 'provincias':provincias, 'municipios':municipios}
    return render_to_response(ruta_administracion_cuenta, data, context_instance=RequestContext(request))
