
from django.db import models


# Create your models here.
class Contratos(models.Model):
    # solo le agrega el id
    
    rut = models.CharField(max_length=10, null=False )
    patente = models.CharField(max_length=15, null=False)
    pie = models.IntegerField(null=False)
    observacion = models.CharField(max_length=200, null=True, blank=True)
    numero_cuotas = models.IntegerField(null=False)
    fecha = models.DateField(null=False)
    
    

    #clase helper
    # cuando llamo modelo campo muetsre por defecto
    def __str__(self):
        return self.patente
    
    # indica nombre que tiene lka tabla en el admin de django
    class Meta:
        db_table='Contratos'
        verbose_name = 'Contratos'
        verbose_name_plural = 'Contratos'
