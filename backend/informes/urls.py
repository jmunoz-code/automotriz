from django.urls import path
from .views import InformeMensualAPIView

urlpatterns = [
    # Esta será la ruta: api/informes/reporte-mensual/
    path('informes/reporte-mensual/', InformeMensualAPIView.as_view(), name='reporte-mensual'),
]