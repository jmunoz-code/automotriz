# creditos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Esta ruta completa la URL a: /api/creditos/buscar/
    path('creditos/buscar/', views.buscar_creditos_rapido, name='creditos_buscar_rapido'),
]