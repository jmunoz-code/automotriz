import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from auditoria.models import Auditoria

count = Auditoria.objects.count()
print(f"Total Auditoria records: {count}")

if count > 0:
    print("Latest 5 records:")
    for a in Auditoria.objects.all().order_by('-fecha_hora')[:5]:
        print(f"{a.fecha_hora} - {a.usuario} - {a.accion} - {a.modulo_tabla}")
