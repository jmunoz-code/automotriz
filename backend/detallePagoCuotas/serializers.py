# serializers.py
from rest_framework import serializers

from .models import  *  # Importa el modelo desde el archivo models.py local


class DetallePagoCuotasSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePagoCuotas
        fields = '__all__' # Incluye todos los campos del modelo