"""
URL configuration for ProyectoAnalisisNumerico project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')


urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('capitulo1/', include('Capitulo1.urls')),
    path('capitulo2/', include('Capitulo2.urls')),
    path('capitulo3/', include('Capitulo3.urls')),
]
