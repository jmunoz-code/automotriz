from rest_framework import serializers
from .models import Auditoria


class AuditoriaSerializer(serializers.ModelSerializer):
    fecha_hora_formateada = serializers.SerializerMethodField()
    
    class Meta:
        model = Auditoria
        fields = [
            'id',
            'fecha_hora',
            'fecha_hora_formateada',
            'usuario',
            'pagina',
            'accion',
            'modulo_tabla',
            'descripcion',
            'valor_anterior',
            'valor_nuevo',
            'ip_usuario'
        ]
        read_only_fields = ['id', 'fecha_hora']
    
    def get_fecha_hora_formateada(self, obj):
        """Formatea la fecha y hora en formato legible"""
        if obj.fecha_hora:
            return obj.fecha_hora.strftime('%d-%m-%Y %H:%M:%S')
        return None
