from django.forms import ValidationError
from django.shortcuts import render
from http import HTTPStatus
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, NotFound
from .models import TipoPago
from django.http.response import JsonResponse
from rest_framework.response import Response
from .serializers import *
from django.http import Http404

class Clase1(APIView):

    def get(self, request):
        data = TipoPago.objects.order_by('-id').all()
        datos_json = TipoPagoSerializer(data, many=True)
        return JsonResponse({"data": datos_json.data}, status=HTTPStatus.OK)

    def post(self, request):
        modified_data = request.data.copy()

        # Aplica mayúsculas a campos de cadena específicos si existen
        if 'descripcion' in modified_data and modified_data['descripcion']:
            modified_data['descripcion'] = modified_data['descripcion'].upper()
        
        serializer = TipoPagoSerializer(data=modified_data)  # Instancia el serializador

        try:
            serializer.is_valid(raise_exception=True)  # Realiza la validación de datos, lanza una excepción si no es válido
            serializer.save()  # Crea una nueva instancia del cliente
            return Response(
                {"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
                status=HTTPStatus.CREATED
            )
        except ValidationError:  # Captura los errores de validación del serializador
            return Response(
                {"estado": "error", "mensaje": serializer.errors},
                status=HTTPStatus.BAD_REQUEST
            )


class Clase2(APIView):
 
    def get(self, request, id):
        try:
            idpago = TipoPago.objects.filter(id=id).get()
            
            serializer = TipoPagoSerializer(idpago)
            return Response({"data": serializer.data}, status=HTTPStatus.OK)
        
        except TipoPago.DoesNotExist: # Captura si no se encuentra el objeto
            raise NotFound(f"No se encontró tipo de pago con ID: {id}")
        except Exception as e:
            return Response(
                {"error": "Ocurrió un error inesperado al obtener el tipo de pago."},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, id):
        try:
            idpago = TipoPago.objects.filter(id=id).get()
            serializer = TipoPagoSerializer(idpago, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "ID modificado exitosamente"},
                    status=HTTPStatus.OK
                )
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except TipoPago.DoesNotExist: # Captura si no se encuentra el objeto
            raise NotFound(f"No se encontró tipo de pago con ID: {id}")
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error inesperado al modificar: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, id):
        try:
            idpago = TipoPago.objects.get(id=id)
            idpago.delete()
            return Response(status=HTTPStatus.NO_CONTENT)  # Código 204 No Content
        except TipoPago.DoesNotExist:
            raise NotFound(f"No se encontró forma de tipo pago: {id}")
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error inesperado al eliminar: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )