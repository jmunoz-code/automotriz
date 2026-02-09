from django.urls import path
from .views import *

urlpatterns = [
    # Rutas más específicas primero (con texto literal en la URL)
    path('presupuesto/', Clase1.as_view()),
    path('presupuesto/buscar/', PresupuestoListAPIView.as_view()), 
    path('presupuesto/estado/<int:id>/', PresupuestoEstadoUpdateAPIView.as_view()), 
    
    # Rutas con parámetros int (más específicas que str)
    path('presupuesto/<int:id>/', Clase2.as_view()),  # GET, PUT, DELETE por ID
    
    # Rutas con múltiples parámetros
    path('presupuesto/<str:rut>/<str:patente>/', PresupuestoEstadoByRutPatenteAPIView.as_view()),
    
    # Rutas con parámetro str al final (menos específica, captura todo lo demás)
    path('presupuesto/<str:patente>/', Clase3.as_view()),  # GET por patente
]
