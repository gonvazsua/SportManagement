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

class Roles(models.Model):
    tipo = models.CharField(max_length=50, verbose_name="Rol")

class Perfil(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='perfil')
    rol = models.ForeignKey(Roles, unique=True, related_name="rol")
    imagen = models.ImageField(upload_to='Imagenes', verbose_name='Imagen', blank=True)
    municipio = models.ForeignKey(Municipios, related_name='municipio_perfil', blank=True, null=True, on_delete=models.SET_NULL)
    def __unicode__(self):
		return self.user.first_name