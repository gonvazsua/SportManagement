# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import *
from django.conf import settings
import uuid
import os

#Evitar que imagenes se dupliquen con el mismo nombre
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('Imagenes', filename)

#Evitar que imagenes se dupliquen en el blog
def get_file_path_blog(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('Blog', filename)

# Create your models here.
class Comunidades(models.Model):
	comunidad = models.CharField(max_length=255, verbose_name="Comunidad")
	def __unicode__(self):
		return unicode(self.comunidad)

class Provincias(models.Model):
	provincia = models.CharField(max_length=255, verbose_name="Provincia")
	comunidad = models.ForeignKey(Comunidades, related_name='comunidad_provincia')
	def __unicode__(self):
		return unicode(self.provincia)

class Municipios(models.Model):
	provincia = models.ForeignKey(Provincias, related_name='provincia_municipio')
	municipio = models.CharField(max_length=255, verbose_name="Municipio")
	latitud = models.FloatField(verbose_name="Latitud")
	longitud = models.FloatField(verbose_name="Longitud")
	def __unicode__(self):
		return unicode(self.municipio)

class Rol(models.Model):
    rol = models.CharField(max_length=50, verbose_name="Rol")
    def __unicode__(self):
		return unicode(self.rol)

class Deporte(models.Model):
    deporte = models.CharField(max_length=50, verbose_name="Deporte")
    num_jugadores = models.IntegerField(max_length=3, blank=True, null=True)
    def __unicode__(self):
		return unicode(self.deporte)

class Sociedad(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    cif = models.CharField(max_length=50, verbose_name="CIF")
    def __unicode__(self):
		return unicode(self.nombre)

class Club(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    municipio = models.ForeignKey(Municipios, related_name='municipio_club', blank=True, null=True, on_delete=models.SET_NULL)
    descripcion = models.TextField(max_length=400, verbose_name="Descripción")
    imagen = models.ImageField(upload_to=get_file_path, verbose_name='Imagen', blank=True)
    direccion = models.CharField(max_length=50, verbose_name="Dirección")
    facebook = models.CharField(max_length=200, verbose_name="Facebook", blank=True, null=True)
    def __unicode__(self):
		return unicode(self.nombre)

class Pista(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    club = models.ForeignKey(Club, related_name="pista_club")
    deporte = models.ForeignKey(Deporte, related_name="pista_deporte")
    orden = models.IntegerField(verbose_name="Orden", null=True, blank=True)
    def __unicode__(self):
		return unicode(self.nombre + " (" +self.club.nombre + ")")

class Nivel(models.Model):
    nivel = models.CharField(verbose_name="Nivel", max_length=50)
    deporte = models.ForeignKey(Deporte)
    club = models.ForeignKey(Club)
    def __unicode__(self):
		return unicode(self.club.nombre + ": " + self.nivel + " - " + self.deporte.deporte)

class Perfil(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='perfil_user')
    imagen = models.ImageField(upload_to=get_file_path, verbose_name='Imagen', blank=True)
    municipio = models.ForeignKey(Municipios, related_name='perfil_municipio', blank=True, null=True, on_delete=models.SET_NULL)
    telefono = models.CharField(max_length=12, verbose_name="Teléfono", blank=True)
    deporteNivel = models.ManyToManyField(Nivel)
    def __unicode__(self):
		return unicode(self.user.first_name + ", " + self.user.last_name)
    def deportes(self):
        deportes = []
        for n in self.deporteNivel.all():
            deportes.append(n.deporte)
        return deportes
    def clubes(self):
        return Club.objects.filter(id__in = PerfilRolClub.objects.values_list('club_id', flat=True).filter(perfil=self))
    def es_administrador(self):
        return PerfilRolClub.objects.filter(perfil=self, rol=settings.ROL_ADMINISTRADOR).exists()

class PerfilRolClub(models.Model):
    rol = models.ForeignKey(Rol)
    club = models.ForeignKey(Club)
    perfil = models.ForeignKey(Perfil)
    def __unicode__(self):
		return unicode(self.perfil.user.first_name + " " + self.club.nombre + " - " + self.rol.rol)

class FranjaHora(models.Model):
    club = models.ForeignKey(Club, related_name="franja_horaria_club", verbose_name="Club")
    inicio = models.TimeField(auto_now=False, verbose_name="Hora inicio")
    fin = models.TimeField(auto_now=False, verbose_name="Hora fin")
    #estado = models.NullBooleanField()
    def __unicode__(self):
		return unicode(self.club.nombre + ": " + self.inicio.strftime('%H:%M:%S') + " - " + self.fin.strftime('%H:%M:%S'))

class Partido(models.Model):
    franja_horaria = models.ForeignKey(FranjaHora, related_name="partido_franja_horaria", verbose_name="Franja horaria")
    fecha = models.DateField(auto_now=False, verbose_name="Fecha")
    #perfiles = models.ManyToManyField(Perfil, related_name="partido_perfiles")
    perfiles = models.ManyToManyField(Perfil, through="Partido_perfiles", null=True)
    pista = models.ForeignKey(Pista, related_name="partido_pista")
    creado_por = models.ForeignKey(Perfil, related_name="creado_por")
    visible = models.BooleanField(verbose_name="Es visible")
    def __unicode__(self):
		return unicode("Fecha: " + self.fecha.strftime('%d-%m-%Y') + ", Hora:" + self.franja_horaria.inicio.strftime('%H:%M:%S'))
    def club(self):
        return self.pista.club
    def num_perfiles(self):
        return self.perfiles.count()
    def max_perfiles(self):
        return self.pista.deporte.num_jugadores
    def bloqueado(self):
        if self.fecha < datetime.now().date()\
                or (self.fecha < datetime.now().date() and self.franja_horaria.fin < datetime.now().time()):
            return True
        else:
            return False
    def es_partido_evento(self):
        es_evento = False
        partidos = Evento.objects.filter(club=self.club(), fecha=self.fecha).values_list('partidos__pk', flat=True)
        if self.id in partidos:
            es_evento = True
        return es_evento
    def evento_nombre(self):
        nombre = ""
        eventos = Evento.objects.filter(club=self.club(), fecha=self.fecha)
        for evento in eventos:
            if self in evento.partidos.all():
                nombre = evento.nombre
        return nombre

class Partido_perfiles(models.Model):
    partido = models.ForeignKey(Partido)
    perfil = models.ForeignKey(Perfil)
    pago = models.FloatField(verbose_name="Pago", null=True)
    fecha_pago = models.DateTimeField(verbose_name="Fecha", auto_now=False, null=True)
    def __unicode__(self):
		return unicode("Perfil: " + self.perfil)

class RutaTiempo(models.Model):
    municipio = models.ForeignKey(Municipios)
    ruta = models.TextField(blank=True)

class Notificacion(models.Model):
    leido = models.BooleanField(verbose_name="Estado lectura")
    fecha = models.DateField(auto_now=True, verbose_name="Fecha")
    tipo = models.IntegerField(max_length=1, verbose_name="Tipo") #Ver settings
    destino = models.IntegerField(max_length=1, verbose_name="Destino") #0 = Club; 1 = Jugador
    partido = models.ForeignKey(Partido, verbose_name="Partido", blank=True, null=True)
    jugador = models.ForeignKey(Perfil, verbose_name="Perfil", blank=True, null=True)
    estado = models.NullBooleanField(verbose_name="Estado aceptación", blank=True, null=True) #None=Pendiente, 1=Aceptada, 0=Denegada
    club = models.ForeignKey(Club, verbose_name="Club", blank=True, null=True)
    def __unicode__(self):
		return unicode("Club: "+str(self.fecha))

class Evento(models.Model):
    partidos = models.ManyToManyField(Partido, null=True, blank=True)
    club = models.ForeignKey(Club, null=True, blank=True)
    fecha = models.DateField(auto_now=False, verbose_name="Fecha")
    descripcion = models.TextField(max_length=400, verbose_name="Descripción")
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    hora = models.TimeField(auto_now = False, verbose_name='Hora del evento', null=True, blank=True)
    imagen = models.ImageField(upload_to=get_file_path, verbose_name='Imagen', blank=True)
    creado_por = models.ForeignKey(Perfil, null=True, blank=True)
    creado_el = models.DateField(auto_now=True, verbose_name="Fecha")
    def __unicode__(self):
		return unicode("Evento: "+self.nombre+". Club: " + self.club.nombre)
    def bloqueado(self):
        if self.fecha < datetime.now().date():
            return True
        else:
            return False

class Blog(models.Model):
    fecha = models.DateField(auto_now=True, verbose_name="Fecha")
    creado_por = models.ForeignKey(Perfil, null=True, blank=True)
    titulo = models.CharField(max_length=300, verbose_name="Titulo")
    texto = models.CharField(max_length=2000, verbose_name="Texto")
    imagen = models.ImageField(upload_to=get_file_path_blog, verbose_name='Imagen', blank=True, null=True)
    def __unicode__(self):
		return unicode("Entrada blog: "+str(self.fecha))

class ComentarioPartido(models.Model):
    fecha = models.DateTimeField(auto_now=True, verbose_name="Fecha")
    creado_por = models.ForeignKey(Perfil, null=True, blank=True)
    texto = models.CharField(max_length=150, verbose_name="Texto")
    partido = models.ForeignKey(Partido, null=False, blank=False)
    def __unicode__(self):
		return unicode("Comentario: "+str(self.id))


