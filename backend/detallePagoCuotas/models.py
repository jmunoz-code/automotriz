# models.py (Solo el modelo de DetallePagoCuotas)
from django.db import models


class DetallePagoCuotas(models.Model):
    id = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, null=True)
    patente = models.CharField(max_length=10, null=True)
    numero_cuota = models.IntegerField(null=True)
    monto_cuota = models.IntegerField(null=True) # Monto del abono
    interes = models.FloatField(null=True)
    capital = models.IntegerField(null=True)
    fecha_abono = models.DateField(auto_now_add=True)
    numero_contrato = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = 'detalle_pago' # Nombre real de tu tabla en la base de datos
        verbose_name = "detalle_pago"
        verbose_name_plural = "detalle_pago"