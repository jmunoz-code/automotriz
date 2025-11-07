from rest_framework import status
from http import HTTPStatus
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from .models import Costos
from .serializers import CostosSerializer
from drf_yasg import openapi
from django.db.models import Sum 


class Clase1(APIView):
      
    def get(self, request):
        """
        Obtiene una lista de todos los costos existentes, ordenados por ID de forma descendente.
        """
        data = Costos.objects.order_by('-patente').all()
        datos_json = CostosSerializer(data, many=True)
        return JsonResponse({"data":datos_json.data},status= HTTPStatus.OK)
   
    def post(self, request):
        """
        Crea un nuevo registro de costo.
        El campo 'tipo_costo' se convertirá a mayúsculas automáticamente.
        """
        modified_data = request.data.copy()

        if 'patente' in modified_data and modified_data['patente']:
            modified_data['patente'] = modified_data['patente'].upper()

        # Convertir a mayúsculas el campo 'tipo_costo' si existe
        if 'tipo_costo' in modified_data and modified_data['tipo_costo']:
            modified_data['tipo_costo'] = modified_data['tipo_costo'].upper()

        serializer = CostosSerializer(data=modified_data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
                            status=HTTPStatus.CREATED)
        except ValidationError:
            return Response({"estado": "error", "mensaje": serializer.errors},
                            status=HTTPStatus.BAD_REQUEST)

class Clase2(APIView):
    
    def put(self, request, id):
        try:
            costo_instance = Costos.objects.get(id=id)
        except Costos.DoesNotExist:
            raise NotFound(detail=f"Costo con ID {id} no encontrado")

        modified_data = request.data.copy()

        # Convertir a mayúsculas el campo 'tipo_costo' si existe en los datos de actualización
        if 'tipo_costo' in modified_data and modified_data['tipo_costo']:
            modified_data['tipo_costo'] = modified_data['tipo_costo'].upper()

        serializer = CostosSerializer(costo_instance, data=modified_data, partial=True) # partial=True permite actualización parcial
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"estado": "ok", "mensaje": "Se actualiza el registro exitosamente"},
                            status=HTTPStatus.OK)
        except ValidationError:
            return Response({"estado": "error", "mensaje": serializer.errors},
                            status=HTTPStatus.BAD_REQUEST)

   
    def delete(self, request, id):
     
        try:
            cliente = Costos.objects.get(id=id)
            cliente.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        except Costos.DoesNotExist:
            raise NotFound(detail=f"No se encontró ningún costo con el ID: {id}")
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado al eliminar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        

class Clase3(APIView):
    
    def get(self, request, patente):
        try:
            total_valor_agg = Costos.objects.filter(patente=patente).aggregate(total_valor=Sum('valor'))
            
            # Obtén el valor sumado. Si es None (no hay registros), usa 0.
            suma_final = total_valor_agg.get('total_valor')
            if suma_final is None:
                suma_final = 0

            # Devuelve directamente el valor numérico
            return Response(suma_final, status=status.HTTP_200_OK)

        except Exception as e:
            # Manejo general de cualquier otra excepción
            # Es buena práctica devolver un error JSON si algo sale mal
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Clase4(APIView):
    
    def get(self, request, patente):

        data = Costos.objects.filter(patente=patente) 
        datos_json = CostosSerializer(data, many=True)
        return JsonResponse({"data":datos_json.data},status= HTTPStatus.OK)