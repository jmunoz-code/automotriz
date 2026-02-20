import threading

thread_local = threading.local()

def get_current_user():
    user = getattr(thread_local, 'user', None)
    return user if user else 'Anónimo'

class UsuarioSesionMiddleware:
    """
    Middleware para capturar el usuario de sesión y página de origen desde headers HTTP.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capturar el usuario desde el header personalizado
        usuario_sesion = request.META.get('HTTP_X_USUARIO_SESION', None)
        
        # Almacenar en el request
        request.usuario_sesion = usuario_sesion if usuario_sesion else None
        
        # Almacenar en thread_local para acceso desde señales
        thread_local.user = usuario_sesion
        
        try:
            response = self.get_response(request)
        finally:
            # Limpiar thread_local para evitar fugas de información
            thread_local.user = None
            
        return response
