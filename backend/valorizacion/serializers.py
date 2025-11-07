from rest_framework import serializers
from .models import  Valorizacion  # Importa el modelo desde el archivo models.py local

class valorizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valorizacion
        fields = '__all__'