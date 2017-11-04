
from django.conf.urls import include, url


from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .admin import site

urlpatterns = [
    url(r'^admin/', include(site.urls))
]

urlpatterns = urlpatterns + staticfiles_urlpatterns()
