import os
import django
import sys

# Configurar entorno Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automotriz.settings')
django.setup()

from pagoCuotas.models import PagoCuotas
from generarCuotas.models import GenerarCuotas
from presupuesto.models import Presupuesto

patente_buscada = 'GVTL29'

print(f"\n--- REPORTE PARA PATENTE: {patente_buscada} ---")

# 1. Verificar si existe el Contrato (Presupuesto)
contrato = Presupuesto.objects.filter(patente_vehiculo=patente_buscada).first()
if contrato:
    print(f"✅ Contrato ENCONTRADO:")
    print(f"   - Cliente: {contrato.nombre_cliente} (RUT: {contrato.rut_cliente})")
    print(f"   - Fecha Creación: {contrato.fecha_creacion}")
    print(f"   - Tipo Pago ID: {contrato.tipo_pago}")
    print(f"   - Estado: {contrato.estado}")
else:
    print(f"❌ Contrato NO encontrado en tabla 'presupuesto'.")

print("-" * 30)

# 2. Verificar en la tabla CORRECTA (pago_cuotas)
cuotas_reales = PagoCuotas.objects.filter(patente=patente_buscada)
count_reales = cuotas_reales.count()

if count_reales > 0:
    print(f"✅ Se encontraron {count_reales} cuotas en la tabla CORRECTA ('pago_cuotas').")
    for c in cuotas_reales:
        print(f"   - Cuota {c.numero_cuota}: Vence {c.fecha_vencimiento}, Monto {c.monto_cuota}")
else:
    print(f"⚠️ NO se encontraron cuotas en la tabla 'pago_cuotas'.")

print("-" * 30)

# 3. Verificar en la tabla INCORRECTA (generar_cuotas - antigua)
# Nota: Puede que el modelo GenerarCuotas ya no apunte a la tabla si lo borramos, 
# pero intentaremos consultarlo por si quedaron registros viejos.
try:
    cuotas_viejas = GenerarCuotas.objects.filter(patente=patente_buscada)
    count_viejas = cuotas_viejas.count()
    
    if count_viejas > 0:
        print(f"☢️  ¡ATENCIÓN! Se encontraron {count_viejas} cuotas en la tabla ANTIGUA/INCORRECTA ('generar_cuotas_generarcuotas').")
        print("   Esto significa que se crearon antes del arreglo.")
    else:
        print(f"✅ No hay registros perdidos en la tabla antigua.")
except Exception as e:
    print(f"No se pudo consultar la tabla antigua: {e}")

print("\n-------------------------------------------")
