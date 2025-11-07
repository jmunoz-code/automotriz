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
from decimal import Decimal, ROUND_HALF_UP, getcontext # ⬅️ Importamos getcontext para configurar precisión

# Configuramos la precisión decimal para evitar errores de coma flotante
getcontext().prec = 28 # Usar alta precisión para los cálculos

# Importa tus serializadores y modelos
# 🟢 CORREGIDO: Importar el serializador con el nombre 'GenerarCuotasSerializer'
from generarCuotas.serializers import GenerarCuotasSerializer 

from .models import GenerarCuotas as Cuota


# 🟢 Nombre de Clase Consistente
class GenerarCuotasAPIView(APIView):
 
    # 🟢 CAMBIO: Ahora usamos GET para recibir los parámetros por URL
    def Post(self, request, format=None):
    
        # 1. Obtener datos de la URL (query_params)
        params = request.query_params

        try:
            # Validación y conversión manual de los parámetros de la URL
            rut_cliente = params['rut_cliente']
            patente = params['patente']
            
            # Conversión a tipos Python nativos
            cantidad_cuotas = int(params['numero_cuota'])
            
            # Conversión a Decimal y Date.
            # Los query params son STRINGS, así que se convierten directamente a Decimal.
            monto_cuota_fija = Decimal(params['monto_cuota']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            monto_prestamo = Decimal(params['monto_prestamo']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            interes_mensual = Decimal(params['interes_mensual'])
            
            # Conversión de fecha (asumiendo formato YYYY-MM-DD, que es el estándar ISO)
            fecha_vencimiento_inicial = date.fromisoformat(params['fecha_vencimiento'])

            # Cáculo de la tasa de interés
            interes_mensual_tasa = (interes_mensual / 100).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)

            generated_cuotas = []
            saldo_pendiente = monto_prestamo 
 
            with transaction.atomic():
                for i in range(cantidad_cuotas):
                    # Uso de dateutil.relativedelta para el cálculo de meses (importado arriba)
                    fecha_cuota = (fecha_vencimiento_inicial + relativedelta(months=i))
                    
                    # 2. Cálculos (Interés y Capital)
                    interes_esta_cuota = (saldo_pendiente * interes_mensual_tasa).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    capital_amortizado_esta_cuota = (monto_cuota_fija - interes_esta_cuota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    
                    # Ajuste del saldo pendiente
                    saldo_pendiente -= capital_amortizado_esta_cuota
                    
                    # 3. Ajuste de la última cuota para cuadrar el saldo
                    if i == cantidad_cuotas - 1:
                        # Ajustamos el abono a capital para que el saldo sea 0.00 (manejo de errores de redondeo)
                        capital_amortizado_esta_cuota += saldo_pendiente.quantize(Decimal('0.01'))
                        saldo_pendiente = Decimal('0.00') # Forzamos el saldo a cero
                        
                    # 4. Creación de la instancia del modelo (Grabar en BDD)
                    cuota = Cuota.objects.create(
                        rut_cliente=rut_cliente,
                        patente=patente,
                        numero_cuota=i + 1,
                        fecha_vencimiento=fecha_cuota,
                        monto_cuota=monto_cuota_fija,
                        abono_capital=capital_amortizado_esta_cuota, 
                        fecha_pago=None,
                        observacion=None,
                    )
                    generated_cuotas.append(cuota)
            
            # 5. Respuesta (Usando el Serializador solo para el OUTPUT)
            response_serializer = GenerarCuotasSerializer(generated_cuotas, many=True)
            return Response({'message': 'Cuotas generadas exitosamente y guardadas en la base de datos.', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)

        except KeyError as ke:
            # Error en datos de entrada (falta un campo requerido en la URL)
            required_fields = ['rut_cliente', 'patente', 'numero_cuota', 'monto_cuota', 'fecha_vencimiento', 'monto_prestamo', 'interes_mensual']
            return Response({
                "error": f"Faltan parámetros requeridos en la URL: {str(ke)}.", 
                "detalle": f"Asegúrese de incluir todos los siguientes campos como query parameters: {', '.join(required_fields)}."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except (ValueError, TypeError) as ve:
            # Error de conversión (ej. "abc" en lugar de número o formato de fecha incorrecto)
            return Response({
                "error": "Error de formato de datos.", 
                "detalle": f"Asegúrese de que los campos numéricos y de fecha (YYYY-MM-DD) estén correctos. Detalle: {str(ve)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Cualquier otro error interno (ej. problemas de BDD, cálculos, etc.)
            return Response({"error": f"Error interno al generar las cuotas: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
