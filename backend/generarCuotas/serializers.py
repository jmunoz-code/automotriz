from rest_framework import serializers
from .models import GenerarCuotas

# Importamos el modelo correcto que usamos para guardar las cuotas.
# Basado en tu archivo models.py, asumimos que el modelo es GenerarCuotas.


# 🟢 CORREGIDO: Renombrar la clase para consistencia
class GenerarCuotasSerializer(serializers.ModelSerializer):
    """
    Serializador usado para transformar el modelo GenerarCuotas (Cuotas Generadas)
    en una respuesta JSON para la API. 
    Se han eliminado los SerializerMethodField() que dependían de los modelos
    'Presupuesto' y 'Clientes' ya que la lógica principal de generación de cuotas
    ya no los necesita para la entrada de datos.
    """
    
    class Meta:
        # 🟢 Usamos el modelo GenerarCuotas para el output
        model = GenerarCuotas
        # Incluimos todos los campos del modelo que ya guardamos en la BDD
        fields = '__all__'
