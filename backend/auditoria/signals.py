from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import Auditoria
from .utils import registrar_auditoria
from backend.middleware import get_current_user
import json
import threading

# Use thread local storage to hold old state
thread_local = threading.local()

def get_model_name(instance):
    return instance._meta.verbose_name.title()

def serialize_instance(instance):
    try:
        data = model_to_dict(instance)
        # Convert to simple types
        return {k: str(v) if v is not None else None for k, v in data.items()}
    except:
        return {"error": "No serializable"}

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if sender._meta.app_label in ['auditoria', 'admin', 'sessions', 'contenttypes']:
        return

    try:
        if instance.pk:
            current_instance = sender.objects.get(pk=instance.pk)
            # Store old state in thread local, keyed by instance ID
            if not hasattr(thread_local, 'audit_old_state'):
                thread_local.audit_old_state = {}
            thread_local.audit_old_state[instance.pk] = serialize_instance(current_instance)
    except Exception:
        pass

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if sender._meta.app_label in ['auditoria', 'admin', 'sessions', 'contenttypes']:
        return

    try:
        usuario = get_current_user()
        tabla = get_model_name(instance)
        
        try:
            instance_str = str(instance)
        except Exception:
            instance_str = f"<{tabla} ID: {instance.pk}>"

        if created:
            accion = 'CREAR'
            descripcion = f"Creación de {tabla}: {instance_str}"
            valor_nuevo = json.dumps(serialize_instance(instance), default=str)
            valor_anterior = None
            
            registrar_auditoria(
                usuario=usuario,
                accion=accion,
                modulo_tabla=tabla,
                descripcion=descripcion,
                valor_anterior=valor_anterior,
                valor_nuevo=valor_nuevo
            )
        else:
            accion = 'MODIFICAR'
            
            # Retrieve old state
            old_data = {}
            if hasattr(thread_local, 'audit_old_state') and instance.pk in thread_local.audit_old_state:
                old_data = thread_local.audit_old_state.pop(instance.pk)
            
            new_data = serialize_instance(instance)
            
            # Calculate changes
            changes_old = {}
            changes_new = {}
            
            for field, new_value in new_data.items():
                old_value = old_data.get(field)
                # Compare as strings to avoid type issues
                if str(old_value) != str(new_value):
                    changes_old[field] = old_value
                    changes_new[field] = new_value
            
            if changes_old: # Only log if there are actual changes
                descripcion = f"Modificación de {tabla}: {instance_str}"
                
                registrar_auditoria(
                    usuario=usuario,
                    accion=accion,
                    modulo_tabla=tabla,
                    descripcion=descripcion,
                    valor_anterior=json.dumps(changes_old, default=str),
                    valor_nuevo=json.dumps(changes_new, default=str)
                )

    except Exception as e:
        print(f"Error crítico en auditoría (ignorado): {e}")

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if sender._meta.app_label in ['auditoria', 'admin', 'sessions', 'contenttypes']:
        return

    try:
        usuario = get_current_user()
        tabla = get_model_name(instance)
        
        try:
            instance_str = str(instance)
        except Exception:
            instance_str = f"<{tabla} ID: {instance.pk}>"
        
        accion = 'ELIMINAR'
        descripcion = f"Eliminación de {tabla}: {instance_str}"
        valor_anterior = json.dumps(serialize_instance(instance), default=str)
        valor_nuevo = None

        registrar_auditoria(
            usuario=usuario,
            accion=accion,
            modulo_tabla=tabla,
            descripcion=descripcion,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo
        )
    except Exception as e:
        print(f"Error crítico en auditoría (ignorado): {e}")
