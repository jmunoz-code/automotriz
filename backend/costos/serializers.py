from rest_framework import serializers

from costos.models import Costos

class CostosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Costos
        #fields= ("id","nombre", "slug")
        fields= '__all__'
        # fields= ('__all__')