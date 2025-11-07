
from django.db import models


# Create your models here.
class Presupuesto(models.Model):
    # solo le agrega el id
    rut_cliente = models.CharField(max_length=15, null=False)
    rut_vendedor = models.CharField(max_length=15, null=True)
    nombre_cliente = models.CharField(max_length=50)
    patente_vehiculo = models.CharField(max_length=15, null=False)
    tipo_pago = models.CharField(max_length=50, null=False)
    valor_pie = models.IntegerField(null=False)
    numero_cuotas = models.IntegerField(null=False)
    monto_a_financiar = models.IntegerField(null=False)
    valor_cuota = models.IntegerField(null=False)
    interes_mensual = models.FloatField(null=False)
    fecha_creacion = models.DateField(null=True)
    fecha_inicio_pago = models.DateField(null=True)
    precio_venta = models.IntegerField(null=True)
    estado = models.IntegerField(default=0)

 
    #clase helper
    # cuando llamo modelo campo muetsre por defecto
    def __str__(self):
      return f"{self.nombre_cliente} - {self.patente_vehiculo}"
    
    # indica nombre que tiene lka tabla en el admin de django
    class Meta:
        db_table='presupuesto'
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuesto'
