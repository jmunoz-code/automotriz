from django.db import models

# --- ¡ESTA ES LA LÍNEA CORREGIDA! ---
# Importamos TipoArriendo desde la app 'arriendos' (no desde '.models')
from tipo_arriendo.models import TipoArriendo 

class Reserva(models.Model):
    # Datos del Arrendatario
    rut_arrendatario = models.CharField(max_length=12)
    nombre_arrendatario = models.CharField(max_length=255)

    # Datos de la Reserva
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Este campo 'ForeignKey' ahora funcionará gracias a la importación correcta
    tipo_arriendo = models.ForeignKey(
        TipoArriendo,
        on_delete=models.SET_NULL, # Si se borra un tipo, la reserva no se borra
        null=True,                # Permite que el campo sea nulo en la BD
        related_name='reservas'
    )
    
    valor_arriendo = models.IntegerField() # Usamos IntegerField para CLP

    def __str__(self):
        # Mostramos el nombre del tipo si existe
        tipo_str = self.tipo_arriendo.nombre if self.tipo_arriendo else "Sin tipo"
        return f"Reserva de {self.nombre_arrendatario} ({tipo_str})"