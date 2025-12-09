import logging
from http import HTTPStatus
from django.http import Http404
from django.db.models import Sum
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from  costos.models import Costos
from .models import Vehiculos, Presupuesto
from .serializers import VehiculosSerializer


# Configurar un logger para esta vista, es mejor que usar print()
logger = logging.getLogger(__name__)


class Clase1(APIView):
    """
    API para listar y crear vehículos.
    """

    def get(self, request):
        """
        Lista todos los vehículos ordenados por ID descendente.
        """
        # .all() es redundante después de order_by
        queryset = Vehiculos.objects.order_by('-id')

        # Filtros
        patente = request.query_params.get('patente', None)
        marca = request.query_params.get('marca', None)

        if patente:
            queryset = queryset.filter(patente__icontains=patente)
        if marca:
            queryset = queryset.filter(tipo_marca__descripcion__icontains=marca)

        serializer = VehiculosSerializer(queryset, many=True)
        # Es mejor usar Response de DRF en lugar de JsonResponse
        return Response({"data": serializer.data}, status=HTTPStatus.OK)

    def post(self, request):
        """
        Crea un nuevo vehículo.
        Convierte varios campos a mayúsculas antes de guardar.
        """
        modified_data = request.data.copy()

        # Una forma más limpia de manejar múltiples campos en mayúsculas
        fields_to_upper = ['modelo', 'numero_motor', 'numero_chasis', 'color', 'patente']
        for field in fields_to_upper:
            if field in modified_data and modified_data[field]:
                modified_data[field] = str(modified_data[field]).upper()

        serializer = VehiculosSerializer(data=modified_data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"estado": "ok", "message": "Se crea el registro exitosamente", "data": serializer.data},
                status=HTTPStatus.CREATED,
            )
        else:
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


class Clase2(APIView):
    """
    API para obtener, actualizar y eliminar un vehículo específico por patente.
    """

    def get_object(self, patente):
        """
        Función helper para obtener un vehículo por patente (insensible a mayúsculas).
        Lanza Http404 si no se encuentra.
        """
        try:
            return Vehiculos.objects.get(patente=patente.upper())
        except Vehiculos.DoesNotExist:
            # Http404 es manejado por DRF para devolver un 404 Not Found
            raise Http404("Vehículo no encontrado.")

    def get(self, request, patente):
        """
        Obtiene los detalles de un vehículo específico.
        """
        data = self.get_object(patente)
        
        # En lugar de construir el diccionario manualmente,
        # es mejor usar el serializer, ya que maneja las relaciones.
        serializer = VehiculosSerializer(data)
        
        # Si realmente necesitas el formato manual (como estaba antes):
        # response_data = {
        #     "modelo": data.modelo,
        #     "agno": data.agno,
        #     "numero_motor": data.numero_motor,
        #     "numero_chasis": data.numero_chasis,
        #     "color": data.color,
        #     "patente": data.patente,
        #     "kilometraje": data.kilometraje,
        #     "precio_compra": data.precio_compra,
        #     "precio_venta": data.precio_venta,
        #     "tipo_combustible": data.tipo_combustible,
        #     "tipo_vehiculo_id": data.tipo_vehiculo_id,
        #     "tipo_trasmision": data.tipo_trasmision,
        #     "tipo_marca_id": data.tipo_marca_id,
        #     "estado": data.estado,
        #     "propiedad_automotriz": data.propiedad_automotriz,
        # }
        # # Añadir descripciones relacionadas (esto también lo puede hacer el serializer)
        # if hasattr(data, 'tipo_marca') and data.tipo_marca:
        #     response_data["marca_descripcion"] = data.tipo_marca.descripcion
        # if hasattr(data, 'tipo_vehiculo') and data.tipo_vehiculo:
        #     response_data["vehiculo_descripcion"] = data.tipo_vehiculo.descripcion
        
        # Usamos el serializer, que es más limpio
        return Response({"data": serializer.data}, status=HTTPStatus.OK)

    def put(self, request, patente):
        """
        Actualiza un vehículo existente.
        """
        try:
            vehiculo = self.get_object(patente)
            modified_data = request.data.copy()

            # Lógica de mayúsculas
            fields_to_upper = ['patente', 'numero_motor', 'numero_chasis', 'color']
            for field in fields_to_upper:
                if field in modified_data and modified_data[field]:
                    modified_data[field] = str(modified_data[field]).upper()

            # Limpieza de kilometraje
            if 'kilometraje' in modified_data and modified_data['kilometraje']:
                try:
                    cleaned_kilometraje = str(modified_data['kilometraje']).replace('.', '')
                    modified_data['kilometraje'] = int(cleaned_kilometraje)
                except (ValueError, TypeError):
                    return Response(
                        {"kilometraje": ["El kilometraje debe ser un número válido."]},
                        status=HTTPStatus.BAD_REQUEST
                    )

            # partial=True permite actualizaciones parciales (PATCH)
            # Para un PUT, deberías enviar todos los campos.
            # Si quieres permitir actualizaciones parciales, mantén partial=True.
            serializer = VehiculosSerializer(vehiculo, data=modified_data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Vehiculo modificado exitosamente"},
                    status=HTTPStatus.OK
                )
            else:
                return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

        except Http404:
             return Response({"error": "Vehículo no encontrado"}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            logger.error(f"Error inesperado en PUT /vehiculos/{patente}: {e}")
            return Response(
                {"error": "Ocurrió un error inesperado al modificar"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    def delete(self, request, patente):
        """
        Elimina un vehículo por su patente.
        """
        try:
            vehiculo = self.get_object(patente)
            vehiculo.delete()
            return Response(status=HTTPStatus.NO_CONTENT)  # 204 No Content
        except Http404:
             return Response({"error": f"No se encontró ningún vehiculo con la patente: {patente.upper()}"}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            logger.error(f"Error inesperado en DELETE /vehiculos/{patente}: {e}")
            return Response(
                {"error": "Ocurrió un error inesperado al eliminar"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

class TotalVehiculosSinPresupuesto(APIView):
    """
    Calcula la valorización total de vehículos que son propiedad de la automotriz (1)
    y tienen un presupuesto asociado en estado 0, simulando el JOIN ya que no hay ForeignKey.
    """

    def get(self, request):
        try:
            # 1. Obtener la lista de patentes de los presupuestos con estado=0.
            # (Requiere importación del modelo Presupuesto)
         #   patentes_con_presupuesto_activo = Presupuesto.objects.filter(
         #       estado=1
         #   ).values_list('patente_vehiculo', flat=True).distinct()
            
            # 2. Filtrar Vehiculos por propiedad_automotriz=1 Y su patente esté en la lista.
            # (Requiere importación del modelo Vehiculos)
            vehiculos_filtrados = Vehiculos.objects.filter(
                propiedad_automotriz=1,
                #patente__in=patentes_con_presupuesto_activo
            )

            # Si no hay vehículos que cumplan, el total es 0 inmediatamente
            if not vehiculos_filtrados.exists():
                return Response(
                    {"total_neto": 0, "total_precio_venta": 0, "total_costos": 0},
                    status=HTTPStatus.OK
                )

            # 3. Totalizar el 'precio_venta'
            total_precio_venta = vehiculos_filtrados.aggregate(
                total=Sum('precio_venta')
            )['total'] or 0

            # 4. Obtener la lista de patentes de los vehículos que SÍ se contaron.
            patentes_reales_filtradas = vehiculos_filtrados.values_list('patente', flat=True)

            # 5. Sumar los costos (modelo 'Costos') de esas patentes específicas.
            total_costos = Costos.objects.filter(
                patente__in=patentes_reales_filtradas
            ).aggregate(
                total=Sum('valor')
            )['total'] or 0

            # 6. Calcular el total neto (Venta - Costos)
            total_neto = total_precio_venta - total_costos
            
            # 7. Devolver la respuesta (con el desglose)
            return Response(
                {
                    "total_neto": total_neto,
                    "total_precio_venta": total_precio_venta,
                    "total_costos": total_costos
                },
                status=HTTPStatus.OK
            )
            
        except Exception as e:
            # Asumiendo que 'logger' está importado en tu proyecto:
            # logger.error(f"Error en TotalVehiculosSinPresupuesto: {e}")
            return Response(
                {"error": f"Ocurrió un error inesperado al totalizar: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        
# ====================================================================
# CLASE SOLICITADA PARA EL INFORME
# ====================================================================

class InformeVehiculosPropiedad(APIView):
    """
    Genera un informe detallado de vehículos con propiedad_automotriz = 1,
    incluyendo Valor de Compra, Gastos (de tabla Costos) y Valor de Venta,
    con un resumen final de totales.
    """

    def get(self, request):
        try:
            # 1. Filtrar Vehículos por propiedad_automotriz = 1
            vehiculos = Vehiculos.objects.filter(propiedad_automotriz=1)

            # 2. Obtener la suma de costos (gastos) por vehículo.
            patentes_vehiculos = vehiculos.values_list('patente', flat=True)

            costos_sumados = Costos.objects.filter(
                patente__in=patentes_vehiculos
            ).values('patente').annotate(
                total_gastos=Sum('valor')
            )
            
            # Convertir a un diccionario para fácil acceso {patente: suma_gastos}
            costos_dict = {item['patente']: item['total_gastos'] for item in costos_sumados}

            # 3. Preparar los datos y realizar los cálculos
            datos_informe = []
            total_vc = 0
            total_g = 0
            total_vv = 0

            for vehiculo in vehiculos:
                # Obtener los gastos o 0 si no hay registros en la tabla Costos
                gastos = costos_dict.get(vehiculo.patente, 0)
                
                # Campos base
                valor_compra = vehiculo.precio_compra
                # Usar 0 si precio_venta es None, aunque el modelo tiene default=0
                valor_venta = vehiculo.precio_venta if vehiculo.precio_venta is not None else 0
                
                # Cálculos por fila
                total_egresos = valor_compra + gastos
                beneficio_bruto = valor_venta - total_egresos
                
                margen_beneficio = 0
                if valor_venta > 0:
                    # Margen = (Beneficio Bruto / Valor de Venta) * 100
                    margen_beneficio = (beneficio_bruto / valor_venta) * 100
                
                # Acumular totales (los últimos tres campos solicitados)
                total_vc += valor_compra
                total_g += gastos
                total_vv += valor_venta

                datos_informe.append({
                    'agno': vehiculo.agno, # año del vehículo
                    'marca': vehiculo.tipo_marca.descripcion if hasattr(vehiculo, 'tipo_marca') else None,
                    'modelo': vehiculo.modelo,
                    'valor_de_compra': valor_compra,
                    'gastos': gastos,
                    'valor_de_venta': valor_venta,
                    'total_egresos': total_egresos,
                    'beneficio_bruto': beneficio_bruto,
                    'margen_beneficio': round(margen_beneficio, 2),
                })
                
            # 4. Calcular el resumen global (incluyendo Total de Egresos Global)
            total_egresos_global = total_vc + total_g
            
            resumen = {
                'total_valor_de_compra': total_vc,
                'total_gastos': total_g,
                'total_valor_de_venta': total_vv,
            }
            
            # Adicional: Métricas consolidadas
            resumen['total_egresos_global'] = total_egresos_global
            resumen['beneficio_bruto_global'] = total_vv - total_egresos_global

            # 5. Formatear la respuesta
            return Response({
                "data": datos_informe,
                "resumen_solicitado": resumen # Contiene los 3 campos solicitados y totales calculados.
            }, status=HTTPStatus.OK)
        
        except Exception as e:
            logger.error(f"Error en InformeVehiculosPropiedad: {e}")
            return Response(
                {"error": f"Ocurrió un error inesperado al generar el informe."},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )