from django.conf.urls.defaults import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .admin import site

urlpatterns = patterns('',
    url(r'^admin/', include(site.urls)),
) + staticfiles_urlpatterns()
