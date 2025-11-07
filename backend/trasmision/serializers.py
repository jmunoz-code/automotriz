from rest_framework import serializers
from .models import  Trasmision  # Importa el modelo desde el archivo models.py local

class TrasmisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trasmision
        fields = '__all__'