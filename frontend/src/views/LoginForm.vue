<template>
  <div id="login-screen" class="login-container">

    <div>
      <img src="/img/core-img/logo.png" alt="logo" style="width:420px; max-width: 90%; height:auto;" />
    </div>
    <br>

    <h2>Iniciar Sesión</h2>
    <form @submit.prevent="handleLogin" class="login-form">
      <div class="form-group">
        <label for="username">Usuario:</label>
        <input type="text" id="username" v-model="username" required placeholder="Ingresa tu usuario" />
      </div>
      <div class="form-group">
        <label for="password">Contraseña:</label>
        <input type="password" id="password" v-model="password" required placeholder="Ingresa tu contraseña" />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Cargando...' : 'Ingresar' }}
      </button>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
    </form>
  </div>
</template>

<script>
export default {
  name: 'LoginScreen',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null,
      successMessage: null,
    };
  },
  methods: {
    // FUNCIÓN PARA OBTENER EL VALOR DE UNA COOKIE
    getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    },

    // FUNCIÓN PRINCIPAL DE LOGIN MODIFICADA
    async handleLogin() {
      this.loading = true;
      this.error = null;
      this.successMessage = null;

      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}login/`;
        console.log('url', apiUrl);

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            usuario: this.username,
            clave: this.password,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Credenciales inválidas o error en el servidor.');
        }

        const responseData = await response.json();
        this.successMessage = '¡Ingreso exitoso! Redirigiendo...';
        console.log('Login exitoso:', responseData);

        if (responseData.data && responseData.data.nivel) {
          localStorage.setItem('user_nivel', responseData.data.nivel);
          localStorage.setItem('user_usuario', responseData.data.usuario);
          localStorage.setItem('user_id', responseData.data.id);
        }

        // Redirigir siempre a Presupuesto
        this.$router.push('/presupuesto');

      } catch (err) {
        console.error('Error durante el login:', err);
        this.error = err.message || 'Ocurrió un error inesperado al intentar iniciar sesión.';
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
/* Estilos básicos para que se vea decente */
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  background-color: white;
  font-family: Arial, sans-serif;
  padding: 20px;
  /* Add padding for small screens */
}

.login-form {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  box-sizing: border-box;
}

h2 {
  color: #555;
  margin-bottom: 30px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: bold;
}

input[type='text'],
input[type='password'] {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
  /* Incluir padding y borde en el ancho total */
}

input[type='text']:focus,
input[type='password']:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
}

button {
  width: 100%;
  padding: 12px;
  background-color: #379648;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 18px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover:not(:disabled) {
  background-color: #1e3723;
}

button:disabled {
  background-color: #a0cbf7;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
}

.success-message {
  color: #28a745;
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
}

/* Media Query for Mobile Devices */
@media (max-width: 480px) {
  .login-form {
    padding: 20px;
    box-shadow: none;
    /* Simplify on very small screens if desired, or keep it */
    border: 1px solid #eee;
    /* Optional border instead of shadow */
  }

  .login-container {
    padding: 10px;
  }
}
</style>