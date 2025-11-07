from django.db import models

# Create your models here.

from django.db import models


# Create your models here.
class detalle(models.Model):
    # solo le agrega el id
    id_compra = models.IntegerField(null=False)
    numero_cuota = models.IntegerField(null=False)
    valor_cuota =  models.IntegerField(null=False)
    estado = models.IntegerField(null=False)
    fecha_vencimiento =  models.DateField()
    fecha_pago = models.DateField()
    observacion = models.CharField(max_length=250, null=True)


    #clase helper
    # cuando llamo modelo campo muetsre por defecto
    def __str__(self):
        return self.observacion
    
    # indica nombre que tiene lka tabla en el admin de django
    class Meta:
        db_table='detalle'
        verbose_name = 'detalle'
        verbose_name_plural = 'detalles'
