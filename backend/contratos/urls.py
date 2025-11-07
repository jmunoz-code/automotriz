from django.urls import path
from .views import *

urlpatterns = [
    path('contratos/', Clase1.as_view()),  # La ruta ahora es la raíz
    path('contratos/<int:id>/',Clase2.as_view()), # Nueva ruta para buscar por RUT
    path('contratos/<str:rut>/<str:patente>/',Clase2.as_view()), # Nueva ruta para buscar por RUT
      
]
