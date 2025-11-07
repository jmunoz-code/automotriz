from django.urls import path
from .views import *

urlpatterns = [
    path('tipo_pago/',Clase1.as_view()),
    path('tipo_pago/<int:id>/',Clase2.as_view())
]


