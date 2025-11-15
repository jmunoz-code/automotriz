from django.shortcuts import render

# Create your views here.
# reservas/views.py

from rest_framework import viewsets
from rest_framework.response import Response
from .models import Reserva
from .serializers import ReservaSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver, crear, editar y eliminar Reservas.
    """
    queryset = Reserva.objects.all().order_by('-fecha_inicio') # Ordenar por fecha
    serializer_class = ReservaSerializer

    # --- ¡Personalización Importante! ---
    # Tu frontend (IngresoReservas.vue, línea 120) espera que la lista
    # de reservas venga dentro de una clave "data".
    # Vamos a sobrescribir el método 'list' para que haga eso.
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # Envolvemos la respuesta estándar ([...]) en un diccionario {"data": [...]}
        return Response({'data': serializer.data})

    # Los métodos create(), update(), retrieve() y destroy() 
    # funcionarán bien sin cambios.