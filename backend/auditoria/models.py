from django.db import models
from django.utils import timezone

class Auditoria(models.Model):
    ACCION_CHOICES = [
        ('CREAR', 'Crear'),
        ('MODIFICAR', 'Modificar'),
        ('ELIMINAR', 'Eliminar'),
    ]
    
    fecha_hora = models.DateTimeField(default=timezone.now, db_index=True)
    usuario = models.CharField(max_length=100, db_index=True)
    pagina = models.CharField(max_length=200, help_text='Página desde donde se realizó el cambio')
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES, db_index=True)
    modulo_tabla = models.CharField(max_length=100, db_index=True, help_text='Módulo o tabla afectada')
    descripcion = models.TextField()
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)
    ip_usuario = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        db_table = 'auditoria'
        ordering = ['-fecha_hora']
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
    
    def __str__(self):
        return f"{self.fecha_hora} - {self.usuario} - {self.accion} en {self.modulo_tabla}"
