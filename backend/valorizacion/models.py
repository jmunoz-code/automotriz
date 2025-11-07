# Create your models here.
from django.db import models

# Create your models here.
class Valorizacion(models.Model):
    # solo le agrega el id
    
    patente = models.CharField(max_length=50, null=False)
    precio_compra = models.IntegerField(null=False)
    costo_asociado = models.IntegerField(null=False)
    margen = models.IntegerField(null=False)
    interes = models.IntegerField(null=False)
    

    #clase helper
    # cuando llamo modelo campo muetsre por defecto
    def __str__(self):
        return self.patente
    
    # indica nombre que tiene lka tabla en el admin de django
    class Meta:
         db_table='valorizacion'
         verbose_name = 'valorizacion'
         verbose_name_plural = 'valorizacion'

