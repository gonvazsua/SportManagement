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
    url(r'^media/(?P<path>.*)$','django.views.static.serve', {'document_root':settings.MEDIA_ROOT,}),
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),

    #Pagina principal
    url(r'^$', 'Core.views.inicio'),
    url(r'^logout', 'Core.views.logout'),
    url(r'^recuperar_pass', 'Core.views.recuperar_pass'),

    ###########################################################
    ########## ADMINISTRADOR URLS
    ###########################################################

    #Inicio administrador
    url(r'^administrador/(?P<id_usuario>\d+)$', 'Core.views.perfil_administrador'),
    url(r'^administrador/(?P<id_usuario>\d+)/club/(?P<club_id>\d+)$', 'Core.views.cambio_club_administrador'),

    #Administradores
    url(r'^administrador/(?P<id_usuario>\d+)/administradores$', 'Core.views.administradores_club'),

    #Administracion de club
    url(r'^administrador/(?P<id_usuario>\d+)/club$', 'Core.views.administracion_club'),
    url(r'^guardar_administracion$', 'Core.views.guardar_administracion'),
    url(r'^guardar_franja_horaria$', 'Core.views.guardar_franja_horaria_ajax'),
    url(r'^guardar_niveles_juego$', 'Core.views.guardar_niveles_juego_ajax'),
    url(r'^guardar_pistas$', 'Core.views.guardar_pistas_ajax'),

    #Administracion Jugadores
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

    #Notificaciones
    url(r'^administrador/(?P<id_usuario>\d+)/notificaciones$', 'Core.views.notificaciones'),
    url(r'^marcar_leida$', 'Core.views.marcar_como_leida'),
    url(r'^aceptar_denegar_inscripcion$', 'Core.views.aceptar_denegar_inscripcion'),
    url(r'^comprobar_notificaciones', 'Core.views.comprobar_notificaciones'),

    #Eventos
    url(r'^administrador/(?P<id_usuario>\d+)/eventos/nuevo', 'Core.views.nuevo_evento'),
    url(r'^administrador/(?P<id_usuario>\d+)/eventos/(?P<id_evento>\d+)/editar', 'Core.views.editar_evento'),
    url(r'^administrador/(?P<id_usuario>\d+)/eventos/difusion', 'Core.views.difundir_evento'),
    url(r'^administrador/(?P<id_usuario>\d+)/eventos/eliminar', 'Core.views.eliminar_evento'),
    url(r'^administrador/(?P<id_usuario>\d+)/eventos', 'Core.views.eventos'),

    #AJAX
    url(r'^login', 'Core.views.login'),
    url(r'^registro', 'Core.views.registro'),
    url(r'^municipios_ajax/', 'Core.views.municipios_ajax'),
    url(r'^comprueba_disponibilidad_partido_ajax', 'Core.views.comprueba_disponibilidad_partido_ajax'),
    url(r'^nuevo_partido', 'Core.views.crear_partido_ajax'),
    url(r'^editar_partido', 'Core.views.editar_partido_ajax'),
    url(r'^baja_jugador_club', 'Core.views.baja_jugador_club'),

    ###########################################################
    ########## USUARIOS URLS
    ###########################################################

    #Inicio
    url(r'^usuario/(?P<id_usuario>\d+)$', 'Core.views.usuario_inicio'),
    url(r'^completar_datos_inicio', 'Core.views.completar_datos_inicio'),

    #Clubes
    url(r'^usuario/(?P<id_usuario>\d+)/clubes$', 'Core.views.usuario_mis_clubes'),
    url(r'^usuario/(?P<id_usuario>\d+)/buscador/clubes$', 'Core.views.usuario_buscador_clubes'),
    url(r'^buscador/clubes/inscripcion$', 'Core.views.usuario_club_inscripcion'),
    url(r'^buscador/clubes/baja$', 'Core.views.usuario_club_baja'),

    #Cuenta
    url(r'^usuario/(?P<id_usuario>\d+)/cuenta$', 'Core.views.usuario_mi_cuenta'),
    url(r'^clubes_niveles_cuenta', 'Core.views.clubes_niveles_cuenta'),
    url(r'^clubes_deportes_cuenta', 'Core.views.clubes_deportes_cuenta'),
    url(r'^eliminar_niveles_club_cuenta', 'Core.views.eliminar_niveles_club_cuenta'),
    url(r'^usuario/(?P<id_usuario>\d+)/eliminar$', 'Core.views.eliminar_cuenta_usuario'),

    #Partidos
    url(r'^usuario/(?P<id_usuario>\d+)/partidos/(?P<id_partido>\d+)$', 'Core.views.usuario_partido'),
    url(r'^usuario/(?P<id_usuario>\d+)/partidos/buscador$', 'Core.views.usuario_buscador_partido'),
    url(r'^inscripcion_partidos', 'Core.views.inscripcion_partidos'),
    url(r'^usuario/(?P<id_usuario>\d+)/partidos$', 'Core.views.usuario_mis_partidos'),
    url(r'^actualizar_franjas_club_ajax$', 'Core.views.actualizar_franjas_club_ajax'),

    ###########################################################
    ########## UTILES URLS
    ###########################################################
    url(r'^enviarEmail', 'Core.views.send_email'),
)
