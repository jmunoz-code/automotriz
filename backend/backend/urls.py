from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

# openapi swagger
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import path

schema_view = get_schema_view(
    openapi.Info(
        title="Sistema FullSatck Automotriz django frameworkrest",
        default_version='V1',
        description="Api desarrollada para implementacion de Backend del sistema automotriz FullStack",
        terms_of_service="https://www.jaimemunoz.com/sistema",
        contact=openapi.Contact(email="jaimemunozoyarzun@gmail.com"),
        license=openapi.License("BSD license")
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('jmunoz_admin/', admin.site.urls),  # Add this line to include admin URLs
    path('api/', include('clientes.urls')),
    path('api/', include('tipoCombustible.urls')),
    path('api/', include('tipoVehiculo.urls')),
    path('api/', include('marca.urls')),
    path('api/', include('vehiculos.urls')),
    path('api/', include('tipo_pago.urls')),
    path('api/', include('trasmision.urls')),
    path('api/', include('costos.urls')),
    path('api/', include('seguridad.urls')),
    path('api/', include('vendedores.urls')),
    path('api/', include('contratos.urls')),
    path('api/', include('presupuesto.urls')),
    path('api/', include('pagoCuotas.urls')), 
    path('api/', include('detallePagoCuotas.urls')), 
    path('api/', include('generarCuotas.urls')), 
    path('api/', include('creditos.urls')),
    path('api/', include('reservas.urls')),
    path('api/', include('tipo_arriendo.urls')),
    path('api/', include('gastos.urls')),
    

    # esta son las documentaciones de todas laas APIS
    path('documentacion<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('documentacion/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)