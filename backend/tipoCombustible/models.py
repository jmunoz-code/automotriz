from django.db import models

# Create your models here.

from django.db import models


# Create your models here.
class TipoCombustible(models.Model):
    # solo le agrega el id
    tipo_combustible = models.IntegerField(null=False)
    descripcion = models.CharField(max_length=50, null=False)
    


    #clase helper
    # cuando llamo modelo campo muetsre por defecto
    def __str__(self):
        return self.descripcion
    
    # indica nombre que tiene lka tabla en el admin de django
    class Meta:
        db_table='tipocombustible'
        verbose_name = 'tipoCombustible'
        verbose_name_plural = 'tipoCombustible'
