from django.urls import path
from .views import *

urlpatterns = [
    path('trasmision/',Clase1.as_view()),
    path('trasmision/<int:id>/',Clase2.as_view())
]


