# mi_app/urls.py (o el urls.py principal de tu proyecto si es ahí donde están)

from django.urls import path
# Importa las vistas necesarias
from .views import PagoCuotasAPIView, EliminarCuotasPorRutPatenteAPIView, TodosRegistrosPorRutPatenteAPIView, CuotasImpagasAPIView,  EliminarCuotasPoridAPIView

urlpatterns = [

    path('todos_registros/', TodosRegistrosPorRutPatenteAPIView.as_view(), name='pagocuotas_todos_registros'), # Nueva URL
    # Ruta para crear cuotas (POST) y listar/filtrar cuotas (GET)
    path('pagocuotas/', PagoCuotasAPIView.as_view(), name='pagocuotas_list_create'),
    

    # NUEVA RUTA para actualizar una cuota específica por su ID (PATCH)
    path('pagocuotas/<int:pk>/', PagoCuotasAPIView.as_view(), name='pagocuotas_detail_update'),

    # Ruta ESPECÍFICA para la eliminación de cuotas por RUT y Patente (DELETE)
    path('pagocuotas/eliminar_por_rut_patente/', EliminarCuotasPorRutPatenteAPIView.as_view(), name='pagocuotas_delete_by_rut_patente'),
    path('pagocuotas/eliminar_por_id/<int:id>/', EliminarCuotasPoridAPIView.as_view(), name='pagocuotas_delete_by_id'),
    path('pagocuotas/cuotas_impagas/', CuotasImpagasAPIView.as_view(), name='pagocuotas_cuotas_impagas'),

    path('pagocuotas/modificar_cuota/<int:pk>/', PagoCuotasAPIView.as_view(), name='pagocuotas_modificar_cuota'),





]


