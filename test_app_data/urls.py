
from django.conf.urls import url


from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .admin import site

urlpatterns = [
    url(r'^admin/', site.urls)
]

urlpatterns = urlpatterns + staticfiles_urlpatterns()
