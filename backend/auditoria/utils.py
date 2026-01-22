from .models import Auditoria
import traceback

def registrar_auditoria(usuario, pagina, accion, modulo_tabla, descripcion, valor_anterior=None, valor_nuevo=None, ip_usuario=None):
    """
    Función helper para registrar eventos de auditoría desde cualquier parte del sistema.
    
    Uso:
    from auditoria.utils import registrar_auditoria
    
    registrar_auditoria(
        usuario=request.user.username,
        pagina='NombreVista',
        accion='MODIFICAR',
        modulo_tabla='Contratos',
        descripcion='Se modificó el contrato X',
        ...
    )
    """
    try:
        Auditoria.objects.create(
            usuario=str(usuario), # Asegurar string
            pagina=pagina,
            accion=accion,
            modulo_tabla=modulo_tabla,
            descripcion=descripcion,
            valor_anterior=str(valor_anterior) if valor_anterior is not None else None,
            valor_nuevo=str(valor_nuevo) if valor_nuevo is not None else None,
            ip_usuario=ip_usuario
        )
    except Exception as e:
        # Fallo silencioso para no romper el flujo principal si falla la auditoría
        print(f"Error al registrar auditoría: {str(e)}")
        traceback.print_exc()
