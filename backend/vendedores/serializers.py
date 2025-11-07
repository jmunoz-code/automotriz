# serializers.py
from rest_framework import serializers
from .models import Vendedores
from django.contrib.auth.hashers import make_password # <--- ¡Importa esto!

class VendedoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedores
        fields = '__all__'
        # Opcional: Si no quieres que la clave sea retornada en las respuestas GET
        extra_kwargs = {'clave': {'write_only': True}}

    # Sobreescribir el método create para hashear la contraseña
    def create(self, validated_data):
        if 'clave' in validated_data:
            # Hashear la contraseña antes de guardarla
            validated_data['clave'] = make_password(validated_data['clave'])
        return super().create(validated_data)

    # Sobreescribir el método update para hashear la contraseña si se actualiza
    def update(self, instance, validated_data):
        if 'clave' in validated_data:
            # Hashear la nueva contraseña antes de actualizar
            validated_data['clave'] = make_password(validated_data['clave'])
        return super().update(instance, validated_data)
    
    