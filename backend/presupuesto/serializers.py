# serializers.py
from rest_framework import serializers

from clientes.models import Clientes
from .models import Presupuesto
from vehiculos.models import Vehiculos
from django.db.models import Sum
from costos.models import Costos

class PresupuestoSerializer(serializers.ModelSerializer):
    # Campos calculados para el vehículo
    modelo_vehiculo = serializers.SerializerMethodField()
    marca_vehiculo = serializers.SerializerMethodField()
    apellidos = serializers.SerializerMethodField()
    
    # Campos calculados para la información financiera
    precio_compra = serializers.SerializerMethodField()
    sumatoria_gastos = serializers.SerializerMethodField()
    utilidad = serializers.SerializerMethodField()

    class Meta:
        model = Presupuesto
        fields = [
            'id',
            'rut_cliente',
            'rut_vendedor',
            'nombre_cliente',
            'patente_vehiculo',
            'tipo_pago',
            'valor_pie',
            'numero_cuotas',
            'monto_a_financiar',
            'valor_cuota',
            'interes_mensual',
            'fecha_creacion',
            'fecha_inicio_pago',
            'precio_venta',
            'precio_compra',
            'modelo_vehiculo',
            'marca_vehiculo',
            'sumatoria_gastos',
            'utilidad',
            'apellidos',
            'estado',
            'pausa',
        ]

    def get_modelo_vehiculo(self, obj):
        try:
            vehiculo = Vehiculos.objects.get(patente=obj.patente_vehiculo)
            return vehiculo.modelo
        except Vehiculos.DoesNotExist:
            return None

    def get_marca_vehiculo(self, obj):
        try:
            vehiculo = Vehiculos.objects.get(patente=obj.patente_vehiculo)
            if hasattr(vehiculo, 'tipo_marca') and vehiculo.tipo_marca:
                return vehiculo.tipo_marca.descripcion
            return None
        except Vehiculos.DoesNotExist:
            return None

    def get_precio_compra(self, obj):
        try:
            vehiculo = Vehiculos.objects.get(patente=obj.patente_vehiculo)
            return vehiculo.precio_compra
        except Vehiculos.DoesNotExist:
            return 0
            
    def get_sumatoria_gastos(self, obj):
        # Filtra los gastos por la patente del presupuesto
        gastos_agregados = Costos.objects.filter(patente=obj.patente_vehiculo).aggregate(total=Sum('valor'))
        # Retorna el total de los gastos, o 0 si no hay ninguno
        return gastos_agregados['total'] if gastos_agregados['total'] is not None else 0

    def get_utilidad(self, obj):
        try:
            vehiculo = Vehiculos.objects.get(patente=obj.patente_vehiculo)
            # Asegura que los valores sean numéricos (o 0 si son nulos) para evitar errores de cálculo
            precio_compra = vehiculo.precio_compra if vehiculo.precio_compra is not None else 0
            
            # Obtiene la sumatoria de gastos para el cálculo de la utilidad
            sumatoria_gastos = self.get_sumatoria_gastos(obj)
            
            if obj.precio_venta is not None:
                # La utilidad es el precio de venta menos el precio de compra y los gastos
                return obj.precio_venta - precio_compra - sumatoria_gastos
            return 0
        except Vehiculos.DoesNotExist:
            return 0
        

    def get_apellidos(self, obj):
        try:
            cliente = Clientes.objects.get(rut=obj.rut_cliente)
            return  cliente.apellidos
        except Clientes.DoesNotExist:
            return None    