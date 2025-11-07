from django.urls import path
from .views import *

urlpatterns = [
    path('valorizacion/',Clase1.as_view()),
    path('valorizacion/<int:id>/',Clase2.as_view())
]


