from django.urls import path
from .views import *

urlpatterns = [
    path('',Clase1.as_view()),
    path('<int:id>',Clase2.as_view())
]


