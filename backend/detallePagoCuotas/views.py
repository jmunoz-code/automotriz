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
        """
        # Aquí puedes añadir filtros si necesitas, por ejemplo, si recibes 'rut' o 'patente'
        # Esto fue una adición previa, pero ahora el código de ejemplo que me diste lo omite.
        # Asumo que solo devuelve todos sin filtros si no hay 'TodosRegistrosPorRutPatenteAPIView'.
        data = DetallePagoCuotas.objects.order_by('-id').all()
        serializer = DetallePagoCuotasSerializer(data, many=True)
        return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)

    def post(self, request):
        """
        Crea un nuevo registro de abono en la tabla `detalle_pago`.
        NO realiza ninguna actualización en la tabla `pagocuotas` principal.
        """
        data = request.data

        
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