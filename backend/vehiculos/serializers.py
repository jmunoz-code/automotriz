from rest_framework import serializers
from .models import * # Importa todos los modelos, incluyendo Vehiculos y Costos

# Serializador para el modelo Costos

class VehiculosSerializer(serializers.ModelSerializer):
    # Campos existentes
    tipo_marca_id = serializers.IntegerField()
    tipo_vehiculo_id = serializers.IntegerField()
       

    marca_descripcion = serializers.SerializerMethodField()
    vehiculo_descripcion = serializers.SerializerMethodField()
       

    class Meta:
        model = Vehiculos
        fields = [
            'id',
            'tipo_marca_id',
            'tipo_vehiculo_id',
            'tipo_combustible',
            'tipo_trasmision',
            'modelo',
            'agno',
            'numero_motor',
            'numero_chasis',
            'color',
            'patente',
            'kilometraje',
            'estado',
            'precio_compra',
            'marca_descripcion',
            'vehiculo_descripcion',
            'precio_venta',
            # NUEVO CAMPO
            'propiedad_automotriz',
            'revision_tecnica_al_dia',
            'permiso_circulacion',
            'seguro_vigente'
        ]

    # Método para obtener la descripción de la marca
    def get_marca_descripcion(self, obj):
        if obj.tipo_marca:
            return obj.tipo_marca.descripcion
        return None

    # Método para obtener la descripción del tipo de vehículo
    def get_vehiculo_descripcion(self, obj):
        if obj.tipo_vehiculo:
            return obj.tipo_vehiculo.descripcion
        return None