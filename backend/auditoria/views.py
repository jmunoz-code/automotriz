from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Auditoria
from .serializers import AuditoriaSerializer
from django.db.models import Q


class AuditoriaAPIView(APIView):
    """
    API para consultar registros de auditoría
    """
    def get(self, request):
        try:
            # Obtener parámetros de filtro opcionales
            usuario = request.query_params.get('usuario', None)
            accion = request.query_params.get('accion', None)
            modulo = request.query_params.get('modulo', None)
            fecha_desde = request.query_params.get('fecha_desde', None)
            fecha_hasta = request.query_params.get('fecha_hasta', None)
            
            # Consulta base
            queryset = Auditoria.objects.all()
            
            # Aplicar filtros si existen
            if usuario:
                queryset = queryset.filter(usuario__icontains=usuario)
            
            if accion:
                queryset = queryset.filter(accion=accion)
            
            if modulo:
                queryset = queryset.filter(modulo_tabla__icontains=modulo)
            
            if fecha_desde:
                queryset = queryset.filter(fecha_hora__gte=fecha_desde)
            
            if fecha_hasta:
                queryset = queryset.filter(fecha_hora__lte=fecha_hasta)
            
            # Limitar a los últimos 1000 registros para performance
            total_count = queryset.count()
            queryset = queryset[:1000]
            
            serializer = AuditoriaSerializer(queryset, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'count': total_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al obtener registros de auditoría: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """
        Crear un nuevo registro de auditoría
        """
        try:
            # Obtener IP del usuario
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Agregar IP a los datos si no está presente
            data = request.data.copy()
            if 'ip_usuario' not in data:
                data['ip_usuario'] = ip
            
            serializer = AuditoriaSerializer(data=data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Registro de auditoría creado exitosamente',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al crear registro de auditoría: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
