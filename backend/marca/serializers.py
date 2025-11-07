# D:\automotriz\backend\marca\serializers.py
from rest_framework import serializers
from .models import Marca  # <--- IMPORTA EL MODELO MARCA DESDE EL models.py DE ESTA MISMA APP

class MarcaSerializer(serializers.ModelSerializer):
  class Meta:
        model = Marca
        fields = ['id', 'tipo_marca', 'descripcion'] #