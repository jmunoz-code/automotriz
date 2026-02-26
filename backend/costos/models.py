# Create your models here.
from django.db import models

# Create your models here.
class Costos(models.Model):
    # solo le agrega el id
    patente = models.CharField(max_length=10, null=False)
    fecha = models.DateField(null=True, blank=True)
    numero_boleta = models.CharField(max_length=50, null=True, blank=True)
    tipo_costo = models.CharField(max_length=30, null=False)
    descripcion = models.CharField(max_length=100, null=False)
    valor = models.IntegerField(null=False)

    #clase helper
    # cuando llamo modelo campo muetsre por defecto
    def __str__(self):
        return self.patente
    
    # indica nombre que tiene lka tabla en el admin de django
    class Meta:
        db_table='costos'
        verbose_name = 'Costos'
        verbose_name_plural = 'Costos'
