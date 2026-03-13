# views.py
from datetime import datetime
from http import HTTPStatus
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

from detallePagoCuotas.models import DetallePagoCuotas


from .serializers import DetallePagoCuotasSerializer # Solo importamos este serializador

# API para listar y crear detalles de pago (abonos)
class DetallePagoCuotasAPI(APIView):
  
    def get(self, request):
        """
        Obtiene todos los registros de abonos (detalles de pago).
        EXCLUYE abonos de contratos descartados (estado=1).
        """
        from presupuesto.models import Presupuesto
        from django.db.models import Q
        
        # Excluir abonos de contratos descartados
        data = DetallePagoCuotas.objects.filter(
            Q(rut__in=Presupuesto.objects.filter(estado=0).values_list('rut_cliente', flat=True)) &
            Q(patente__in=Presupuesto.objects.filter(estado=0).values_list('patente_vehiculo', flat=True))
        ).order_by('-id').all()
        
        serializer = DetallePagoCuotasSerializer(data, many=True)
        return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)

    def post(self, request):
        """
        Crea un nuevo registro de abono en la tabla `detalle_pago`.
        NO realiza ninguna actualización en la tabla `pagocuotas` principal.
        VALIDA que el contrato no esté descartado.
        """
        from presupuesto.models import Presupuesto
        
        data = request.data
        
        # Validar que el contrato no esté descartado
        rut = data.get('rut')
        patente = data.get('patente')
        numero_contrato = data.get('numero_contrato')
        
        if rut and patente:
            query_descartado = {
                'rut_cliente': rut,
                'patente_vehiculo': patente,
                'estado': 1  # Descartado
            }
            if numero_contrato:
                query_descartado['numero_contrato'] = numero_contrato
                
            contrato_descartado = Presupuesto.objects.filter(**query_descartado).exists()
            
            if contrato_descartado:
                return Response({
                    "error": "No se puede realizar abonos en un contrato descartado.",
                    "message": "El contrato asociado ha sido descartado y no permite operaciones."
                }, status=HTTPStatus.FORBIDDEN)
            
            # Validar que el contrato exista y esté activo
            query_activo = {
                'rut_cliente': rut,
                'patente_vehiculo': patente,
                'estado': 0  # Activo
            }
            if numero_contrato:
                query_activo['numero_contrato'] = numero_contrato
                
            contrato_activo = Presupuesto.objects.filter(**query_activo).exists()
            
            if not contrato_activo:
                return Response({
                    "error": "No se encontró un contrato activo.",
                    "message": "El contrato no existe o ha sido descartado."
                }, status=HTTPStatus.NOT_FOUND)
        
        serializer = DetallePagoCuotasSerializer(data=data)
        
        try:
            serializer.is_valid(raise_exception=True) # Valida los datos del abono
            serializer.save()  # Guarda el nuevo abono en la tabla `detalle_pago`
            return Response({"data": serializer.data, "message": "Detalle de pago creado exitosamente"}, status=HTTPStatus.CREATED)
        except ValidationError as e:
            return Response({"errors": e.detail, "message": "Datos de abono inválidos"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            print(f"Error inesperado al crear detalle de pago: {e}")
            return Response({"error": f"Ocurrió un error inesperado al crear: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                

class DetallePagoCuotasIndividualAPI(APIView):


     def get(self, request, id=None, rut=None, patente=None, numero_cuota=None):
        """
        Obtiene detalles de pago. Maneja tanto búsqueda por ID como por RUT, Patente y Nº Cuota.
        """
        if id is not None:
            try:
                detalle_pago_cuota = DetallePagoCuotas.objects.get(id=id)
                serializer = DetallePagoCuotasSerializer(detalle_pago_cuota)
                return Response({"data": serializer.data}, status=HTTPStatus.OK)
            except DetallePagoCuotas.DoesNotExist:
                return Response({"message": f"No se encontró ningún detalle de pago con el ID: {id}"}, status=HTTPStatus.NOT_FOUND)
            except Exception as e:
                print(f"Error inesperado al obtener detalle de pago por ID: {e}")
                return Response({"error": f"Ocurrió un error inesperado: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                
        elif rut is not None and patente is not None and numero_cuota is not None:
            try:
                from presupuesto.models import Presupuesto
                from django.db.models import Q
                numero_contrato = request.query_params.get('numero_contrato')
                
                # Verificar primero que el contrato no esté descartado
                query = Q(rut_cliente=rut, patente_vehiculo=patente, estado=0)
                if numero_contrato:
                    query &= Q(numero_contrato=numero_contrato)
                    
                contrato_activo = Presupuesto.objects.filter(query).exists()
                
                if not contrato_activo:
                    raise NotFound(f"No se encontró un contrato activo para RUT: {rut}, Patente: {patente}.")
                
                q_abonos = Q(rut=rut, patente=patente, numero_cuota=numero_cuota)
                if numero_contrato:
                    q_abonos &= Q(numero_contrato=numero_contrato)
                    
                detalles_abonos = DetallePagoCuotas.objects.order_by('-id').filter(q_abonos)
                if not detalles_abonos.exists():
                    raise NotFound(f"No se encontraron abonos para RUT: {rut}, Patente: {patente} y Cuota: {numero_cuota}.")
                serializer = DetallePagoCuotasSerializer(detalles_abonos, many=True)
                return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)
            except NotFound as e:
                return JsonResponse({"message": str(e)}, status=HTTPStatus.NOT_FOUND)
            except Exception as e:
                print(f"Error al obtener abonos por RUT, Patente y Cuota: {e}")
                return JsonResponse({"error": f"Ocurrió un error interno al buscar abonos: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
        else:
             return Response({"message": "Ruta no soportada."}, status=HTTPStatus.BAD_REQUEST)

   
     def put(self, request, rut):
        """
        Modifica un detalle de pago específico por RUT.
        """
        data = request.data
        try:
            # PROBLEMA: Si hay múltiples DetallePagoCuotas con el mismo RUT, .get() lanzará un error.
            # Esto solo funciona si `rut` es un campo único en `DetallePagoCuotas` o si esperas actualizar SOLO el primero.
            detalle_pago_cuota = DetallePagoCuotas.objects.get(rut=rut) 
            serializer = DetallePagoCuotasSerializer(detalle_pago_cuota, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data, "message": "Detalle de pago modificado exitosamente"}, status=HTTPStatus.OK)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except DetallePagoCuotas.DoesNotExist:
            raise NotFound(f"No se encontró ningún detalle de pago con el RUT: {rut}")
        except Exception as e:
            print(f"Error inesperado al modificar detalle de pago: {e}")
            return Response({"error": f"Ocurrió un error inesperado al modificar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                

     def delete(self, request, id):
        """
        Elimina un detalle de pago específico por RUT.
        """
        try:
            # PROBLEMA: Similar al PUT, DetallePagoCuotas.objects.get(rut=rut) fallará si hay múltiples.
            detalle_pago_cuota = DetallePagoCuotas.objects.get(id=id)
            detalle_pago_cuota.delete()
            return Response(status=HTTPStatus.NO_CONTENT) # Código 204 No Content
        except DetallePagoCuotas.DoesNotExist:
            raise NotFound(f"No se encontró ningún detalle de pago con el RUT: {id}")
        except Exception as e:
            print(f"Error inesperado al eliminar detalle de pago: {e}")
            return Response({"error": f"Ocurrió un error inesperado al eliminar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


class EliminarDetallesPorRutPatenteAPI(APIView):
    """
    Elimina todos los detalles de pago (abonos) por RUT y PATENTE.
    """
    def delete(self, request):
        """
        Elimina todos los registros de detalle_pago para un RUT y PATENTE específicos.
        """
        # Aceptar parámetros tanto de query_params como de request.data
        rut = request.query_params.get('rut') or request.data.get('rut')
        patente = request.query_params.get('patente') or request.data.get('patente')
        numero_contrato = request.query_params.get('numero_contrato') or request.data.get('numero_contrato')
        
        print(f"DEBUG: Solicitud de eliminación de detalles para RUT: {rut}, Patente: {patente}")
        
        if not rut or not patente:
            return Response(
                {"message": "RUT y patente son requeridos para la eliminación."},
                status=HTTPStatus.BAD_REQUEST
            )
        
        try:
            query_params_delete = {'rut': rut, 'patente': patente}
            if numero_contrato:
                query_params_delete['numero_contrato'] = numero_contrato

            detalles_eliminados, _ = DetallePagoCuotas.objects.filter(**query_params_delete).delete()
            
            if detalles_eliminados > 0:
                print(f"DEBUG: {detalles_eliminados} detalle(s) de pago eliminado(s) para RUT: {rut}, Patente: {patente}")
                return Response(
                    {"message": f"{detalles_eliminados} detalle(s) de pago eliminado(s) exitosamente."},
                    status=HTTPStatus.OK
                )
            else:
                print(f"DEBUG: No se encontraron detalles de pago para RUT: {rut}, Patente: {patente}")
                return Response(
                    {"message": "No se encontraron detalles de pago para los criterios especificados."},
                    status=HTTPStatus.NOT_FOUND
                )
        except Exception as e:
            print(f"ERROR: Excepción al eliminar detalles de pago: {e}")
            return Response(
                {"message": f"Error interno del servidor: {str(e)}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )