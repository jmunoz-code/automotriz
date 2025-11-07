from django.urls import path

from clientes.views import Clase2
from .views import InformeVehiculosPropiedad, Clase1, Clase2, TotalVehiculosSinPresupuesto


urlpatterns = [
    path('vehiculos/',Clase1.as_view()),
    path('vehiculos/total-sin-presupuesto/', TotalVehiculosSinPresupuesto.as_view()),
    path('vehiculos/<str:patente>/',Clase2.as_view()),
    # NUEVA RUTA PARA EL INFORME SOLICITADO
    path('vehiculos/informe/propiedad-automotriz/', InformeVehiculosPropiedad.as_view()),
    
]


