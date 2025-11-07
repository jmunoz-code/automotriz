from rest_framework import serializers
from .models import TipoPago  # Importa el modelo desde el archivo models.py local

class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPago
        fields = '__all__'