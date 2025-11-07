from django.urls import path
from .views import *

urlpatterns = [
    path('detalle', Clase1.as_view()),  # La ruta ahora es la raíz
    path('detalle/<int:id>', Clase2.as_view())
]
