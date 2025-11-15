from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GastoViewSet

# Creamos un router
router = DefaultRouter()

# Registramos nuestra vista. 'basename' es 'gasto'.
# Esto crea las URLs: /gastos/ y /gastos/<id>/
router.register(r'gastos', GastoViewSet, basename='gasto')

urlpatterns = [
    # Incluimos las URLs generadas por el router
    path('', include(router.urls)),
]
