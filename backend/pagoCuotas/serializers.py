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
        abonos_map = self.context.get('abonos_map')
        if abonos_map is not None:
            return abonos_map.get((obj.rut_cliente, obj.patente, obj.numero_cuota), 0)
            
        # Fallback si no hay contexto (compatibilidad)
        abono = DetallePagoCuotas.objects.filter(
            rut=obj.rut_cliente, 
            patente=obj.patente,
            numero_cuota=obj.numero_cuota
        ).aggregate(Sum('monto_cuota'))
        return abono['monto_cuota__sum'] or 0
    
    def get_dias_atraso(self, obj):
        abono_total = self.get_abono_total(obj) # Usa la lógica optimizada
        monto_cuota = obj.monto_cuota or 0
        fecha_vencimiento = obj.fecha_vencimiento
        
        if not fecha_vencimiento or fecha_vencimiento >= date.today():
            return 0
        
        if abono_total < monto_cuota:
            return (date.today() - fecha_vencimiento).days
        return 0

    # --- MÉTODOS DE CLIENTES/PRESUPUESTO OPTIMIZADOS ---
    
    def _get_cliente(self, rut):
        clientes_map = self.context.get('clientes_map')
        if clientes_map is not None:
            return clientes_map.get(rut)
        try:
            return Clientes.objects.get(rut=rut)
        except Clientes.DoesNotExist:
            return None

    def _get_presupuesto(self, rut, patente):
        presupuestos_map = self.context.get('presupuestos_map')
        if presupuestos_map is not None:
            return presupuestos_map.get((rut, patente))
        return Presupuesto.objects.filter(rut_cliente=rut, patente_vehiculo=patente).first()

    def get_fono(self, obj):
        cliente = self._get_cliente(obj.rut_cliente)
        return cliente.fono if cliente else None
        
    def get_nombres(self, obj):
        cliente = self._get_cliente(obj.rut_cliente)
        return cliente.nombres if cliente else None
        
    def get_apellidos(self, obj):
        cliente = self._get_cliente(obj.rut_cliente)
        return  cliente.apellidos if cliente else None
    
    def get_monto_a_financiar(self, obj):
        p = self._get_presupuesto(obj.rut_cliente, obj.patente)
        return p.monto_a_financiar if p else None
    
    def get_numero_cuotas(self, obj):
        p = self._get_presupuesto(obj.rut_cliente, obj.patente)
        return p.numero_cuotas if p else None
    
    def get_precio_venta(self, obj):
        p = self._get_presupuesto(obj.rut_cliente, obj.patente)
        return p.precio_venta if p else None
    
    def get_valor_pie(self, obj):
        p = self._get_presupuesto(obj.rut_cliente, obj.patente)
        return p.valor_pie if p else None
    
    def get_interes_mensual(self, obj):
        p = self._get_presupuesto(obj.rut_cliente, obj.patente)
        return p.interes_mensual if p else None
    
    def get_fecha_creacion(self, obj):
        p = self._get_presupuesto(obj.rut_cliente, obj.patente)
        return p.fecha_creacion if p else None