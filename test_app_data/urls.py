try:
    from django.conf.urls import patterns, include, url
except ImportError:
    from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .admin import site

urlpatterns = patterns('',
    url(r'^admin/', include(site.urls)),
) + staticfiles_urlpatterns()
