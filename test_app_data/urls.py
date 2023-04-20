from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import re_path

from .admin import site

urlpatterns = [re_path(r"^admin/", site.urls)]

urlpatterns = urlpatterns + staticfiles_urlpatterns()
