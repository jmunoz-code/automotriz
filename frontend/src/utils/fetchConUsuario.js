/**
 * Wrapper de fetch que automáticamente agrega el header X-Usuario-Sesion
 * con el usuario almacenado en localStorage
 */
export async function fetchConUsuario(url, options = {}) {
    // Obtener el usuario del localStorage
    const usuario = localStorage.getItem('user_usuario');

    // Crear headers si no existen
    const headers = new Headers(options.headers || {});

    // Agregar el header personalizado si hay un usuario
    if (usuario) {
        headers.set('X-Usuario-Sesion', usuario);
    }

    // Combinar opciones
    const fetchOptions = {
        ...options,
        headers: headers
    };

    // Ejecutar fetch normal
    return fetch(url, fetchOptions);
}

// También exportar como default para import default
export default fetchConUsuario;
