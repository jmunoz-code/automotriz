import os
import django
from django.conf import settings
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from auditoria.models import Auditoria

# Create a sample record
Auditoria.objects.create(
    usuario='Sistema',
    pagina='Prueba Inicial',
    accion='CREAR',
    modulo_tabla='Auditoria',
    descripcion='Registro de prueba inicial para verificar visualización',
    fecha_hora=timezone.now(),
    valor_nuevo='{"status": "ok"}'
)

print("Created 1 dummy audit record.")
