from django.db import models



class creditos(models.Model):
    rut_cliente = models.CharField(max_length=12, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    patente = models.CharField(max_length=10, unique=True)
    # ... otros campos del crédito
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.patente}"
