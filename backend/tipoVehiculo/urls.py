from django.urls import path
from .views import *

urlpatterns = [
    path('tipoVehiculo/',Clase1.as_view()),
    path('tipoVehiculo/<int:id>/',Clase2.as_view())
]


