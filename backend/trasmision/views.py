from django.shortcuts import render
from http import HTTPStatus
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from django.http.response import JsonResponse
from django.http import Http404

from trasmision.serializers import TrasmisionSerializer
from .models import Trasmision


class Clase1(APIView):
    def get(self, request):
        data = Trasmision.objects.order_by('-id').all()
        datos_json = TrasmisionSerializer(data, many=True)
        return JsonResponse({"data":datos_json.data},status= HTTPStatus.OK)

    def post(self, request):
       
          # Create a mutable copy of request.data to modify
        modified_data = request.data.copy()

        # Apply uppercasing to specific string fields if they exist
        if 'descripcion' in modified_data and modified_data['descripcion']:
            modified_data['descripcion'] = modified_data['descripcion'].upper()
        
        serializer = TrasmisionSerializer(data=modified_data)  #instantiate the serializer
        try:
            serializer.is_valid(raise_exception=True) #perform data validation, raise exception if not valid
            serializer.save()  #creates new client instance
            return Response({"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
                            status=HTTPStatus.CREATED)
        except ValidationError: #catch serializer validation errors
             return Response({"estado": "error", "mensaje": serializer.errors},
                            status=HTTPStatus.BAD_REQUEST)
      
class Clase2(APIView):
 
    def get(self, request, id):
        try:
            tipo = Trasmision.objects.filter(id=id).get()
           
            serializer = TrasmisionSerializer(tipo)
            return Response({"data": serializer.data}, status=HTTPStatus.OK)
        
        except Exception as e:
            return Response({"error": "Ocurrió un error inesperado."},
                                status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    def put(self, request, id):

          # Create a mutable copy of request.data to modify
        modified_data = request.data.copy()

        # Apply uppercasing to specific string fields if they exist
        if 'descripcion' in modified_data and modified_data['descripcion']:
            modified_data['descripcion'] = modified_data['descripcion'].upper()
        
        try:
            tipo = Trasmision.objects.filter(id=id).get()
            serializer =  TrasmisionSerializer(tipo, modified_data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data, "message": "ID modificado exitosamente"}, status=HTTPStatus.OK)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except NotFound as e:
            return Response({"error": str(e)}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado al modificar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    

    def delete(self, request, id):
        try:
            tipo = Trasmision.objects.get(id=id)
            tipo.delete()
            return Response(status=HTTPStatus.NO_CONTENT)  # Código 204 No Content
        except tipo.DoesNotExist:
            raise NotFound(f"No se encontró forma de tipo Trasmisión: {id}")
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado al eliminar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    