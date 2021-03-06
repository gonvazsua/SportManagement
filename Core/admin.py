from django.contrib import admin
from Core.models import *
from django import forms

admin.site.register(Comunidades)
admin.site.register(Provincias)
admin.site.register(Municipios)
admin.site.register(Perfil)
admin.site.register(Rol)
admin.site.register(Nivel)
admin.site.register(Club)
admin.site.register(Sociedad)
admin.site.register(Pista)
admin.site.register(Deporte)
admin.site.register(Partido)
admin.site.register(Partido_perfiles)
admin.site.register(FranjaHora)
admin.site.register(PerfilRolClub)
admin.site.register(RutaTiempo)
admin.site.register(Notificacion)

#Caso para poner textarea en administracion para la clase Blog
class BlogForm(forms.ModelForm):
    texto = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Blog

class BlogAdmin(admin.ModelAdmin):
    form = BlogForm

admin.site.register(Blog, BlogAdmin)
