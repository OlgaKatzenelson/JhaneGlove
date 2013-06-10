from django.conf.urls import patterns, include, url

from django.contrib import admin
import settings
import os

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^glow/', include('JhaneGlove.urls', namespace="glow")),
    url(r'^', include('JhaneGlove.urls', namespace="glow")),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),


    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_URL }),
    url(r'^accounts/', include('registration.urls')),
)
