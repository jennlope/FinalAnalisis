from django.urls import path
from . import views

urlpatterns = [
    path('', views.capitulo2_form, name='capitulo2_form'),
    path('calcular/', views.calcular_resultados, name='calcular_resultados'),
    path('informe/', views.generar_informe, name='generar_informe'),
]