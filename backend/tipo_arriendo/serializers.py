from rest_framework import serializers
from .models import TipoArriendo

class TipoArriendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoArriendo
        # --- CAMPO AÑADIDO ---
        fields = ['id', 'nombre', 'comision']