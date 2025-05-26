from django.urls import path
from . import views

urlpatterns = [
    path('', views.formulario_capitulo2, name='capitulo2_formulario'),
    path('resultado/', views.resultado_capitulo2, name='capitulo2_resultado'),
    path('informe/', views.informe_capitulo2, name='capitulo2_informe'),
]
