from rest_framework import serializers

from .models import  *  # Importa el modelo desde el archivo models.py local


class ContratosSerializer(serializers.ModelSerializer):
     
   # habilitado = serializers.IntegerField(source='habilitado')

    marca_descripcion = serializers.SerializerMethodField()
    vehiculo_descripcion = serializers.SerializerMethodField()

    class Meta:
        model = Contratos
        
        fields= '__all__'
        