import os
import django
import sys
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from pagoCuotas.models import PagoCuota

# Buscar la cuota 1
cuota1 = PagoCuota.objects.filter(
    rut_cliente='14151043-6',
    patente='PYLV84',
    numero_cuota=1
).first()

if not cuota1:
    print("Error: No se encontró la cuota 1 para duplicar")
    sys.exit(1)

# Verificar si ya existe la cuota 2
cuota2_existe = PagoCuota.objects.filter(
    rut_cliente='14151043-6',
    patente='PYLV84',
    numero_cuota=2
).exists()

if cuota2_existe:
    print("La cuota 2 ya existe. No se creará duplicado.")
    sys.exit(0)

# Crear cuota 2 duplicando cuota 1
cuota2 = PagoCuota()
cuota2.rut_cliente = cuota1.rut_cliente
cuota2.nombres = cuota1.nombres
cuota2.apellidos = cuota1.apellidos
cuota2.patente = cuota1.patente
cuota2.numero_cuota = 2
cuota2.fecha_vencimiento = datetime(2025, 11, 8).date()  # 08-11-2025
cuota2.monto_a_financiar = cuota1.monto_a_financiar
cuota2.interes_mensual = cuota1.interes_mensual
cuota2.monto_cuota = cuota1.monto_cuota
cuota2.interes_mora = 0
cuota2.abono_total = 0
cuota2.observacion = ''
cuota2.estado = cuota1.estado

cuota2.save()

print(f"✓ Cuota 2 creada exitosamente:")
print(f"  - RUT: {cuota2.rut_cliente}")
print(f"  - Patente: {cuota2.patente}")
print(f"  - Número de Cuota: {cuota2.numero_cuota}")
print(f"  - Fecha Vencimiento: {cuota2.fecha_vencimiento}")
print(f"  - Monto Cuota: {cuota2.monto_cuota}")
print(f"  - Abono Total: {cuota2.abono_total}")
