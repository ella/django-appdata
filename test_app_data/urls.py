import django

try:
    from django.conf.urls import include, url
except ImportError:
    from django.conf.urls.defaults import include, url

try:
    from django.conf.urls import patterns
except ImportError:
    try:
        from django.conf.urls.defaults import patterns
    except ImportError:
        pass

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .admin import site

list_of_urls = [
    url(r'^admin/', include(site.urls))
]

if django.VERSION > (1, 8):
    urlpatterns = list_of_urls
else:
    urlpatterns = patterns('', *list_of_urls)

urlpatterns = urlpatterns + staticfiles_urlpatterns()
