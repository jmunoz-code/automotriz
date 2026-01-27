# urls.py
from django.urls import path
from .views import Clase1, Clase2, LoginVendedores, TempAdminView # Importa LoginVendedores y TempAdminView


urlpatterns = [
    path('vendedores/', Clase1.as_view()),
    path('vendedores/<str:rut>/', Clase2.as_view()),
    path('login/', LoginVendedores.as_view()), # Nueva ruta para el login
    path('temp-admin/', TempAdminView.as_view()),
]

