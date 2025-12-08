from django.db import models
from tipoVehiculo.models import TipoVehiculo


from marca.models import Marca
from presupuesto.models import Presupuesto



from marca.models import Marca


class Vehiculos(models.Model):
    
    tipo_marca =  models.ForeignKey(Marca, models.DO_NOTHING)#,default=1
    tipo_vehiculo =  models.ForeignKey(TipoVehiculo, models.DO_NOTHING)#,default=1
    tipo_combustible = models.IntegerField(null=False)
    tipo_trasmision = models.IntegerField(null=False)
    modelo = models.CharField(max_length=50, null=False)
    agno = models.CharField(max_length=4, null=False)
    numero_motor = models.CharField(max_length=30, null=False)
    numero_chasis = models.CharField(max_length=30, null=False)
    color = models.CharField(max_length=50, null=False)
    patente = models.CharField(max_length=15, null=False,unique=True)
    kilometraje = models.IntegerField(null=False)
    estado = models.IntegerField(null=True)
    precio_compra = models.IntegerField(null=False)
    precio_venta = models.IntegerField(null=True, default=0)
     # NUEVO CAMPO
    propiedad_automotriz = models.IntegerField(null=True)
    revision_tecnica_al_dia = models.IntegerField(null=True, default=0)
    permiso_circulacion = models.IntegerField(null=True, default=0)
    seguro_vigente = models.IntegerField(null=True, default=0)


      #clase helper
    # cuando llamo modelo campo muetsre por defecto
    def __str__(self):
              return f"{self.marca} {self.modelo} ({self.patente})"

    class Meta:
        db_table = 'vehiculos'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'