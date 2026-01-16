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
        
        if rut and patente:
            contrato_descartado = Presupuesto.objects.filter(
                rut_cliente=rut,
                patente_vehiculo=patente,
                estado=1  # Descartado
            ).exists()
            
            if contrato_descartado:
                return Response({
                    "error": "No se puede realizar abonos en un contrato descartado.",
                    "message": "El contrato asociado ha sido descartado y no permite operaciones."
                }, status=HTTPStatus.FORBIDDEN)
            
            # Validar que el contrato exista y esté activo
            contrato_activo = Presupuesto.objects.filter(
                rut_cliente=rut,
                patente_vehiculo=patente,
                estado=0  # Activo
            ).exists()
            
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


     def get(self, request, rut):
        """
        Obtiene UN detalle de pago específico por RUT (el primero que encuentre si hay varios).
        """
        try:
            # Aquí se usa get_object que usa .get() que espera solo uno.
            # Si quieres todos los de un RUT, deberías usar .filter()
            detalle_pago_cuota = self.get_object(rut) 
            serializer = DetallePagoCuotasSerializer(detalle_pago_cuota)
            return Response({"data": serializer.data}, status=HTTPStatus.OK)
        except NotFound as e:
            return Response({"message": str(e)}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            print(f"Error inesperado al obtener detalle de pago por RUT: {e}")
            return Response({"error": f"Ocurrió un error inesperado: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


     def get(self, request, rut, patente, numero_cuota): # Para la ruta con rut/patente/cuota
        try:
            from presupuesto.models import Presupuesto
            from django.db.models import Q
            
            # Verificar primero que el contrato no esté descartado
            contrato_activo = Presupuesto.objects.filter(
                rut_cliente=rut,
                patente_vehiculo=patente,
                estado=0  # Solo contratos no descartados
            ).exists()
            
            if not contrato_activo:
                raise NotFound(f"No se encontró un contrato activo para RUT: {rut}, Patente: {patente}.")
            
            detalles_abonos = DetallePagoCuotas.objects.order_by('-id').filter(
                rut=rut,
                patente=patente,
                numero_cuota=numero_cuota
            )
            if not detalles_abonos.exists():
                raise NotFound(f"No se encontraron abonos para RUT: {rut}, Patente: {patente} y Cuota: {numero_cuota}.")
            serializer = DetallePagoCuotasSerializer(detalles_abonos, many=True)
            return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)
        except NotFound as e:
            return JsonResponse({"message": str(e)}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            print(f"Error al obtener abonos por RUT, Patente y Cuota: {e}")
            return JsonResponse({"error": f"Ocurrió un error interno al buscar abonos: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

   
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
        
        print(f"DEBUG: Solicitud de eliminación de detalles para RUT: {rut}, Patente: {patente}")
        
        if not rut or not patente:
            return Response(
                {"message": "RUT y patente son requeridos para la eliminación."},
                status=HTTPStatus.BAD_REQUEST
            )
        
        try:
            detalles_eliminados, _ = DetallePagoCuotas.objects.filter(rut=rut, patente=patente).delete()
            
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