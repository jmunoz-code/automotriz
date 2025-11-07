from django.urls import path
from .views import *

urlpatterns = [
    path('marca/',Clase1.as_view()),
    path('marca/<int:id>/',Clase2.as_view())
]


