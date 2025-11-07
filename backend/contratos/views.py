from http import HTTPStatus
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from .models import Contratos
from .serializers import ContratosSerializer


class Clase1(APIView):
   
    def get(self, request):

        # select * from recetas order by id desc
        data = Contratos.objects.order_by('-id').all()
        datos_json = ContratosSerializer(data, many=True)
        # return Response(datos_json.data)
        return JsonResponse({"data": datos_json.data}, status=HTTPStatus.OK)
    # aqui envolvimos en un serealizable

    def post(self, request):

        serializer = ContratosSerializer(data=request.data)  # instantiate the serializer
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
            contrato = Contratos.objects.filter(rut=rut).get()
           
            serializer = ContratosSerializer(contrato)
            return Response({"data": serializer.data}, status=HTTPStatus.OK)
        
        except Exception as e:
            return Response({"error": "Ocurrió un error inesperado."},
                                status=HTTPStatus.INTERNAL_SERVER_ERROR)
       

    def get(self, request, rut, patente):
        try:
            contrato = Contratos.objects.filter(rut=rut, patente=patente).get()
           
            serializer = ContratosSerializer(contrato)
            return Response({"data": serializer.data}, status=HTTPStatus.OK)
        
        except Exception as e:
            return Response({"error": "Ocurrió un error inesperado."},
                                status=HTTPStatus.INTERNAL_SERVER_ERROR)
                                

        

    def delete(self, request, id):
        try:
            contrato = Contratos.objects.get(id=id)
            contrato.delete()
            return Response(status=HTTPStatus.NO_CONTENT)  # Código 204 No Content
        except Contratos.DoesNotExist:
            raise NotFound(f"No se encontró ningún contrato : {id}")
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado al eliminar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
        

    