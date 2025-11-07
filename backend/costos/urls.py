from django.urls import path
from costos.views import *

urlpatterns = [
    
    path('costos/', Clase1.as_view()),  # La ruta ahora es la raíz
    path('costos/<int:id>/', Clase2.as_view()), #obtiene la suma total por patente
    path('costos/<str:patente>/', Clase3.as_view(), name='costos-list-create'),
    path('costos/filtro/<str:patente>/', Clase4.as_view(), name='costos'),
    
   
    

]
