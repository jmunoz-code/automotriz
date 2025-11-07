from django.shortcuts import render
from http import HTTPStatus
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.response import JsonResponse
from django.http import Http404

from estados.serializers import EstadosSerializer
from .models import Estados


class Clase1(APIView):
    def get(self, request):
        """
        Obtiene todos los tipos de vehículos ordenados por ID descendente.
        """
        data = Estados.objects.order_by('-id').all()
        datos_json = EstadosSerializer(data, many=True)
        return JsonResponse({"data": datos_json.data}, status=HTTPStatus.OK)

    def post(self, request):
        """
        Crea un nuevo tipo de estado.
        """
        if not request.data.get("tipo_estado"):
            return JsonResponse({"estado": "error", "mensaje": "El campo tipo estado es obligatorio"},
                            status=HTTPStatus.BAD_REQUEST)
        if not request.data.get("descripcion"):
            return JsonResponse({"estado": "error", "mensaje": "El campo descripcion es obligatorio"},
                            status=HTTPStatus.BAD_REQUEST)
        try:
            serializer = EstadosSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=HTTPStatus.CREATED)
            return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            raise Http404


class Clase2(APIView):
    def get(self, request, id):
        try:
            data = Estados.objects.filter(id=id).get()
            return JsonResponse({"data": {"id": data.id,
                                            "tipo_estado": data.tipo_estado,  # Corrección aquí
                                            "descripcion": data.descripcion}},
                            status=HTTPStatus.OK)
        except Estados.DoesNotExist:
            raise Http404

    # modificación de registro
    def put(self, request, id):
        if request.data.get("tipo_estado") is None or not request.data['tipo_estado']:
            return Response({"estado": "error", "mensaje": "El campo tipo_combustible es obligatorio"},
                            status=HTTPStatus.BAD_REQUEST)

        if request.data.get("descripcion") is None or not request.data['descripcion']:
            return Response({"estado": "error", "mensaje": "El campo descripcion es obligatorio"},
                            status=HTTPStatus.BAD_REQUEST)

        try:
            data = Estados.objects.filter(pk=id).get()
            Estados.objects.filter(pk=id).update(tipo_estados=request.data.get("tipo_estados"),  # Corrección aquí
                                                    descripcion=request.data.get("descripcion"))
            return JsonResponse({"estado": "ok", "mensaje": "Se Modifico el registro exitosamente"},
                            status=HTTPStatus.OK)
        except Estados.DoesNotExist:
            raise Http404

    def delete(self, request, id):
        try:
            data = Estados.objects.filter(pk=id).get()
            Estados.objects.filter(pk=id).delete()
            return JsonResponse({"estado": "ok", "mensaje": "Se Elimina el registro exitosamente"},
                            status=HTTPStatus.OK)
        except Estados.DoesNotExist:
            raise Http404
