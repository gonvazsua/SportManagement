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

    #Usuarios
    url(r'^profile/', 'Core.views.perfil')
)
