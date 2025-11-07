from rest_framework import serializers
from .models import TipoCombustible  # Importa el modelo desde el archivo models.py local

class TipoCombustibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCombustible
        fields = '__all__'