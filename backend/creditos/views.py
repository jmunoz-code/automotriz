# creditos/views.py (AJUSTE NECESARIO)
# creditos/views.py (función buscar_creditos_rapido)

from http import HTTPStatus
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import Q # <--- ¡ASEGÚRATE DE

from clientes.models import Clientes
from presupuesto.models import Presupuesto # Asegúrate de que esta importación esté

@api_view(['GET'])
def buscar_creditos_rapido(request):
    """
    Busca créditos solo por Nombre, RUT o Patente. 
    Adjunta el Apellido para que solo aparezca en el frontend.
    """
    
    termino = request.query_params.get('q', '').strip()

    print(termino)

    if not termino or len(termino) < 3:
        return JsonResponse({'success': True, 'data': []})

    # 1. CONSTRUCCIÓN DE LA CONSULTA (Solo campos de Presupuesto)
    filtro_q = (
        Q(rut_cliente__icontains=termino) |          # Busca por RUT (campo en Presupuesto)
        Q(nombre_cliente__icontains=termino) |       # Busca por Nombre (campo en Presupuesto)
        Q(patente_vehiculo__icontains=termino)       # Busca por Patente (campo en Presupuesto)
    )
    
    try:
        # 2. OBTENER RESULTADOS INICIALES
        # Busca en Presupuesto con el filtro_q. Solo pide los campos que necesita.
        resultados_presupuesto = Presupuesto.objects.filter(filtro_q).values(
            'rut_cliente', 
            'nombre_cliente', 
            'patente_vehiculo',
       
            
        ).distinct()[:10]
        
        # 3. RECUPERAR LOS APELLIDOS POR SEPARADO (Solamente para que aparezca)
        ruts_encontrados = [item['rut_cliente'] for item in resultados_presupuesto]
        
        # Busca los apellidos en la tabla Clientes con los RUTs encontrados
        apellidos_map = { 
            c.rut: c.apellidos for c in Clientes.objects.filter(rut__in=ruts_encontrados).only('rut', 'apellidos')
        }
        
        # 4. FORMATEAR LA RESPUESTA
        data = [
            {
                "rut_cliente": item['rut_cliente'],
                "nombres_completos": item['nombre_cliente'], 
                "patente": item['patente_vehiculo'],
                # Adjunta el apellido, que solo aparecerá en el frontend.
                "apellidos_cliente": apellidos_map.get(item['rut_cliente'], '')
            }
            for item in resultados_presupuesto
        ]
        print(data)
        return JsonResponse({'success': True, 'data': data})
    

    except Exception as e:
        print(f"ERROR en buscar_creditos_rapido: {e}")
        return JsonResponse(
            {'success': False, 'message': 'Error interno del servidor'}, 
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )