from rest_framework import serializers

from detalle.models import detalle

class detalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = detalle
        #fields= ("id","nombre", "slug")
        fields= '__all__'
        # fields= ('__all__')