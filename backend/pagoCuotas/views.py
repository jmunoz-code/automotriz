# views.py
from django.db.models import Sum, OuterRef, Subquery, DecimalField, F, Q
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP

# Importa tus serializadores y modelos
from detallePagoCuotas.serializers import DetallePagoCuotasSerializer
from pagoCuotas.serializers import PagoCuotasSerializer
from .models import PagoCuotas as Cuota
from detallePagoCuotas.models import DetallePagoCuotas
from clientes.models import Clientes
from presupuesto.models import Presupuesto


class PagoCuotasAPIView(APIView):

    def post(self, request, format=None):
        params = request.data
        try:
            rut_cliente = params['rut_cliente']
            patente = params['patente']
            cantidad_cuotas = int(params['numero_cuota'])
            
            monto_cuota_fija = Decimal(str(params['monto_cuota'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            monto_prestamo = Decimal(str(params['monto_prestamo'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            interes_mensual = Decimal(str(params['interes_mensual']))

            fecha_vencimiento_inicial = date.fromisoformat(params['fecha_vencimiento'])
            
            interes_mensual_tasa = (interes_mensual / 100).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)

            saldo_pendiente = monto_prestamo
            generated_cuotas = []
            
            with transaction.atomic():
                Cuota.objects.filter(rut_cliente=rut_cliente, patente=patente).delete()

                for i in range(cantidad_cuotas):
                    fecha_cuota = (fecha_vencimiento_inicial + relativedelta(months=i))
                    
                    interes_esta_cuota = (saldo_pendiente * interes_mensual_tasa).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    capital_amortizado_esta_cuota = (monto_cuota_fija - interes_esta_cuota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    
                    saldo_pendiente -= capital_amortizado_esta_cuota
                    
                    if i == cantidad_cuotas - 1:
                        capital_amortizado_esta_cuota += saldo_pendiente.quantize(Decimal('0.01'))
                        saldo_pendiente = Decimal('0.00') # Forzamos el saldo a cero
                        
                    Cuota.objects.create(
                        rut_cliente=rut_cliente,
                        patente=patente,
                        numero_cuota=i + 1,
                        fecha_vencimiento=fecha_cuota,
                        monto_cuota=monto_cuota_fija,
                        abono_capital=capital_amortizado_esta_cuota,
                        monto_prestamo=monto_prestamo,
                        interes_mensual=interes_mensual,
                    )
            
            generated_cuotas = Cuota.objects.filter(rut_cliente=rut_cliente, patente=patente).order_by('numero_cuota')
            response_serializer = PagoCuotasSerializer(generated_cuotas, many=True)
            return Response({'message': f'Cuotas generadas exitosamente ({cantidad_cuotas}) y guardadas en la base de datos.', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)

        except KeyError as ke:
            required_fields = ['rut_cliente', 'patente', 'numero_cuota', 'monto_cuota', 'monto_prestamo', 'interes_mensual', 'fecha_vencimiento']
            return Response({
                "error": f"Faltan datos en la solicitud: {str(ke)}.",
                "detalle": f"Asegúrese de enviar todos los campos requeridos en el JSON: {', '.join(required_fields)}."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except (ValueError, TypeError) as ve:
            return Response({
                "error": "Error de formato de datos.", 
                "detalle": f"Asegúrese de que los campos numéricos y de fecha (YYYY-MM-DD) estén correctos. Detalle: {str(ve)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": f"Error interno del servidor al procesar la solicitud: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, format=None):
        """ Maneja la consulta y filtrado de cuotas con cálculo de abonos. """
        try:
            print("DEBUG: Entrando en PagoCuotasAPIView.get")

            rut_cliente = request.query_params.get('rut_cliente', None)
            patente = request.query_params.get('patente', None)
            nombres_filtro = request.query_params.get('nombres', None)
            historico = request.query_params.get('historico', 'false').lower() == 'true'

            # Subconsulta para abonos
            subquery_abonos = DetallePagoCuotas.objects.filter(
                rut=OuterRef('rut_cliente'),
                patente=OuterRef('patente'),
                numero_cuota=OuterRef('numero_cuota')
            ).values('rut', 'patente', 'numero_cuota').annotate(
                total_abonos_sum=Coalesce(Sum('monto_cuota'), 0, output_field=DecimalField())
            ).values('total_abonos_sum')[:1]

            # Definir estado a filtrar
            estado_filtro = 1 if historico else 0
            
            # --- ESTRATEGIA SEGURA (BULLETPROOF) v2 ---
            # 1. Obtener lista de tuplas (rut, patente) válidas
            # Convertimos a lista para evitar cualquier lazy evaluation rara de Django/DB
            qs_contratos = Presupuesto.objects.filter(estado=estado_filtro).values_list('rut_cliente', 'patente_vehiculo')
            lista_contratos = list(qs_contratos)
            
            # 2. Si no hay contratos, retornamos vacio inmediatamente
            if not lista_contratos:
                return Response({'message': 'No hay contratos en ese estado', 'data': []}, status=status.HTTP_200_OK)

            # 3. Construir filtro Q grande
            filtro_pares = Q()
            for r, p in lista_contratos:
                filtro_pares |= Q(rut_cliente=r, patente=p)
            
            # 4. Filtrar cuotas base usando el filtro construido
            cuotas = Cuota.objects.annotate(
                abono_total=Subquery(subquery_abonos)
            ).filter(filtro_pares)

            # --- APLICAR FILTROS EXTRA ---
            if rut_cliente:
                cuotas = cuotas.filter(rut_cliente=rut_cliente)

            if patente:
                cuotas = cuotas.filter(patente=patente)

            if nombres_filtro:
                ruts_por_nombre = list(Clientes.objects.filter(
                    Q(nombres__icontains=nombres_filtro) | 
                    Q(apellidos__icontains=nombres_filtro)
                ).values_list('rut', flat=True))
                
                if ruts_por_nombre:
                    cuotas = cuotas.filter(rut_cliente__in=ruts_por_nombre)
                else:
                    cuotas = Cuota.objects.none()

            # Ordenar
            cuotas = cuotas.order_by('rut_cliente', 'patente', 'numero_cuota')
            
            # Serializar
            serializer = PagoCuotasSerializer(cuotas, many=True)
            return Response({'message': 'Cuotas obtenidas exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            # Captura de error FINAL para debugging
            print(f"CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                "error": "Error critico en servidor", 
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk, format=None):
        try:
            cuota = Cuota.objects.get(pk=pk)
        except Cuota.DoesNotExist:
            return Response({"message": "Cuota no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PagoCuotasSerializer(cuota, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Cuota actualizada exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodosRegistrosPorRutPatenteAPIView(APIView):
    def get(self, request, format=None):
        rut_cliente = request.query_params.get('rut_cliente', None)
        patente = request.query_params.get('patente', None)

        if not rut_cliente or not patente:
            return Response(
                {"message": "RUT y Patente requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        registros = DetallePagoCuotas.objects.filter(
            rut_cliente=rut_cliente,
            patente=patente
        ).order_by('numero_cuota')

        serializer = DetallePagoCuotasSerializer(registros, many=True)
        return Response({'message': 'Registros obtenidos', 'data': serializer.data}, status=status.HTTP_200_OK)


class EliminarCuotasPorRutPatenteAPIView(APIView):
    def delete(self, request, *args, **kwargs):
        rut_cliente = request.query_params.get('rut') or request.data.get('rut_cliente')
        patente = request.query_params.get('patente') or request.data.get('patente')

        if not rut_cliente or not patente:
            return Response({"message": "RUT y Patente requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            num, _ = Cuota.objects.filter(rut_cliente=rut_cliente, patente=patente).delete()
            if num > 0:
                return Response({"message": f"{num} cuotas eliminadas."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No se encontraron cuotas."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CuotasImpagasAPIView(APIView):
    def get(self, request, format=None):
        try:
            fecha_inicio_str = request.query_params.get('fecha_inicio')
            fecha_fin_str = request.query_params.get('fecha_fin')
            
            # --- ESTRATEGIA SEGURA v2 ---
            qs_activos = Presupuesto.objects.filter(estado=0).values_list('rut_cliente', 'patente_vehiculo')
            lista_activos = list(qs_activos)
            
            filtro_pares = Q()
            for r, p in lista_activos:
                filtro_pares |= Q(rut_cliente=r, patente=p)
            
            if not lista_activos:
                cuotas_base = Cuota.objects.none()
            else:
                cuotas_base = Cuota.objects.filter(
                    Q(fecha_vencimiento__lt=date.today()) | Q(fecha_vencimiento__isnull=True)
                ).filter(filtro_pares).order_by('fecha_vencimiento')

            if fecha_inicio_str:
                cuotas_base = cuotas_base.filter(fecha_vencimiento__gte=date.fromisoformat(fecha_inicio_str))
            if fecha_fin_str:
                cuotas_base = cuotas_base.filter(fecha_vencimiento__lte=date.fromisoformat(fecha_fin_str))
            
            subquery_abonos = DetallePagoCuotas.objects.filter(
                rut=OuterRef('rut_cliente'),
                patente=OuterRef('patente'),
                numero_cuota=OuterRef('numero_cuota')
            ).values('rut', 'patente', 'numero_cuota').annotate(
                total_abonos_sum=Coalesce(Sum('monto_cuota'), 0, output_field=DecimalField())
            ).values('total_abonos_sum')[:1]

            cuotas_queryset = cuotas_base.annotate(
                abono_total_anotado=Subquery(subquery_abonos) 
            )

            serializer = PagoCuotasSerializer(cuotas_queryset, many=True)
            data_serializada = serializer.data
            
            cuotas_filtradas = [
                item for item in data_serializada if item.get('dias_atraso', 0) > 0
            ]

            return Response(cuotas_filtradas, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"Error interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EliminarCuotasPoridAPIView(APIView):
    def delete(self, request, id):
        try:
            num, _ = Cuota.objects.filter(id=id).delete()
            if num > 0:
                return Response({"message": f"{num} cuotas eliminadas."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)