from django.urls import path
from . import views

urlpatterns = [
    path('', views.capitulo1_view, name="capitulo1"),
]
