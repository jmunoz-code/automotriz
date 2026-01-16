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
        print("DEBUG: Entrando en PagoCuotasAPIView.get")

        rut_cliente = request.query_params.get('rut_cliente', None)
        patente = request.query_params.get('patente', None)
        nombres_filtro = request.query_params.get('nombres', None) # Término de búsqueda de nombres
        historico = request.query_params.get('historico', 'false').lower() == 'true'  # Parámetro para histórico

        print(f"DEBUG: Parámetro historico={historico}")

        # Subconsulta para calcular la suma de abonos (total_abonos_sum) para cada Cuota
        subquery_abonos = DetallePagoCuotas.objects.filter(
            rut=OuterRef('rut_cliente'),
            patente=OuterRef('patente'),
            numero_cuota=OuterRef('numero_cuota')
        ).values('rut', 'patente', 'numero_cuota').annotate(
            total_abonos_sum=Coalesce(Sum('monto_cuota'), 0, output_field=DecimalField())
        ).values('total_abonos_sum')[:1]

        # Anotar el total de abonos a cada objeto Cuota
        # Filtrar según el parámetro 'historico':
        # - Si historico=true: SOLO cuotas de contratos con estado=1
        # - Si historico=false: SOLO cuotas de contratos con estado=0 (activos)
        if historico:
            # Mostrar SOLO contratos descartados (estado=1)
            cuotas = Cuota.objects.annotate(
                abono_total=Subquery(subquery_abonos)
            ).filter(
                Q(rut_cliente__in=Presupuesto.objects.filter(estado=1).values_list('rut_cliente', flat=True)) &
                Q(patente__in=Presupuesto.objects.filter(estado=1).values_list('patente_vehiculo', flat=True))
            )
            print(f"DEBUG: Filtrando SOLO contratos descartados (estado=1). Total: {cuotas.count()}")
        else:
            # Mostrar SOLO contratos activos (estado=0)
            cuotas = Cuota.objects.annotate(
                abono_total=Subquery(subquery_abonos)
            ).filter(
                Q(rut_cliente__in=Presupuesto.objects.filter(estado=0).values_list('rut_cliente', flat=True)) &
                Q(patente__in=Presupuesto.objects.filter(estado=0).values_list('patente_vehiculo', flat=True))
            )
            print(f"DEBUG: Filtrando SOLO contratos activos (estado=0). Total: {cuotas.count()}")
        
        # ----------------------------------------------------------------------
# LÓGICA DE FILTRADO POR RUT Y PATENTE
# ----------------------------------------------------------------------
        if rut_cliente:
            cuotas = cuotas.filter(rut_cliente=rut_cliente)
        print(f"DEBUG: Filtrando por rut_cliente={rut_cliente}. Total: {cuotas.count()}")

        if patente:
            cuotas = cuotas.filter(patente=patente)
        print(f"DEBUG: Filtrando por patente={patente}. Total: {cuotas.count()}")

# ----------------------------------------------------------------------
# LÓGICA DE FILTRADO POR NOMBRES/APELLIDOS
# ----------------------------------------------------------------------
        if nombres_filtro:
            ruts_coincidentes = Clientes.objects.filter(
        Q(nombres__icontains=nombres_filtro) | 
        Q(apellidos__icontains=nombres_filtro)
        ).values_list('rut', flat=True)
   


        # Ordenar el resultado
        cuotas = cuotas.order_by('rut_cliente', 'patente', 'numero_cuota' )

        if not rut_cliente and not patente and not nombres_filtro:
            print(f"DEBUG: No se proporcionaron filtros. Obteniendo todas las cuotas y ordendolas. Total: {cuotas.count()}")

        serializer = PagoCuotasSerializer(cuotas, many=True)
        
        return Response({'message': 'Cuotas obtenidas exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)


    def patch(self, request, pk, format=None):


        try:
            cuota = Cuota.objects.get(pk=pk)
        except Cuota.DoesNotExist:
            print(f"ERROR: Cuota no encontrada con PK: {pk}")
            return Response({"message": "Cuota no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Usar partial=True permite actualizar solo los campos proporcionados
        serializer = PagoCuotasSerializer(cuota, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            print(f"DEBUG: Cuota con PK {pk} actualizada exitosamente.")
            return Response({'message': 'Cuota actualizada exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            print(f"ERROR: Error de validacin en PATCH: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------

class TodosRegistrosPorRutPatenteAPIView(APIView):
    """
    Recupera todos los registros de DetallePagoCuotas para un rut_cliente y patente específicos.
    """
    def get(self, request, format=None):
        print("DEBUG: Entrando en TodosRegistrosPorRutPatenteAPIView.get")

        rut_cliente = request.query_params.get('rut_cliente', None)
        patente = request.query_params.get('patente', None)

    

        if not rut_cliente or not patente:
          
            return Response(
                {"message": "RUT de cliente y Patente son requeridos para obtener todos los registros de cuotas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        registros = DetallePagoCuotas.objects.filter(
            rut_cliente=rut_cliente,
            patente=patente
        ).order_by('numero_cuota')

        print(f"DEBUG: Registros obtenidos para RUT '{rut_cliente}' y Patente '{patente}'. Total: {registros.count()}")

        serializer = DetallePagoCuotasSerializer(registros, many=True)
        print("DEBUG: Registros serializados para la respuesta GET.")
        return Response({'message': 'Registros obtenidos exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)


# -----------------------------------------------------

class EliminarCuotasPorRutPatenteAPIView(APIView):
    """
    Gestiona la eliminación masiva de cuotas por rut_cliente y patente.
    """
    def delete(self, request, *args, **kwargs):
        print("DEBUG: Entrando en EliminarCuotasPorRutPatenteAPIView.delete")

        # Aceptar parámetros tanto de query_params como de request.data
        rut_cliente = request.query_params.get('rut') or request.data.get('rut_cliente')
        patente = request.query_params.get('patente') or request.data.get('patente')

        print(f"DEBUG: Solicitud de eliminación para RUT: {rut_cliente}, Patente: {patente}")

        if not rut_cliente or not patente:
            print("ERROR: RUT de cliente o patente no proporcionados para la eliminación.")
            return Response(
                {"message": "RUT de cliente y patente son requeridos para la eliminación."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cuotas_eliminadas, _ = Cuota.objects.filter(rut_cliente=rut_cliente, patente=patente).delete()

            if cuotas_eliminadas > 0:
                print(f"DEBUG: {cuotas_eliminadas} cuota(s) eliminada(s) exitosamente para RUT: {rut_cliente}, Patente: {patente}")
                return Response(
                    {"message": f"{cuotas_eliminadas} cuota(s) eliminada(s) exitosamente."},
                    status=status.HTTP_200_OK
                )
            else:
                print(f"DEBUG: No se encontraron cuotas para eliminar con el RUT: {rut_cliente} y Patente: {patente}.")
                return Response(
                    {"message": "No se encontraron cuotas para los criterios especificados."},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            print(f"ERROR: Excepción inesperada en EliminarCuotasPorRutPatenteAPIView: {str(e)}")
            return Response(
                {"message": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# -----------------------------------------------------
class CuotasImpagasAPIView(APIView):
    """
    Recupera cuotas con la lógica correcta de impago:
    (Vencida) AND (Abono_Total < Monto_Cuota)
    """
    def get(self, request, format=None):
        print("DEBUG: Entrando en CuotasImpagasAPIView.get")
        try:
            fecha_inicio_str = request.query_params.get('fecha_inicio')
            fecha_fin_str = request.query_params.get('fecha_fin')
            
            # 1. PRE-FILTRO: Solo cuotas que han vencido (reduce el queryset)
            # Y aquellas que aún no tienen la fecha de vencimiento.
            # EXCLUIR cuotas de contratos descartados
            cuotas_base = Cuota.objects.filter(
                Q(fecha_vencimiento__lt=date.today()) | Q(fecha_vencimiento__isnull=True)
            ).filter(
                # Filtrar solo cuotas cuyos contratos NO están descartados
                Q(rut_cliente__in=Presupuesto.objects.filter(estado=0).values_list('rut_cliente', flat=True)) &
                Q(patente__in=Presupuesto.objects.filter(estado=0).values_list('patente_vehiculo', flat=True))
            ).order_by('fecha_vencimiento')

            # 2. Aplicar filtro por rango de fechas de vencimiento si se proporcionaron
            if fecha_inicio_str:
                fecha_inicio = date.fromisoformat(fecha_inicio_str)
                cuotas_base = cuotas_base.filter(fecha_vencimiento__gte=fecha_inicio)
            if fecha_fin_str:
                fecha_fin = date.fromisoformat(fecha_fin_str)
                cuotas_base = cuotas_base.filter(fecha_vencimiento__lte=fecha_fin)
            
            # 3. Anotar el abono total (Subquery)
            # Esto mejora la eficiencia, aunque el Serializer todavía hace el chequeo de la DB.
            subquery_abonos = DetallePagoCuotas.objects.filter(
                rut=OuterRef('rut_cliente'),
                patente=OuterRef('patente'),
                numero_cuota=OuterRef('numero_cuota')
            ).values('rut', 'patente', 'numero_cuota').annotate(
                total_abonos_sum=Coalesce(Sum('monto_cuota'), 0, output_field=DecimalField())
            ).values('total_abonos_sum')[:1]

            cuotas_queryset = cuotas_base.annotate(
                # El abono_total anotado será usado por el get_abono_total del Serializer 
                # si lo modificas para no consultar la DB, pero lo dejamos por consistencia.
                abono_total_anotado=Subquery(subquery_abonos) 
            )

            # 4. Serializar para calcular 'dias_atraso' (que incluye la lógica de abono)
            # NO se debe iterar y calcular manualmente, sino dejar que el Serializer lo haga.
            serializer = PagoCuotasSerializer(cuotas_queryset, many=True)
            data_serializada = serializer.data
            
            # 5. FILTRO FINAL: Solo incluimos las cuotas que el Serializer marcó como impagas (dias_atraso > 0)
            # El Serializer contiene la regla de negocio de Monto Cuota vs. Abono Total.
            cuotas_filtradas = [
                item for item in data_serializada if item.get('dias_atraso', 0) > 0
            ]

            return Response(cuotas_filtradas, status=status.HTTP_200_OK)

        except Exception as e:
            # Manejo de errores 
            print(f"ERROR: Excepción en CuotasImpagasAPIView: {str(e)}")
            return Response(
                {"message": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# -----------------------------------------------------
class EliminarCuotasPoridAPIView(APIView):
    """
    Elimina una cuota específica por su ID (PK).
    """
    def delete(self, request, id):
        print(f"DEBUG: Entrando en EliminarCuotasPoridAPIView.delete para ID: {id}")
        try:
            num_eliminados, _ = Cuota.objects.filter(id=id).delete()

            if num_eliminados > 0:
                print(f"DEBUG: {num_eliminados} cuota(s) eliminada(s) exitosamente para ID: {id}")
                return Response(
                    {"message": f"{num_eliminados} cuota(s) eliminada(s) exitosamente."},
                    status=status.HTTP_200_OK
                )
            else:
                print(f"DEBUG: No se encontró cuota para eliminar con el ID: {id}.")
                return Response(
                    {"message": "No se encontró la cuota para el ID especificado."},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            print(f"ERROR: Excepción inesperada en EliminarCuotasPoridAPIView: {str(e)}")
            return Response(
                {"message": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )