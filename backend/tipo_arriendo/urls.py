from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipoArriendoViewSet

# Crea un router y registra nuestro viewset
router = DefaultRouter()
router.register('tipos-arriendo', TipoArriendoViewSet, basename='tipoarriendo')

# Las URLs de la API son determinadas automáticamente por el router.
urlpatterns = [
    path('', include(router.urls)),
]