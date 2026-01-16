from django.urls import path
from .views import *

urlpatterns = [
    path('presupuesto/', Clase1.as_view()),  # La ruta ahora es la raíz
    path('presupuesto/<int:id>/',Clase2.as_view()), # Nueva ruta para buscar por RUT
    path('presupuesto/buscar/', PresupuestoListAPIView.as_view()), 
    path('presupuesto/<str:patente>/',Clase3.as_view()), # Nueva ruta para buscar por RUT


     # --- NUEVA RUTA DEDICADA PARA LA MODIFICACIÓN DE ESTADO POR ID ---
    path('presupuesto/estado/<int:id>/', PresupuestoEstadoUpdateAPIView.as_view()), 
    
    # --- RUTA PARA ACTUALIZAR ESTADO POR RUT Y PATENTE ---
    path('presupuesto/<str:rut>/<str:patente>/', PresupuestoEstadoByRutPatenteAPIView.as_view()),
    
         
]
