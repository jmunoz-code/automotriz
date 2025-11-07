from django.db import models

class GenerarCuotas(models.Model):
    """
    Modelo para registrar las cuotas de un préstamo o crédito.
    """
    # Identificadores de la transacción (llaves foráneas conceptuales)
    rut_cliente = models.CharField(max_length=12, help_text="RUT del cliente asociado a la cuota.")
    patente = models.CharField(max_length=10, help_text="Patente del vehículo asociado al préstamo.")
    
    # Detalle de la cuota
    numero_cuota = models.IntegerField(help_text="Número de la cuota dentro del total (1, 2, 3...).")
    fecha_vencimiento = models.DateField(help_text="Fecha límite de pago de la cuota.")
    
    # Valores monetarios
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto total a pagar en esta cuota.")
    abono_capital = models.DecimalField(max_digits=10, decimal_places=2, help_text="Porción del pago que amortiza el capital principal.")
    
    # Estado de pago
    fecha_pago = models.DateField(null=True, blank=True, help_text="Fecha en que se efectuó el pago.")
    observacion = models.TextField(null=True, blank=True, help_text="Cualquier nota adicional sobre el pago.")
    
    # Campos de auditoría (opcional, pero buena práctica)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Generar Cuotas"
        verbose_name_plural = "generar cuotas"
        # Asegura que no haya dos cuotas con el mismo número para el mismo préstamo/patente.
        unique_together = ('patente', 'numero_cuota')

    def __str__(self):
        return f"Cuota {self.numero_cuota} - Patente: {self.patente}"