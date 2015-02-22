# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

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
    tipo = models.CharField(max_length=50, verbose_name="Rol")
    def __unicode__(self):
		return self.tipo

class Nivel(models.Model):
    nivel = models.CharField(max_length=50, verbose_name="Nivel")
    def __unicode__(self):
		return self.nivel

class Deporte(models.Model):
    deporte = models.CharField(max_length=50, verbose_name="Deporte")
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
    sociedad = models.ForeignKey(Sociedad, unique=True, related_name="club_sociedad")
    def __unicode__(self):
		return self.nombre

class Pista(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    club = models.ForeignKey(Club, related_name="pista_club", unique=True)
    deporte = models.ForeignKey(Deporte, related_name="pista_deporte", unique=True)
    def __unicode__(self):
		return self.nomre + " (" +self.club.nombre + ")"

class Perfil(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='perfil_user')
    rol = models.ForeignKey(Rol, unique=True, related_name="perfil_rol")
    nivel = models.ForeignKey(Nivel, unique=True, related_name="perfil_nivel")
    imagen = models.ImageField(upload_to='Imagenes', verbose_name='Imagen', blank=True)
    municipio = models.ForeignKey(Municipios, related_name='perfil_municipio', blank=True, null=True, on_delete=models.SET_NULL)
    clubes = models.ManyToManyField(Club, related_name="perfil_clubes")
    def __unicode__(self):
		return self.user.first_name + " " + self.user.last_name

class Partido(models.Model):
    pista = models.ForeignKey(Pista, unique=True, related_name="pista", verbose_name="Pista")
    hora = models.TimeField(auto_now=False, verbose_name="Hora")
    fecha = models.DateField(auto_now=False, verbose_name="Fecha")
    perfiles = models.ManyToManyField(Perfil, related_name="partido_perfiles")
    def __unicode__(self):
		return "Pista: " + self.pista.nombre + ", Fecha: " + self.fecha + ", Hora:" + self.hora