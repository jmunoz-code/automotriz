
import '/public/style.css'
import '@/assets/css/responsive-overrides.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Sobrescribir fetch globalmente para incluir el usuario de sesión en los headers
const originalFetch = window.fetch;
window.fetch = function (url, options) {
    // Obtener el usuario del localStorage
    const usuario = localStorage.getItem('user_usuario');

    // Si no hay usuario, llamar fetch normalmente
    if (!usuario) {
        return originalFetch.call(this, url, options);
    }

    // Crear una copia de las opciones
    const newOptions = options ? { ...options } : {};

    // Crear headers
    const newHeaders = {};

    // Si ya hay headers, copiarlos
    if (newOptions.headers) {
        if (newOptions.headers instanceof Headers) {
            // Convertir Headers a objeto plano
            newOptions.headers.forEach((value, key) => {
                newHeaders[key] = value;
            });
        } else if (typeof newOptions.headers === 'object') {
            // Copiar objeto plano
            Object.assign(newHeaders, newOptions.headers);
        }
    }

    // Agregar el header del usuario
    newHeaders['X-Usuario-Sesion'] = usuario;
    newOptions.headers = newHeaders;

    // Llamar al fetch original
    return originalFetch.call(this, url, newOptions);
};


const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
