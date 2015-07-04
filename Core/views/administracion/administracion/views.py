# -*- encoding: utf-8 -*-
from Core.views import *
from django.core import serializers
from Core.utils import *
from Core.forms import *

#Rutas de la vista
ruta_administracion_club = "administracion/configuracion/administracion_club.html"

def administracion_club(request, id_usuario):
    municipio = ""
    provincia = ""
    form_admin_club = FormAdministracionClub()
    perfil = comprueba_usuario_administrador(id_usuario)
    club = Club.objects.get(id = PerfilRolClub.objects.values_list('club_id', flat=True).get(perfil=perfil, rol_id=1))
    provincias = Provincias.objects.all()
    if perfil.municipio != "":
        municipio = Municipios.objects.get(id=perfil.municipio.id)
        provincia = Provincias.objects.get(id = municipio.provincia.id)
        municipios = Municipios.objects.filter(provincia = perfil.municipio.provincia)
    else:
        municipios = Municipios.objects.all()
    franjas_horarias = FranjaHora.objects.filter(club = club)
    niveles_juego = Nivel.objects.filter(club=club).order_by('deporte__deporte')
    pistas = Pista.objects.filter(club=club).order_by('deporte__deporte', 'orden')
    deportes = Deporte.objects.all()
    data = {'perfil':perfil, 'club':club, 'form_admin_club':form_admin_club, 'provincias':provincias, 'municipio':municipio, 'pistas':pistas,
            'provincia':provincia, 'municipios':municipios, 'franjas_horarias':franjas_horarias, 'niveles_juego':niveles_juego, 'deportes':deportes}
    return render_to_response(ruta_administracion_club, data, context_instance=RequestContext(request))

def guardar_administracion(request):
    id_usuario = request.POST['user_id']
    accion = request.POST['action']
    club_id=request.POST['club_id']
    club = Club.objects.get(id=club_id)
    error = ""
    if accion == "club":
        club.nombre = request.POST['nombre']
        club.direccion = request.POST['direccion']
        try:
            municipio = Municipios.objects.get(id=request.POST['municipio'])
            club.municipio = municipio
        except Municipios.DoesNotExist:
            return administracion_club(request, id_usuario)
        club.descripcion = request.POST['descripcion']
        club.save()
    elif accion == "franja_hora":
        ids_eliminados = request.POST["ids_fh_eliminadas"]
        array_ids_eliminados = []
        if ids_eliminados != "":
            array_ids_eliminados = ids_eliminados.split(",", 1)
            for id in array_ids_eliminados:
                try:
                    fh = FranjaHora.objects.get(id = id)
                    fh.delete()
                except FranjaHora.DoesNotExist:
                    error = "No encontrada Franja hora"
        if not request.POST["inicio"] == "" and not request.POST["fin"] == "":
            new_fh = FranjaHora.objects.create(club = club, inicio=request.POST["inicio"], fin = request.POST["fin"])
            new_fh.save();
    elif accion == "deporte":
        if not request.POST["deporte"] == "" and not request.POST["num_jugadores"] == "":
            new_deporte = Deporte.objects.create(deporte=request.POST["deporte"], num_jugadores = request.POST["num_jugadores"])
            new_deporte.save();
    elif accion == "nivel_juego":
        ids_eliminados = request.POST["ids_nj_eliminadas"]
        array_ids_eliminados = []
        if ids_eliminados != "":
            array_ids_eliminados = ids_eliminados.split(",", 1)
            for id in array_ids_eliminados:
                try:
                    nj = Nivel.objects.get(id = id)
                    nj.delete()
                except Nivel.DoesNotExist:
                    error = "No encontrado Nivel de juego"
        if not request.POST["nj_deporte"] == "" and not request.POST["nj_nivel"] == "":
            d = Deporte.objects.get(id=request.POST["nj_deporte"])
            new_nj = Nivel.objects.create(club = club, deporte=d, nivel = request.POST["nj_nivel"])
            new_nj.save();
    elif accion == "pistas":
        ids_eliminados = request.POST["ids_pistas_eliminadas"]
        array_ids_eliminados = []
        if ids_eliminados != "":
            array_ids_eliminados = ids_eliminados.split(",", 1)
            for id in array_ids_eliminados:
                try:
                    p = Pista.objects.get(id = id)
                    p.delete()
                except Pista.DoesNotExist:
                    error = "No encontrada pista"
        if not request.POST["pista_orden"] == "" and not request.POST["pista_deporte"] == "" and not request.POST["pista_nombre"] == "":
            d = Deporte.objects.get(id=request.POST["pista_deporte"])
            new_p = Pista.objects.create(club = club, deporte=d, nombre = request.POST["pista_nombre"], orden = request.POST["pista_orden"])
            new_p.save();
    return administracion_club(request, id_usuario)



#****************************************************************************************************
#FUNCIONES AJAX
#****************************************************************************************************

def municipios_ajax(request):
	id_provincia = request.GET['provincia_id']
	municipios = Municipios.objects.filter(provincia__id = id_provincia)
	data = serializers.serialize('json', municipios,
		fields=('id', 'municipio'))
	return HttpResponse(data, mimetype='application/json')
