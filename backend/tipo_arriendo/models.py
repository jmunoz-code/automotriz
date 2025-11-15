from django.db import models

class TipoArriendo(models.Model):
    """
    Modelo para almacenar los diferentes tipos de arriendo (ej: Privado, Airbnb, Booking).
    """
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre del tipo de arriendo")

    # --- NUEVO CAMPO ---
    # max_digits = 3 (ej. 12.3 -> 3 dígitos en total)
    # decimal_places = 1 (1 dígito después del punto)
    comision = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=0.0, 
        help_text="Comisión en porcentaje (ej. 10.5)"
    )
    # --- FIN NUEVO CAMPO ---

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Arriendo"
        verbose_name_plural = "Tipos de Arriendo"
        ordering = ['nombre'] # Es buena idea ordenar por nombre