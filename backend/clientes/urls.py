from django.urls import path
from .views import *

urlpatterns = [
    path('clientes/', Clase1.as_view()),  # La ruta ahora es la raíz
    path('clientes/<str:rut>/',Clase2.as_view()), # Nueva ruta para buscar por RUT
]
