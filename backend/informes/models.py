from django.db import models

# Create your models here.
class Orden(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    # ... otros campos