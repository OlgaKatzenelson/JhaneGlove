from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import os

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^glove/', include('JhaneGlove.urls', namespace="glove")),
    url(r'^', include('JhaneGlove.urls', namespace="glove")),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),


    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_URL }),
    url(r'^accounts/', include('registration.urls')),
    url("", include('django_socketio.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
