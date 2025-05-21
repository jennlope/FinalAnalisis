# Capitulo2/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.formulario_capitulo2, name='formulario_capitulo2'),
    path('resultados/', views.formulario_capitulo2, name='resultados_capitulo2'),
    path('informe/', views.informe_capitulo2, name='informe_capitulo2'),
]
