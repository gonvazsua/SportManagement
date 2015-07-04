from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SportManagement.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    #Ruta de Imagenes
    url(r'^media/(?P<path>.*)$','django.views.static.serve',
          {'document_root':settings.MEDIA_ROOT,}),

    #Pagina principal
    url(r'^$', 'Core.views.inicio'),
    url(r'^logout', 'Core.views.logout'),

    #Usuarios
    url(r'^usuario/(?P<id_usuario>\d+)$', 'Core.views.perfil_usuario'),

    #Administracion de club
    url(r'^administrador/(?P<id_usuario>\d+)/club$', 'Core.views.administracion_club'),
    url(r'^guardar_administracion$', 'Core.views.guardar_administracion'),

    #Administracion Jugadores
    url(r'^administrador/(?P<id_usuario>\d+)$', 'Core.views.perfil_administrador'),
    url(r'^administrador/(?P<id_usuario>\d+)/jugadores$', 'Core.views.administrador_jugadores', name="administrador_jugadores"),
    url(r'^administrador/(?P<id_usuario>\d+)/jugadores/(?P<id_jugador>\d+)$', 'Core.views.administrador_perfil_jugador'),
    url(r'^administrador/(?P<id_usuario>\d+)/jugadores/nuevo$', 'Core.views.administrador_nuevo_jugador'),

    #Administracion Partidos
    url(r'^administrador/(?P<id_usuario>\d+)/nuevo$', 'Core.views.administrador_crear_partido'),
    url(r'^administrador/(?P<id_usuario>\d+)/partido/(?P<id_partido>\d+)/editar$', 'Core.views.administrador_editar_partido'),
    url(r'^administrador/(?P<id_usuario>\d+)/buscador$', 'Core.views.buscador_partidos'),

    #Administracion Estadisticas
    url(r'^administrador/(?P<id_usuario>\d+)/estadisticas$', 'Core.views.administrador_estadisticas'),

    #Administracion Estadisticas
    url(r'^administrador/(?P<id_usuario>\d+)/cuenta$', 'Core.views.administracion_cuenta'),

    #AJAX
    url(r'^login', 'Core.views.login'),
    url(r'^registro', 'Core.views.registro'),
    url(r'^municipios_ajax/', 'Core.views.municipios_ajax'),
    url(r'^comprueba_disponibilidad_partido_ajax', 'Core.views.comprueba_disponibilidad_partido_ajax'),
    url(r'^nuevo_partido', 'Core.views.crear_partido_ajax'),
    url(r'^editar_partido', 'Core.views.editar_partido_ajax'),
    url(r'^baja_jugador_club', 'Core.views.baja_jugador_club'),

    #Utiles
    url(r'^enviarEmail', 'Core.views.send_email'),
)
