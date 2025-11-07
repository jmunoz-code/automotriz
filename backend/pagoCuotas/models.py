# models.py
from django.db import models

class PagoCuotas(models.Model):
    rut_cliente = models.CharField(max_length=15, null=True)
    patente = models.CharField(max_length=15, null=True)
    monto_prestamo = models.IntegerField(null=True)
    interes_mensual = models.FloatField(null=True)
    numero_cuota = models.IntegerField(null=True)
    abono_capital = models.IntegerField(null=True)
    monto_cuota = models.IntegerField(null=True) 
    fecha_vencimiento = models.DateField(null=True)
    fecha_pago = models.DateField(null=True)
    observacion = models.CharField(max_length=50, null=True)
    # --- Nuevo campo para el saldo pendiente ---
    
    def __str__(self):
        return f"Cuota {self.numero_cuota} - Cliente: {self.rut_cliente}, Patente: {self.patente}, Vence: {self.fecha_vencimiento}"

    class Meta:
        db_table = 'pago_cuotas'
        verbose_name = 'pago_cuotas'
        verbose_name_plural = 'Pago_cuotas'
        ordering = ['numero_cuota', 'rut_cliente', 'patente']