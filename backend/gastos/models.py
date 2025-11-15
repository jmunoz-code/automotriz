from django.db import models

class Gasto(models.Model):
    """
    Modelo para almacenar los gastos mensuales.
    """
    
    # Usamos DateField. Almacenaremos el mes/año como el día 1 del mes.
    # Ej: "Noviembre 2025" se guarda como "2025-11-01"
    fecha = models.DateField()
    
    descripcion = models.CharField(max_length=255)
    
    # Usamos DecimalField para dinero, es más preciso que FloatField.
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Formateamos la fecha para mostrar "Mes Año"
        return f"{self.fecha.strftime('%B %Y')} - {self.descripcion}"

    class Meta:
        # Ordenar por fecha, del más reciente al más antiguo
        ordering = ['-fecha']