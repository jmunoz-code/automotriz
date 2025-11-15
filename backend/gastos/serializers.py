from rest_framework import serializers
from .models import Gasto

class GastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gasto
        fields = [
            'id', 
            'fecha', 
            'descripcion', 
            'valor', 
            'creado_en'
        ]
        read_only_fields = ['creado_en']