# reservas/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservaViewSet

# Creamos un router de DRF
router = DefaultRouter()

# Registramos nuestro ViewSet. DRF creará las rutas automáticamente:
# /reservas/ (GET, POST)
# /reservas/<id>/ (GET, PUT, PATCH, DELETE)
router.register('reservas', ReservaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]