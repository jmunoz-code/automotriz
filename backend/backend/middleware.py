import threading

thread_local = threading.local()

def get_current_user():
    return getattr(thread_local, 'user', 'Anónimo')

def get_current_page():
    return getattr(thread_local, 'pagina', 'Sistema/Automático')

class UsuarioSesionMiddleware:
    """
    Middleware para capturar el usuario de sesión y página de origen desde headers HTTP.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capturar el usuario desde el header personalizado
        usuario_sesion = request.META.get('HTTP_X_USUARIO_SESION', None)
        
        # Capturar la página origen
        pagina_origen = request.META.get('HTTP_X_PAGINA_ORIGEN', None)
        
        # Almacenar en el request
        request.usuario_sesion = usuario_sesion if usuario_sesion else None
        
        # Almacenar en thread_local para acceso desde señales
        thread_local.user = usuario_sesion
        thread_local.pagina = pagina_origen # Store page
        
        try:
            response = self.get_response(request)
        finally:
            # Limpiar thread_local para evitar fugas de información
            thread_local.user = None
            thread_local.pagina = None
            
        return response
