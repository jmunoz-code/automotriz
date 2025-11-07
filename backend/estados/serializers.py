from rest_framework import serializers
from .models import  Estados  # Importa el modelo desde el archivo models.py local

class EstadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = '__all__'