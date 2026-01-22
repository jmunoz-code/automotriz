
import os
import django
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import User

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pagoCuotas.models import PagoCuotas as Cuota
from pagoCuotas.views import PagoCuotasAPIView
from auditoria.models import Auditoria

def probar_auditoria():
    print("--- INICIANDO PRUEBA DE AUDITORÍA ---")
    
    # 1. Obtener una cuota para modificar
    cuota = Cuota.objects.first()
    if not cuota:
        print("No hay cuotas en el sistema. Creando una de prueba...")
        # Crear cuota dummy si no existe
        cuota = Cuota.objects.create(
            rut_cliente='11111111-1', 
            patente='ABCD12', 
            numero_cuota=1,
            monto_cuota=10000,
            fecha_vencimiento='2025-01-01'
        )
    
    print(f"Cuota seleccionada ID: {cuota.id}, Observación actual: '{cuota.observacion}'")
    
    # 2. Preparar el cambio (modificar observación)
    nueva_obs = "Prueba Auditoria Automatica"
    factory = APIRequestFactory()
    data = {'observacion': nueva_obs}
    url = f'/api/pagoCuotas/{cuota.id}/'
    
    request = factory.patch(url, data, format='json')
    
    # Agregar IP simulada (ya que factory no siempre la pone igual que el server real)
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    
    # Simular usuario admin
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        
    force_authenticate(request, user=user)
    
    # 3. Ejecutar la vista
    print("Enviando petición PATCH para modificar cuota...")
    view = PagoCuotasAPIView.as_view()
    response = view(request, pk=cuota.id)
    
    if response.status_code == 200:
        print(">>> Modificación exitosa en PagoCuotas.")
        
        # 4. Verificar Auditoría
        print("Verificando tabla de Auditoría...")
        ultimo_log = Auditoria.objects.order_by('-id').first()
        
        if ultimo_log:
            print(f"\n[ÉXITO] Registro encontrado:")
            print(f" - ID: {ultimo_log.id}")
            print(f" - Usuario: {ultimo_log.usuario}")
            print(f" - Acción: {ultimo_log.accion}")
            print(f" - Módulo: {ultimo_log.modulo_tabla}")
            print(f" - Descripción: {ultimo_log.descripcion}")
            print(f" - IP: {ultimo_log.ip_usuario}")
            print(f" - Valor Nuevo: {ultimo_log.valor_nuevo}")
        else:
            print("\n[ERROR] No se encontró ningún registro en la tabla Auditoria.")
    else:
        print(f"\n[ERROR] La petición falló con status {response.status_code}")
        print(response.data)

if __name__ == '__main__':
    probar_auditoria()
