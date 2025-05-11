from django.urls import path
from . import views

urlpatterns = [
    path('', views.formulario_interpolacion, name='interpolacion_formulario'),
    path('resultado/', views.resultado_interpolacion, name='interpolacion_resultado'),
    path('informe/', views.generar_informe, name='informe_interpolacion'),
]
