from rest_framework import serializers

from .models import  *  # Importa el modelo desde el archivo models.py local


class ClientesSerializer(serializers.ModelSerializer):
     
   # habilitado = serializers.IntegerField(source='habilitado')

    class Meta:
        model = Clientes
        
        fields= '__all__'
        