# views.py
from django.db.models import Sum, OuterRef, Subquery, DecimalField, F, Q, Exists
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
from auditoria.utils import registrar_auditoria


class PagoCuotasAPIView(APIView):

    def post(self, request, format=None):
        params = request.data
        try:
            rut_cliente = params['rut_cliente']
            patente = params['patente']
            numero_contrato = params.get('numero_contrato')
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
                        numero_contrato=numero_contrato,
                        numero_cuota=i + 1,
                        fecha_vencimiento=fecha_cuota,
                        monto_cuota=monto_cuota_fija,
                        abono_capital=capital_amortizado_esta_cuota,
                        monto_prestamo=monto_prestamo,
                        interes_mensual=interes_mensual,
                        interes_mora=0,  # Valor por defecto para compatibilidad con cPanel
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
            numero_contrato = request.query_params.get('numero_contrato', None)
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
            
            # --- ESTRATEGIA OPTIMIZADA CON EXISTS ---
            # Usamos Exists para filtrar eficientemente los pares (rut, patente) 
            # que coinciden con un Presupuesto en el estado deseado.
            
            presupuestos_validos = Presupuesto.objects.filter(
                rut_cliente=OuterRef('rut_cliente'),
                patente_vehiculo=OuterRef('patente'), 
                estado=estado_filtro,
                pausa=0  # Excluir contratos pausados
            ).filter(
                Q(numero_contrato=OuterRef('numero_contrato')) | Q(numero_contrato__isnull=True)
            )

            # Filtrar cuotas base usando Exists
            # NOTA: Eliminamos la anotación de abono_total aquí porque el Serializer 
            # la recálcula con un SerializerMethodField ignorando esta anotación.
            # Esto evita una subquery costosa innecesaria en la vista.
            cuotas = Cuota.objects.annotate(
                existe_presupuesto=Exists(presupuestos_validos)
            ).filter(existe_presupuesto=True)

            # --- APLICAR FILTROS EXTRA ---
            if rut_cliente:
                cuotas = cuotas.filter(rut_cliente=rut_cliente)

            if patente:
                cuotas = cuotas.filter(patente__iexact=patente)

            if numero_contrato:
                cuotas = cuotas.filter(numero_contrato=numero_contrato)

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
            cuotas = cuotas.order_by('rut_cliente', 'patente', 'numero_contrato', 'numero_cuota')
            
            # --- OPTIMIZACIÓN DE SERIALIZACIÓN (BULK FETCH) ---
            # Convertimos a lista para "materializar" la query principal una sola vez
            cuotas_list = list(cuotas)
            
            if not cuotas_list:
                return Response({'message': 'No se encontraron cuotas', 'data': []}, status=status.HTTP_200_OK)

            # Recolectar claves para bulk fetch
            ruts = set()
            patentes = set()
            for c in cuotas_list:
                if c.rut_cliente:
                    ruts.add(c.rut_cliente)
                if c.patente:
                    patentes.add(c.patente)
            
            # Bulk Fetch Clientes
            clientes_map = {}
            if ruts:
                for cli in Clientes.objects.filter(rut__in=ruts):
                    clientes_map[cli.rut] = cli

            # Bulk Fetch Presupuestos
            presupuestos_map = {}
            if ruts and patentes:
                # Traemos un superset filtrando por listas independientes
                qs_pres = Presupuesto.objects.filter(rut_cliente__in=ruts, patente_vehiculo__in=patentes)
                for p in qs_pres:
                    presupuestos_map[(p.rut_cliente, p.patente_vehiculo)] = p
                    presupuestos_map[(p.rut_cliente, p.patente_vehiculo, p.numero_contrato)] = p
            
            # Bulk Fetch Abonos (DetallePagoCuotas)
            abonos_map = {}
            if ruts and patentes:
                qs_abonos = DetallePagoCuotas.objects.filter(
                    rut__in=ruts, 
                    patente__in=patentes
                ).values('rut', 'patente', 'numero_cuota', 'numero_contrato').annotate(total=Sum('monto_cuota'))
                
                for ab in qs_abonos:
                    if ab.get('numero_contrato') is not None:
                        abonos_map[(ab['rut'], ab['patente'], ab['numero_cuota'], str(ab.get('numero_contrato')))] = ab['total']
                    else:
                        abonos_map[(ab['rut'], ab['patente'], ab['numero_cuota'])] = ab['total']

            # Contexto para el serializador
            ctx = {
                'clientes_map': clientes_map,
                'presupuestos_map': presupuestos_map,
                'abonos_map': abonos_map
            }
            
            # Serializar
            serializer = PagoCuotasSerializer(cuotas_list, many=True, context=ctx)
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

        numero_contrato = request.query_params.get('numero_contrato') or request.data.get('numero_contrato')

        try:
            query_params_delete = {'rut_cliente': rut_cliente, 'patente': patente}
            if numero_contrato:
                query_params_delete['numero_contrato'] = numero_contrato
                
            num, _ = Cuota.objects.filter(**query_params_delete).delete()
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
            
            # --- ESTRATEGIA OPTIMIZADA CON EXISTS (igual a PagoCuotasAPIView) ---
            presupuestos_activos = Presupuesto.objects.filter(
                rut_cliente=OuterRef('rut_cliente'),
                patente_vehiculo=OuterRef('patente'),
                estado=0,   # Solo activos
                pausa=0     # Excluir contratos pausados
            ).filter(
                Q(numero_contrato=OuterRef('numero_contrato')) | Q(numero_contrato__isnull=True)
            )
            
            # Filtrar cuotas vencidas con Exists
            cuotas_base = Cuota.objects.annotate(
                existe_presupuesto_activo=Exists(presupuestos_activos)
            ).filter(
                existe_presupuesto_activo=True,
                fecha_vencimiento__lt=date.today()
            ).order_by('fecha_vencimiento')

            # Aplicar filtros de fecha si existen
            if fecha_inicio_str:
                cuotas_base = cuotas_base.filter(fecha_vencimiento__gte=date.fromisoformat(fecha_inicio_str))
            if fecha_fin_str:
                cuotas_base = cuotas_base.filter(fecha_vencimiento__lte=date.fromisoformat(fecha_fin_str))
            
            # Obtener la lista de cuotas (evaluar queryset)
            cuotas_list = list(cuotas_base)
            
            # --- BULK FETCHING (igual a PagoCuotasAPIView) ---
            ruts = set()
            patentes = set()
            for c in cuotas_list:
                if c.rut_cliente:
                    ruts.add(c.rut_cliente)
                if c.patente:
                    patentes.add(c.patente)
            
            # Bulk Fetch Clientes
            clientes_map = {}
            if ruts:
                for cli in Clientes.objects.filter(rut__in=ruts):
                    clientes_map[cli.rut] = cli

            # Bulk Fetch Presupuestos
            presupuestos_map = {}
            if ruts and patentes:
                qs_pres = Presupuesto.objects.filter(rut_cliente__in=ruts, patente_vehiculo__in=patentes)
                for p in qs_pres:
                    presupuestos_map[(p.rut_cliente, p.patente_vehiculo)] = p
            
            # Bulk Fetch Abonos (DetallePagoCuotas)
            abonos_map = {}
            if ruts and patentes:
                qs_abonos = DetallePagoCuotas.objects.filter(
                    rut__in=ruts, 
                    patente__in=patentes
                ).values('rut', 'patente', 'numero_cuota', 'numero_contrato').annotate(total=Sum('monto_cuota'))
                
                for ab in qs_abonos:
                    if ab.get('numero_contrato') is not None:
                        abonos_map[(ab['rut'], ab['patente'], ab['numero_cuota'], str(ab.get('numero_contrato')))] = ab['total']
                    else:
                        abonos_map[(ab['rut'], ab['patente'], ab['numero_cuota'])] = ab['total']

            # Contexto para el serializador
            ctx = {
                'clientes_map': clientes_map,
                'presupuestos_map': presupuestos_map,
                'abonos_map': abonos_map
            }
            
            # Serializar
            serializer = PagoCuotasSerializer(cuotas_list, many=True, context=ctx)
            data_serializada = serializer.data
            
            # Filtrar solo las que tienen días de atraso > 0
            cuotas_filtradas = [
                item for item in data_serializada if item.get('dias_atraso', 0) > 0
            ]

            return Response(cuotas_filtradas, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"CRITICAL ERROR in CuotasImpagasAPIView: {str(e)}")
            import traceback
            traceback.print_exc()
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