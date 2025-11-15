from rest_framework import serializers
from .models import Reserva
# No necesitamos importar TipoArriendo aquí

class ReservaSerializer(serializers.ModelSerializer):
    # Campo extra de SOLO LECTURA para mostrar el nombre en la lista del frontend
    tipo_arriendo_nombre = serializers.CharField(
        source='tipo_arriendo.nombre', 
        read_only=True
    )

    class Meta:
        model = Reserva
        # 'tipo_arriendo' ahora se referirá al ID (ForeignKey)
        # 'tipo_arriendo_nombre' nos dará el texto para mostrar
        fields = [
            'id', 
            'rut_arrendatario', 
            'nombre_arrendatario',
            'fecha_inicio',
            'fecha_fin',
            'tipo_arriendo', # <--- Este será el ID (ej: 8)
            'tipo_arriendo_nombre', # <-- Este será el texto (ej: "Otro Privado")
            'valor_arriendo'
        ]