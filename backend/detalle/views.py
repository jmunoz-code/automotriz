from django.shortcuts import render

# Create your views here.
from datetime import datetime
from http import HTTPStatus
from rest_framework.views import APIView
from .models import detalle
from django.http.response import JsonResponse
from rest_framework.response import Response
from .serializers import *
from django.http import Http404


class Clase1(APIView):
    def get(self, request):
        data = detalle.objects.order_by('-id').all()
        serializer = detalleSerializer(data, many=True)
        return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)

    def post(self, request):
        if not request.data.get("rut"):
            return Response(
                {"estado": "error", "mensaje": "El campo rut es obligatorio"},
                status=HTTPStatus.BAD_REQUEST,
            )

        if not request.data.get("id_compra"):
            return Response(
                {"estado": "error", "mensaje": "El campo id_compra es obligatorio"},
                status=HTTPStatus.BAD_REQUEST,
            )

        if not request.data.get("numero_cuota"):
            return Response(
                {"estado": "error", "mensaje": "El campo numero_cuota es obligatorio"},
                status=HTTPStatus.BAD_REQUEST,
            )

        if not request.data.get("valor_cuota"):
            return Response(
                {"estado": "error", "mensaje": "El valor_cuota es obligatorio"},
                status=HTTPStatus.BAD_REQUEST,
            )

        if not request.data.get("fecha_vencimiento"):
            return Response(
                {"estado": "error", "mensaje": "La fecha de vencimiento es obligatoria"},
                status=HTTPStatus.BAD_REQUEST,
            )

        if not request.data.get("fecha_pago"):
            return Response(
                {"estado": "error", "mensaje": "La fecha de pago es obligatoria"},
                status=HTTPStatus.BAD_REQUEST,
            )

        try:
            detalle.objects.create(
                id_compra=request.data["id_compra"],
                numero_cuota=request.data["numero_cuota"],
                valor_cuota=request.data["valor_cuota"],
                estado=request.data.get("estado"),  # Considera usar .get() con un valor por defecto
                fecha_vencimiento=request.data["fecha_vencimiento"],
                fecha_pago=request.data.get("fecha_pago"),  # Considera usar .get() con un valor por defecto
            )

            return Response(
                {"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
                status=HTTPStatus.CREATED,
            )
        except Exception as e:
            return Response(
                {"estado": "error", "mensaje": f"Error al crear el registro: {str(e)}"},
                status=HTTPStatus.BAD_REQUEST,
            )  # Include the error message for debugging


class Clase2(APIView):
    def get(self, request, id):
        try:
            data = detalle.objects.get(id=id)
            return JsonResponse(
                {
                    "data": {
                        "id": data.id,
                        "id_compra": data.id_compra,
                        "numero_cuota": data.numero_cuota,
                        "valor_cuota": data.valor_cuota,
                        "estado": data.estado,
                        "fecha_vencimiento": data.fecha_vencimiento,
                        "fecha_pago": data.fecha_pago,
                    }
                },
                status=HTTPStatus.OK,
            )
        except detalle.DoesNotExist:
            raise Http404

    def put(self, request, id):
        try:
            vehiculo = detalle.objects.get(id=id)
        except detalle.DoesNotExist:
            raise Http404

        serializer = detalleSerializer(detalle, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    def delete(self, request, id):
        try:
            vehiculo = detalle.objects.get(id=id)
        except detalle.DoesNotExist:
            raise Http404

        vehiculo.delete()
        return Response(status=HTTPStatus.NO_CONTENT)