# mi_app/urls.py (o el urls.py principal de tu proyecto si es ahí donde están)

from django.urls import path
# Importa las vistas necesarias
from .views import GenerarCuotasAPIView

urlpatterns = [
    path('generarCuotas/',GenerarCuotasAPIView.as_view()),
]


