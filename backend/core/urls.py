"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import sys

from django import conf
from django.contrib import admin
from django.urls import include, path
from django.views.debug import technical_500_response
from django.views.defaults import server_error


def handler500(request):
    if request.user.is_superuser:
        return technical_500_response(request, *sys.exc_info())
    else:
        return server_error(request)


urlpatterns = [
    path("admin/", admin.site.urls),
]

if conf.settings.DEBUG:
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns
