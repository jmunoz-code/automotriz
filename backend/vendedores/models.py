from django.db import models

# Create your models here.
class Vendedores(models.Model):
    # solo le agrega el id
    
    rut = models.CharField(max_length=10, null=False, unique=True)
    nombres = models.CharField(max_length=50, null=False)
    apellidos = models.CharField(max_length=50, null=False)
    usuario = models.CharField(max_length=15, null=True, unique=True)
    clave = models.CharField(max_length=120, null= True)
    comision = models.FloatField(null=True)
    nivel = models.CharField(max_length=15, null=True)
    activo = models.IntegerField(default=0, null=True)

    #clase helper
    # cuando llamo modelo campo muetsre por defecto
    def __str__(self):
        return self.nombres
    
    # indica nombre que tiene lka tabla en el admin de django
    class Meta:
        db_table='vendedores'
        verbose_name = 'Vendedores'
        verbose_name_plural = 'Vendedores'
