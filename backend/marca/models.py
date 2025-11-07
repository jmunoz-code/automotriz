# marca/models.py
from django.db import models

class Marca(models.Model):
    tipo_marca = models.IntegerField(null=False)
    descripcion = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.descripcion

    class Meta:
        db_table = 'marca'
        verbose_name = 'marca'
        verbose_name_plural = 'Marcas'