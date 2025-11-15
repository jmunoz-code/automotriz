from rest_framework import viewsets, permissions
from .models import TipoArriendo
from .serializers import TipoArriendoSerializer

class TipoArriendoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver, crear, editar y eliminar Tipos de Arriendo.
    """
    queryset = TipoArriendo.objects.all()
    serializer_class = TipoArriendoSerializer
    # Opcional: Define permisos si tienes autenticación configurada
    # permission_classes = [permissions.IsAuthenticated]