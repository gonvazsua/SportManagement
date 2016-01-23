# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import *
from django.conf import settings

# Create your models here.
class Comunidades(models.Model):
	comunidad = models.CharField(max_length=255, verbose_name="Comunidad")
	def __unicode__(self):
		return self.comunidad

class Provincias(models.Model):
	provincia = models.CharField(max_length=255, verbose_name="Provincia")
	comunidad = models.ForeignKey(Comunidades, related_name='comunidad_provincia')
	def __unicode__(self):
		return self.provincia

class Municipios(models.Model):
	provincia = models.ForeignKey(Provincias, related_name='provincia_municipio')
	municipio = models.CharField(max_length=255, verbose_name="Municipio")
	latitud = models.FloatField(verbose_name="Latitud")
	longitud = models.FloatField(verbose_name="Longitud")
	def __unicode__(self):
		return self.municipio

class Rol(models.Model):
    rol = models.CharField(max_length=50, verbose_name="Rol")
    def __unicode__(self):
		return self.rol

class Deporte(models.Model):
    deporte = models.CharField(max_length=50, verbose_name="Deporte")
    num_jugadores = models.IntegerField(max_length=3, blank=True, null=True)
    def __unicode__(self):
		return self.deporte

class Sociedad(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    cif = models.CharField(max_length=50, verbose_name="CIF")
    def __unicode__(self):
		return self.nombre

class Club(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    municipio = models.ForeignKey(Municipios, related_name='municipio_club', blank=True, null=True, on_delete=models.SET_NULL)
    descripcion = models.TextField(max_length=400, verbose_name="Descripción")
    imagen = models.ImageField(upload_to='Imagenes', verbose_name='Imagen', blank=True)
    direccion = models.CharField(max_length=50, verbose_name="Dirección")
    def __unicode__(self):
		return self.nombre

class Pista(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    club = models.ForeignKey(Club, related_name="pista_club")
    deporte = models.ForeignKey(Deporte, related_name="pista_deporte")
    orden = models.IntegerField(verbose_name="Orden", null=True, blank=True)
    def __unicode__(self):
		return self.nombre + " (" +self.club.nombre + ")"

class Nivel(models.Model):
    nivel = models.CharField(verbose_name="Nivel", max_length=50)
    deporte = models.ForeignKey(Deporte)
    club = models.ForeignKey(Club)
    def __unicode__(self):
		return self.club.nombre + ": " + self.nivel + " - " + self.deporte.deporte

class Perfil(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='perfil_user')
    imagen = models.ImageField(upload_to='Imagenes', verbose_name='Imagen', blank=True)
    municipio = models.ForeignKey(Municipios, related_name='perfil_municipio', blank=True, null=True, on_delete=models.SET_NULL)
    telefono = models.CharField(max_length=12, verbose_name="Teléfono", blank=True)
    deporteNivel = models.ManyToManyField(Nivel)
    def __unicode__(self):
		return self.user.first_name + ", " + self.user.last_name
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
		return self.perfil.user.first_name + " " + self.club.nombre + " - " + self.rol.rol

class FranjaHora(models.Model):
    club = models.ForeignKey(Club, related_name="franja_horaria_club", verbose_name="Club")
    inicio = models.TimeField(auto_now=False, verbose_name="Hora inicio")
    fin = models.TimeField(auto_now=False, verbose_name="Hora fin")
    #estado = models.NullBooleanField()
    def __unicode__(self):
		return self.club.nombre + ": " + self.inicio.strftime('%H:%M:%S') + " - " + self.fin.strftime('%H:%M:%S')

class Partido(models.Model):
    franja_horaria = models.ForeignKey(FranjaHora, related_name="partido_franja_horaria", verbose_name="Franja horaria")
    fecha = models.DateField(auto_now=False, verbose_name="Fecha")
    perfiles = models.ManyToManyField(Perfil, related_name="partido_perfiles")
    pista = models.ForeignKey(Pista, related_name="partido_pista")
    creado_por = models.ForeignKey(Perfil)
    visible = models.BooleanField(verbose_name="Es visible")
    def __unicode__(self):
		return "Fecha: " + self.fecha.strftime('%d-%m-%Y') + ", Hora:" + self.franja_horaria.inicio.strftime('%H:%M:%S')
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


class RutaTiempo(models.Model):
    municipio = models.ForeignKey(Municipios)
    ruta = models.TextField(blank=True)

class InscripcionesEnClub(models.Model):
    club = models.ForeignKey(Club, verbose_name="Club")
    jugador = models.ForeignKey(Perfil, verbose_name="Perfil")
    estado = models.NullBooleanField(verbose_name="Estado aceptación") #None=Pendiente, 1=Aceptada, 0=Denegada
    def __unicode__(self):
		return "Club: "+self.club.nombre

class InscripcionesEnPartido(models.Model):
    partido = models.ForeignKey(Partido, verbose_name="Partido")
    jugador = models.ForeignKey(Perfil, verbose_name="Perfil")
    estado = models.NullBooleanField(verbose_name="Estado aceptación") #None=Pendiente, 1=Aceptada, 0=Denegada
    def __unicode__(self):
		return "Club: "+self.club.nombre

class Notificacion(models.Model):
    leido = models.BooleanField(verbose_name="Estado lectura")
    fecha = models.DateField(auto_now=False, verbose_name="Fecha")
    inscripcionEnClub = models.ForeignKey(InscripcionesEnClub, null=True, blank=True)
    inscripcionEnPartido = models.ForeignKey(InscripcionesEnPartido, null=True, blank=True)
    destino = models.IntegerField(max_length=1, verbose_name="Destino")
    def __unicode__(self):
		return "Club: "+self.fecha