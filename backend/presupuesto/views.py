from datetime import datetime
from http import HTTPStatus
from urllib import request
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from .models import *
from .serializers import PresupuestoSerializer
from django.db.models import Q 
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta
from pagoCuotas.models import PagoCuotas

class Clase1(APIView):
    def get(self, request):
        # Excluir contratos descartados (estado=1)
        data = Presupuesto.objects.filter(estado=0).order_by('-fecha_creacion').all()
        datos_json = PresupuestoSerializer(data, many=True)
        return JsonResponse({"data": datos_json.data}, status=HTTPStatus.OK)

    def post(self, request):
        modified_data = request.data.copy()
        if 'nombre_cliente' in modified_data and modified_data['nombre_cliente']:
            modified_data['nombre_cliente'] = modified_data['nombre_cliente'].upper()

        # VALIDACIÓN DE DUPLICADOS: Verificar si ya existe un contrato activo con este RUT y Patente


        serializer = PresupuestoSerializer(data=modified_data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
                            status=HTTPStatus.CREATED)
        except ValidationError as e:
            print("Serializer Errors:", e.detail)
            return Response({"estado": "error", "mensaje": e.detail},
                            status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            print("Unexpected Error:", str(e))
            return Response({"estado": "error", "mensaje": "Ocurrio un error inesperado en el servidor."},
                            status=HTTPStatus.INTERNAL_SERVER_ERROR)

class Clase2(APIView):
    def get(self, request, id):
        try:
            presupuesto = Presupuesto.objects.filter(id=id).get()
            serializer = PresupuestoSerializer(presupuesto)
            return Response({"data": serializer.data}, status=HTTPStatus.OK)
        except Presupuesto.DoesNotExist:
            return Response({"error": "Presupuesto no encontrado."}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return Response({"error": "Ocurrio un error inesperado."},
                            status=HTTPStatus.INTERNAL_SERVER_ERROR)
     
    def put(self, request, id):
        try:
            from datetime import datetime, date
            
            presupuesto_instance = Presupuesto.objects.get(id=id)
            
            # Guardar la fecha anterior para comparar
            fecha_anterior = presupuesto_instance.fecha_inicio_pago
            rut_cliente = presupuesto_instance.rut_cliente
            patente = presupuesto_instance.patente_vehiculo
            
            # Parsear la nueva fecha directamente del request para evitar problemas de timezone
            fecha_inicio_pago_str = request.data.get('fecha_inicio_pago')
            fecha_nueva_raw = None
            if fecha_inicio_pago_str:
                try:
                    # Parsear la fecha desde el string YYYY-MM-DD (sin timezone)
                    fecha_nueva_raw = datetime.strptime(fecha_inicio_pago_str, '%Y-%m-%d').date()
                    print(f"Fecha parseada desde request: {fecha_nueva_raw}")
                except ValueError:
                    print(f"No se pudo parsear fecha: {fecha_inicio_pago_str}")
            
            serializer = PresupuestoSerializer(presupuesto_instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                # Obtener la nueva fecha (usar la parseada si existe, sino la del serializer)
                if fecha_nueva_raw:
                    fecha_nueva = fecha_nueva_raw
                else:
                    fecha_nueva = serializer.instance.fecha_inicio_pago
                    # Convertir a date si es datetime
                    if hasattr(fecha_nueva, 'date'):
                        fecha_nueva = fecha_nueva.date() if callable(fecha_nueva.date) else fecha_nueva
                
                print(f"Fecha anterior: {fecha_anterior}, Fecha nueva: {fecha_nueva}")
                
                # Si la fecha cambió, recalcular las fechas de las cuotas
                if fecha_anterior != fecha_nueva:
                    print(f"Fecha de vencimiento cambió de {fecha_anterior} a {fecha_nueva}")
                    print(f"Recalculando cuotas para RUT: '{rut_cliente}', Patente: '{patente}'")
                    print(f"Fecha base para cálculo: {fecha_nueva} (tipo: {type(fecha_nueva)})")
                    
                    # Debug: Ver todas las cuotas que existen para este cliente
                    todas_cuotas = PagoCuotas.objects.all()
                    print(f"Total cuotas en la BD: {todas_cuotas.count()}")
                    cuotas_cliente = PagoCuotas.objects.filter(rut_cliente=rut_cliente)
                    print(f"Cuotas para RUT '{rut_cliente}': {cuotas_cliente.count()}")
                    if cuotas_cliente.exists():
                        print("Detalles de las cuotas encontradas para este RUT:")
                        for c in cuotas_cliente[:5]:  # Mostrar solo las primeras 5
                            print(f"  - Cuota {c.numero_cuota}, RUT: '{c.rut_cliente}', Patente: '{c.patente}'")
                    
                    # Obtener todas las cuotas de este contrato ordenadas por número
                    cuotas = PagoCuotas.objects.filter(
                        rut_cliente=rut_cliente,
                        patente=patente
                    ).order_by('numero_cuota')
                    
                    print(f"Cuotas filtradas por RUT y Patente: {cuotas.count()}")
                    
                    # Recalcular las fechas de vencimiento
                    cuotas_actualizadas = 0
                    for cuota in cuotas:
                        # La fecha de vencimiento es: fecha_nueva + (numero_cuota - 1) meses
                        nueva_fecha_vencimiento = fecha_nueva + relativedelta(months=cuota.numero_cuota - 1)
                        print(f"Cuota {cuota.numero_cuota}: {cuota.fecha_vencimiento} -> {nueva_fecha_vencimiento}")
                        cuota.fecha_vencimiento = nueva_fecha_vencimiento
                        cuota.save()
                        cuotas_actualizadas += 1
                    
                    print(f"Se actualizaron {cuotas_actualizadas} cuotas")
                    
                return Response({"data": serializer.data, "message": "modificado exitosamente"}, status=HTTPStatus.OK)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        except Presupuesto.DoesNotExist:
            return Response({"error": "Presupuesto no encontrado."}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"Ocurrio un error inesperado al modificar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            presu = Presupuesto.objects.get(id=id)
            presu.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        except presu.DoesNotExist:
            raise NotFound(f"No se encontró : {id}")
        except Exception as e:
            return Response({"error": f"Ocurrio un error inesperado al eliminar: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
class Clase3(APIView):
    def get(self, request, id):
        try:
            pre = Presupuesto.objects.filter(id=id).get()
            serializer = PresupuestoSerializer(pre)
            return Response({"data": serializer.data}, status=HTTPStatus.OK)
        except Exception as e:
            return Response({"error": "Ocurrio un error inesperado."},
                            status=HTTPStatus.INTERNAL_SERVER_ERROR)

class Clase4(APIView):
    def get(self, request, patente):
        try:
            cliente = Presupuesto.objects.filter(patente_vehiculo=patente).order_by('-id').first()
            if not cliente:
                 return Response({"error": f"No se encontro presupuesto para patente {patente}"}, status=HTTPStatus.NOT_FOUND)
            serializer = PresupuestoSerializer(cliente)
            return Response({"data": serializer.data}, status=HTTPStatus.OK)
        except Exception as e:
            return Response({"error": "Ocurrio un error inesperado."},
                            status=HTTPStatus.INTERNAL_SERVER_ERROR)

class PresupuestoListAPIView(APIView):
    
    def get(self, request):
        # 1. Obtener el Queryset base - INCLUIR TODOS los contratos para el informe
        queryset = Presupuesto.objects.order_by('fecha_creacion').all()
        
        # 2. Obtener los parámetros de la URL
        nombre = request.query_params.get('nombre', None)
        rut = request.query_params.get('rut', None)
        patente = request.query_params.get('patente', None)
        fecha_inicio_ingresada = request.query_params.get('fecha_inicio', None)
        fecha_fin_ingresada = request.query_params.get('fecha_fin', None)
        
        # Objeto Q para acumular filtros
        filtros = Q()

        # 3. Construir filtros de texto (nombre, rut, patente)
        if nombre:
            filtros &= Q(nombre_cliente__icontains=nombre)
        if rut:
            filtros &= Q(rut_cliente__icontains=rut)
        if patente:
            filtros &= Q(patente_vehiculo__icontains=patente)

        # 4. Lógica de filtro de fecha CORREGIDA (usando __gte y __lte) 🚀
        if fecha_inicio_ingresada and fecha_fin_ingresada:
            # Rango de fechas: Desde (inclusive) y Hasta (inclusive)
            filtros &= Q(fecha_creacion__gte=fecha_inicio_ingresada) & Q(fecha_creacion__lte=fecha_fin_ingresada)
        elif fecha_inicio_ingresada:
            # Solo fecha de inicio: Mayor o igual que
            filtros &= Q(fecha_creacion__gte=fecha_inicio_ingresada)
        elif fecha_fin_ingresada:
            # Solo fecha de fin: Menor o igual que
            filtros &= Q(fecha_creacion__lte=fecha_fin_ingresada)

        # 5. Aplicar los filtros al Queryset
        if filtros:
            queryset = queryset.filter(filtros)
        
        # 6. Serializar y devolver la respuesta
        datos_json = PresupuestoSerializer(queryset, many=True)
        return JsonResponse({"data": datos_json.data}, status=HTTPStatus.OK)

   
    def post(self, request):
        return Response({"error": "El método POST no está implementado para esta ruta."}, status=HTTPStatus.METHOD_NOT_ALLOWED)
   

   # --- NUEVA CLASE DEDICADA SOLO PARA ACTUALIZAR EL CAMPO 'ESTADO' ---
# ... (otras importaciones y clases)

# --- VISTA DEDICADA SOLO PARA ACTUALIZAR EL CAMPO 'ESTADO' (Usando PATCH) ---
class PresupuestoEstadoUpdateAPIView(APIView):
    
    def patch(self, request, id): 
        
        # 1. Buscar la instancia del Presupuesto por ID
        try:
            presupuesto = Presupuesto.objects.get(id=id)
        except Presupuesto.DoesNotExist:
            raise NotFound(f"No se encontro ningun Presupuesto con ID: {id}")
        
        # 2. Obtener el nuevo estado (esperamos 'estado' como entero: 1 o 0)
        nuevo_estado_raw = request.data.get('estado')

        if nuevo_estado_raw is None:
            return Response({"estado": "error", "mensaje": "El campo 'estado' (1 o 0) es requerido para esta operacion."},
                            status=HTTPStatus.BAD_REQUEST)
        
        try:
            # Convertir el valor a entero y validar que sea 0 o 1
            nuevo_estado = int(nuevo_estado_raw)
            if nuevo_estado not in [0, 1]:
                 raise ValueError
        except ValueError:
             return Response({"estado": "error", "mensaje": "El valor de 'estado' debe ser 1 (Habilitado) o 0 (Deshabilitado)."},
                            status=HTTPStatus.BAD_REQUEST)

        # 3. Actualizar solo el campo 'estado' y guardar
        try:
            presupuesto.estado = nuevo_estado
            presupuesto.save(update_fields=['estado'])
            
            return Response({"estado": "ok", 
                             "mensaje": f"Estado del Presupuesto {id} actualizado a '{nuevo_estado}' exitosamente."},
                            status=HTTPStatus.OK)
        except Exception as e:
            return Response({"error": f"Ocurrio un error inesperado al actualizar el estado: {e}"},
                            status=HTTPStatus.INTERNAL_SERVER_ERROR)
# ----------------------------------------------------------------------

# --- VISTA PARA ACTUALIZAR ESTADO POR RUT Y PATENTE ---
class PresupuestoEstadoByRutPatenteAPIView(APIView):
    
    def patch(self, request, rut, patente): 
        
        # 1. Buscar instancias del Presupuesto por RUT y PATENTE
        presupuestos = Presupuesto.objects.filter(rut_cliente=rut, patente_vehiculo=patente)
        
        if not presupuestos.exists():
            raise NotFound(f"No se encontró ningún Presupuesto con RUT: {rut} y PATENTE: {patente}")
        
        # 2. Obtener el nuevo estado (esperamos 'estado' como entero: 1 o 0)
        nuevo_estado_raw = request.data.get('estado')

        if nuevo_estado_raw is None:
            return Response({"estado": "error", "mensaje": "El campo 'estado' (1 o 0) es requerido para esta operación."},
                            status=HTTPStatus.BAD_REQUEST)
        
        try:
            # Convertir el valor a entero y validar que sea 0 o 1
            nuevo_estado = int(nuevo_estado_raw)
            if nuevo_estado not in [0, 1]:
                 raise ValueError
        except ValueError:
             return Response({"estado": "error", "mensaje": "El valor de 'estado' debe ser 1 (Descartado) o 0 (Activo)."},
                            status=HTTPStatus.BAD_REQUEST)

        # 3. Actualizar el campo 'estado' para TODOS los registros coincidentes
        try:
            # Usamos update() en el queryset para actualizar todos de una vez
            presupuestos.update(estado=nuevo_estado)
             
            mensaje = f"Presupuesto(s) {rut}-{patente} {'descartado(s)' if nuevo_estado == 1 else 'reactivado(s)'} exitosamente."
            return Response({"estado": "ok", "mensaje": mensaje},
                            status=HTTPStatus.OK)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado al actualizar el estado: {e}"},
                            status=HTTPStatus.INTERNAL_SERVER_ERROR)
# ----------------------------------------------------------------------