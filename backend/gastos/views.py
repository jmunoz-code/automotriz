from rest_framework import viewsets, permissions
from .models import Gasto
from .serializers import GastoSerializer

class GastoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para el CRUD de Gastos.
    """
    queryset = Gasto.objects.all()
    serializer_class = GastoSerializer
    
    # --- ¡CAMBIO CRÍTICO! ---
    # Lo ponemos en 'AllowAny' para que sea público,
    # igual que tu API de Tipo_arriendo.
    permission_classes = [permissions.AllowAny]

