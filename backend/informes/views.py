from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, F, Subquery, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from datetime import datetime  # <--- Necesario para arreglar el error de fecha

# Importaciones de tus Apps
from reservas.models import Reserva
from gastos.models import Gasto

class InformeMensualAPIView(APIView):
    
    def post(self, request):
        # 1. Recibir el dato desde el JSON (Body)
        # Postman Body: { "fecha": "01-11-2025" }
        fecha_str = request.data.get('fecha')

        if not fecha_str:
            return Response(
                {"error": "Falta el campo 'fecha' en el JSON"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Procesar la fecha correctamente
        try:
            # Convertimos el texto "01-11-2025" a una fecha real
            fecha_obj = datetime.strptime(fecha_str, "%d-%m-%Y")
            
            # Extraemos año y mes de forma segura
            year = fecha_obj.year
            month = fecha_obj.month
            
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Usa DD-MM-YYYY (ej: 01-11-2025)"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------------------------------
        # PASO A: Subconsulta de Gastos
        # -------------------------------------------------------
        gastos_mes = Gasto.objects.filter(
            fecha__year=year,
            fecha__month=month
        ).values('fecha__year', 'fecha__month').annotate(
            total=Sum('valor')
        ).values('total')

        # -------------------------------------------------------
        # PASO B: Consulta Principal (Reservas)
        # -------------------------------------------------------
        data = Reserva.objects.filter(
            fecha_inicio__year=year,
            fecha_inicio__month=month
        ).select_related('tipo_arriendo').annotate(
            # Cálculo 1: Descuento Comisión
            desc_com=ExpressionWrapper(
                F('valor_arriendo') - (F('valor_arriendo') * F('tipo_arriendo__comision') / 100.0),
                output_field=DecimalField(max_digits=12, decimal_places=0)
            ),
            
            # Cálculo 2: Total Gastos (traído de la subconsulta)
            total_gastos_mes=Coalesce(Subquery(gastos_mes), 0, output_field=DecimalField(max_digits=12, decimal_places=0))
        ).values(
            'fecha_inicio',
            'fecha_fin',
            'nombre_arrendatario',
            'valor_arriendo',
            'tipo_arriendo__nombre',
            'tipo_arriendo__comision',
            'desc_com',
            'total_gastos_mes'
        )

        return Response(list(data), status=status.HTTP_200_OK)


        