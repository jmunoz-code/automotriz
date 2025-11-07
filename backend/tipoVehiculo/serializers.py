from rest_framework import serializers
from .models import  TipoVehiculo  # Importa el modelo desde el archivo models.py local

class TipoVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoVehiculo
        fields = '__all__'