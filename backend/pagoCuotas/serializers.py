# pago_cuotas/serializers.py (Versión Refinada)

from rest_framework import serializers
from django.db.models import Sum
from datetime import date
# Asumo que estos modelos están disponibles para PagoCuotasSerializer
from detallePagoCuotas.models import DetallePagoCuotas
from presupuesto.models import Presupuesto 
from clientes.models import Clientes
from .models import PagoCuotas


class PagoCuotasSerializer(serializers.ModelSerializer):
    fono = serializers.SerializerMethodField()
    nombres = serializers.SerializerMethodField()
    apellidos = serializers.SerializerMethodField()

    interes_mensual = serializers.SerializerMethodField()
    monto_a_financiar = serializers.SerializerMethodField()
    
    # ✅ Campo que calculará el monto total abonado
    abono_total = serializers.SerializerMethodField() 
    
    # ✅ Campo CLAVE que calculará los días de atraso si está impaga
    dias_atraso = serializers.SerializerMethodField() 
    
    numero_cuotas = serializers.SerializerMethodField()
    precio_venta = serializers.SerializerMethodField()
    valor_pie = serializers.SerializerMethodField()
    fecha_creacion = serializers.SerializerMethodField()

    class Meta:
        model = PagoCuotas
        fields = '__all__' 

    # --- MÉTODOS CLAVE CORREGIDOS ---
    
    def get_abono_total(self, obj):
        """
        Calcula la suma de todos los abonos para esta cuota.
        Usa DetallePagoCuotas y suma el campo 'monto_cuota' (que es el abono).
        """
        abono = DetallePagoCuotas.objects.filter(
            rut=obj.rut_cliente, # Coincide el campo 'rut' de DetallePagoCuotas con 'rut_cliente' de PagoCuotas
            patente=obj.patente,
            numero_cuota=obj.numero_cuota
        ).aggregate(Sum('monto_cuota'))
        
        # El resultado de la suma está en 'monto_cuota__sum'
        return abono['monto_cuota__sum'] or 0
    
    def get_dias_atraso(self, obj):
        """
        Determina si la cuota está REALMENTE impaga y calcula los días de atraso.
        Lógica: (Venció) AND (Abono < MontoCuota)
        """
        
        abono_total = self.get_abono_total(obj) # Monto total abonado
        monto_cuota = obj.monto_cuota or 0       # Monto que se debe pagar
        fecha_vencimiento = obj.fecha_vencimiento
        
        # 1. Chequeo de vencimiento
        if not fecha_vencimiento or fecha_vencimiento >= date.today():
            return 0 # No está vencida o falta el dato
        
        # 2. Chequeo de monto suficiente (Regla: Monto abonado < Monto cuota)
        if abono_total < monto_cuota:
            # Cuota vencida y con abono insuficiente -> Impaga
            return (date.today() - fecha_vencimiento).days
            
        # 3. Pago TARDÍO:
        # Según tu regla: "si se pago despues de la fecha de vencimiento y uyo monto sea mayor o igual al modelo pagoc.uotat no debe salir en el listado".
        # Esto significa que un pago COMPLETO (aunque sea tardío) hace que NO aparezca en el listado de impagos.
        # Por lo tanto, si abono_total >= monto_cuota, devolvemos 0 días de atraso.
        return 0

    # --- MÉTODOS DE CLIENTES/PRESUPUESTO (Sin Cambios) ---
    
    # ... (Todos los métodos get_fono, get_nombres, get_apellidos, etc., que ya tenías)
    def get_fono(self, obj):
        try:
            cliente = Clientes.objects.get(rut=obj.rut_cliente)
            return cliente.fono
        except Clientes.DoesNotExist:
            return None
        
    def get_nombres(self, obj):
        try:
            cliente = Clientes.objects.get(rut=obj.rut_cliente)
            return cliente.nombres
        except Clientes.DoesNotExist:
            return None
        
    def get_apellidos(self, obj):
        try:
            cliente = Clientes.objects.get(rut=obj.rut_cliente)
            return  cliente.apellidos
        except Clientes.DoesNotExist:
            return None
   
    def get_monto_a_financiar(self, obj):
        presupuesto = Presupuesto.objects.filter(
            rut_cliente=obj.rut_cliente,
            patente_vehiculo=obj.patente
        ).first()
        if presupuesto:
            return presupuesto.monto_a_financiar
        return None
    
    def get_numero_cuotas(self, obj):
        presupuesto = Presupuesto.objects.filter(
            rut_cliente=obj.rut_cliente,
            patente_vehiculo=obj.patente
        ).first()
        if presupuesto:
            return presupuesto.numero_cuotas
        return None
    
    def get_precio_venta(self, obj):
        presupuesto = Presupuesto.objects.filter(
            rut_cliente=obj.rut_cliente,
            patente_vehiculo=obj.patente
        ).first()
        if presupuesto:
            return presupuesto.precio_venta
        return None
    
    def get_valor_pie(self, obj):
        presupuesto = Presupuesto.objects.filter(
            rut_cliente=obj.rut_cliente,
            patente_vehiculo=obj.patente
        ).first()
        if presupuesto:
            return presupuesto.valor_pie
        return None
    
    def get_interes_mensual(self, obj):
        presupuesto = Presupuesto.objects.filter(
            rut_cliente=obj.rut_cliente,
            patente_vehiculo=obj.patente
        ).first()
        if presupuesto:
            return presupuesto.interes_mensual
        return None
    
    def get_fecha_creacion(self, obj):
        presupuesto = Presupuesto.objects.filter(
            rut_cliente=obj.rut_cliente,
            patente_vehiculo=obj.patente
        ).first()
        if presupuesto:
            return presupuesto.fecha_creacion
        return None