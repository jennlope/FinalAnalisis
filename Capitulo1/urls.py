from django.urls import path
from . import views

urlpatterns = [
    path('', views.capitulo1_view, name="capitulo1"),
    path('', views.comparar_metodos, name="comparar_metodos"),
]
