
from django.db import models



# Create your models here.
class Clientes(models.Model):
    # solo le agrega el id
    
    rut = models.CharField(max_length=10, null=False, unique=True)
    nombres = models.CharField(max_length=50, null=False)
    apellidos = models.CharField(max_length=50, null=False)
    fono = models.CharField(max_length=50, null=False)
    correo = models.CharField(max_length=50, null=False)
    direccion = models.CharField(max_length=100, null=False)    
    ciudad = models.CharField(max_length=100, null=True)
    observacion = models.CharField(max_length=200, null=True, blank=True)
    habilitado  = models.BooleanField(default=False)

    #clase helper
    # cuando llamo modelo campo muetsre por defecto
    def __str__(self):
        return self.nombres
    
    # indica nombre que tiene lka tabla en el admin de django
    class Meta:
        db_table='clientes'
        verbose_name = 'Clientes'
        verbose_name_plural = 'Clientes'
