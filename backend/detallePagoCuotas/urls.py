# urls.py
from django.urls import path
from .views import DetallePagoCuotasAPI, DetallePagoCuotasIndividualAPI, EliminarDetallesPorRutPatenteAPI

urlpatterns = [
    path('detallepago/', DetallePagoCuotasAPI.as_view(), name='detalle_pago_list_create'),
    path('detallepago/<int:id>/', DetallePagoCuotasIndividualAPI.as_view(), name='detalle_pago_detail'),
    #path('detallepago/<str:rut>/<str:patente>/<int:numero_cuota>/', DetallePagoCuotasIndividualAPI.as_view(), name='detalle_pago_detail'),
    path('detallepago/<str:rut>/<str:patente>/<int:numero_cuota>/', DetallePagoCuotasIndividualAPI.as_view(), name='detallepago_list_by_cuota'),
    
    # Ruta específica para eliminar todos los detalles por RUT y PATENTE
    path('detallepagocuotas/', EliminarDetallesPorRutPatenteAPI.as_view(), name='detallepago_eliminar_por_rut_patente'),
]