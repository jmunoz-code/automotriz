from django.urls import path
from .views import *

urlpatterns = [
    path('tipoCombustible/',Clase1.as_view()),
    path('tipoCombustible/<int:id>/',Clase2.as_view())
]


