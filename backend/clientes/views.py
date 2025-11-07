from datetime import datetime
from http import HTTPStatus
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from yaml import serialize
from .models import Clientes
from .serializers import ClientesSerializer


class Clase1(APIView):
  
    def get(self, request):

        # select * from recetas order by id desc
        data = Clientes.objects.order_by('-id').all()
        datos_json = ClientesSerializer(data, many=True)
        # return Response(datos_json.data)
        return JsonResponse({"data": datos_json.data}, status=HTTPStatus.OK)
    # aqui envolvimos en un serealizable


    def post(self, request):

        modified_data = request.data.copy()
         
        if 'nombres' in modified_data and modified_data['nombres']:
            modified_data['nombres'] = modified_data['nombres'].upper()

         
        if 'apellidos' in modified_data and modified_data['apellidos']:
            modified_data['apellidos'] = modified_data['apellidos'].upper()


        if 'direccion' in modified_data and modified_data['direccion']:
            modified_data['direccion'] = modified_data['direccion'].upper()

         
        if 'ciudad' in modified_data and modified_data['ciudad']:
            modified_data['ciudad'] = modified_data['ciudad'].upper()

              
        serializer = ClientesSerializer(data=modified_data) 

        
        try:
            serializer.is_valid(raise_exception=True) # perform data validation, raise exception if not valid
            serializer.save()  # creates new client instance
            return Response({"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
                            status=HTTPStatus.CREATED)
        except ValidationError: # catch serializer validation errors
            return Response({"estado": "error", "mensaje": serializer.errors},
                            status=HTTPStatus.BAD_REQUEST)


class Clase2(APIView):
        
    def get(self, request, rut):
        try:
            cliente = Clientes.objects.filter(rut=rut).get()
           
            serializer = ClientesSerializer(cliente)
            return Response({"data": serializer.data}, status=HTTPStatus.OK)
        
        except Exception as e:
            return Response({"error": "Ocurrió un error inesperado."},
                                status=HTTPStatus.INTERNAL_SERVER_ERROR)

        
        
    def put(self, request, rut):
      
        modified_data = request.data.copy()
         
        if 'nombres' in modified_data and modified_data['nombres']:
            modified_data['nombres'] = modified_data['nombres'].upper()

         
        if 'apellidos' in modified_data and modified_data['apellidos']:
            modified_data['apellidos'] = modified_data['apellidos'].upper()


        if 'direccion' in modified_data and modified_data['direccion']:
            modified_data['direccion'] = modified_data['direccion'].upper()

         
        if 'ciudad' in modified_data and modified_data['ciudad']:
            modified_data['ciudad'] = modified_data['ciudad'].upper()

        if 'correo' in modified_data and modified_data['correo']:
            modified_data['correo'] = modified_data['correo'].upper()
        

        try:
            cliente = Clientes.objects.filter(rut=rut).get()
            serializer = ClientesSerializer(cliente, data=modified_data) 
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data, "message": "Cliente modificado exitosamente"}, status=HTTPStatus.OK)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except NotFound as e:
            return Response({"error": str(e)}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado al modificar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                

    def delete(self, request, rut):
        try:
            cliente = Clientes.objects.get(rut=rut)
            cliente.delete()
            return Response(status=HTTPStatus.NO_CONTENT)  # Código 204 No Content
        except Clientes.DoesNotExist:
            raise NotFound(f"No se encontró ningún cliente con el RUT: {rut}")
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado al eliminar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
        

    