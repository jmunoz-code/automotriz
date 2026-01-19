<script>
import Header from '@/components/HeaderAdmin.vue';
import Footer from '@/components/Footer.vue';
import { ref, computed, onMounted } from 'vue';

export default {
  components: {
    Header,
    Footer,
  },
  setup() {
    const formData = ref({
      rut: '',
      nombres: '',
      apellidos: '',
      fono: '',
      correo: '',
      direccion: '',
      ciudad: '',
      observacion: '',
      habilitado: false, // Inicializado como booleano para el checkbox
    });

    const nivel = ref(localStorage.getItem('user_nivel'));


    const inputText = ref('');
    const mensaje = ref('');
    const tipoMensaje = ref('');
    const datos = ref([]);
    const rutValido = ref(true);
    const correoValido = ref(true);

    const uppercaseText = computed(() => {
      return inputText.value.toUpperCase();
    });

    const registroAEliminarId = ref(null);
    const mostrarModalEliminar = ref(false);

    const abrirModalEliminar = (id) => {
      registroAEliminarId.value = id;
      mostrarModalEliminar.value = true;
    };

    const cerrarModalEliminar = () => {
      registroAEliminarId.value = null;
      mostrarModalEliminar.value = false;
    };

    const validarRut = (rut) => {
      if (!rut || typeof rut !== 'string') {
        return false;
      }
      const rutLimpio = rut.replace(/\./g, '').replace('-', '').toUpperCase();
      if (rutLimpio.length < 2) {
        return false;
      }
      const cuerpo = rutLimpio.slice(0, -1);
      const dv = rutLimpio.slice(-1);
      if (!/^[0-9]+$/.test(cuerpo)) {
        return false;
      }
      let suma = 0;
      let factor = 2;
      for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += parseInt(cuerpo[i]) * factor;
        factor = factor === 7 ? 2 : factor + 1;
      }
      const dvCalculado = 11 - (suma % 11);
      const dvEsperado = dvCalculado === 10 ? 'K' : dvCalculado === 11 ? '0' : String(dvCalculado);
      return dv === dvEsperado;
    };

    const handleRutInput = () => {
      rutValido.value = validarRut(formData.value.rut);
      if (!rutValido.value && formData.value.rut) {
        mostrarMensaje('El RUT ingresado no es válido.', 'error');
      } else if (rutValido.value && formData.value.rut && mensaje.value === 'El RUT ingresado no es válido.') {
        limpiarMensaje();
      }
    };

    const validarEmail = (email) => {
      if (!email) {
        return true;
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    };

    const handleCorreoInput = () => {
      correoValido.value = validarEmail(formData.value.correo);
      if (!correoValido.value && formData.value.correo) {
        mostrarMensaje('El correo electrónico ingresado no es válido.', 'error');
      } else if (correoValido.value && formData.value.correo && mensaje.value === 'El correo electrónico ingresado no es válido.') {
        limpiarMensaje();
      }
    };

    const handleSubmit = () => {
      if (!validarRut(formData.value.rut)) {
        mostrarMensaje('Por favor, ingrese un RUT válido.', 'error');
        return;
      }
      if (!formData.value.nombres.trim()) {
        mostrarMensaje('Por favor, ingrese su nombre.', 'error');
        return;
      }
      if (!validarEmail(formData.value.correo) && formData.value.correo) {
        mostrarMensaje('Por favor, ingrese un correo electrónico válido.', 'error');
        return;
      }

      // Llama a la función para crear el registro si la validación pasa
      crearRegistro();
    };

    const obtenerClientePorRut = async (rut) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}clientes/${rut}/`;
        console.log(apiUrl);

        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!respuesta.ok) {
          console.error(`Error al consultar cliente con RUT ${rut}: ${respuesta.status} - ${respuesta.statusText}`);
          if (respuesta.status === 404) {
            return null;
          }
          throw new Error(`Error en la consulta: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        return data.data;
      } catch (error) {
        console.error('Error al consultar cliente por RUT:', error);
        return null;
      }
    };

    const limpiarFormulario = () => {
      formData.value.rut = '';
      formData.value.nombres = '';
      formData.value.apellidos = '';
      formData.value.fono = '';
      formData.value.correo = '';
      formData.value.direccion = '';
      formData.value.ciudad = '';
      formData.value.observacion = '';
      formData.value.habilitado = false; // Limpiar el estado de habilitado
      mensaje.value = '';
      tipoMensaje.value = '';
      rutValido.value = true;
      correoValido.value = true;
    };

    const cargarDatosCliente = async (rutABuscar) => {
      try {
        const clienteData = await obtenerClientePorRut(rutABuscar);
        if (clienteData) {
          formData.value.rut = clienteData.rut;
          formData.value.nombres = clienteData.nombres;
          formData.value.apellidos = clienteData.apellidos;
          formData.value.fono = clienteData.fono;
          formData.value.correo = clienteData.correo;
          formData.value.direccion = clienteData.direccion;
          formData.value.ciudad = clienteData.ciudad;
          formData.value.observacion = clienteData.observacion;

          // Asigna el valor de 'habilitado' desde la API
          // Vue.js automáticamente manejará 0/1 para true/false en el checkbox si vienen así
          formData.value.habilitado = clienteData.habilitado;


          console.log('Datos del cliente cargados:', formData.value);
        } else {
          console.warn('No se encontraron datos para el RUT:', rutABuscar);
          limpiarFormulario();
          mostrarMensaje('No se encontró cliente con el RUT ingresado.', 'error');
        }
      } catch (error) {
        console.error('Error al cargar datos del cliente:', error);
        mostrarMensaje('Error al cargar datos del cliente.', 'error');
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const crearRegistro = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}clientes/`;
        console.log(apiUrl);

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData.value),
        });

        if (response.ok) {
          const data = await response.json();
          mostrarMensaje('Cliente creado exitosamente!', 'success');
          formData.value = { rut: '', nombres: '', apellidos: '', fono: '', correo: '', direccion: '', ciudad: '', observacion: '', habilitado: false };
          cargarListaDeClientes();
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al crear cliente: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al crear cliente:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const modificarRegistro = async (clienteRut) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}clientes/${clienteRut}/`; // Construye la URL correcta con el valor del RUT

        console.log(apiUrl);

        const response = await fetch(apiUrl, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData.value),
        });

        if (response.ok) {
          const data = await response.json();
          mostrarMensaje('Cliente modificado exitosamente!', 'success');
          formData.value = { rut: '', nombres: '', apellidos: '', fono: '', correo: '', direccion: '', ciudad: '', observacion: '', habilitado: false };
          cargarListaDeClientes();
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al modificar cliente: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al modificar cliente:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const eliminarRegistro = () => {
      if (formData.value.rut) {
        abrirModalEliminar(formData.value.rut);
      } else {
        mostrarMensaje('Por favor, cargue un cliente para eliminar.', 'error');
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const eliminarRegistroConfirmado = async () => {
      if (!registroAEliminarId.value) {
        console.error('No se ha especificado el ID del registro a eliminar.');
        return;
      }

      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}clientes/${registroAEliminarId.value}/`;
        const response = await fetch(apiUrl, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          mostrarMensaje('Cliente Eliminado exitosamente!', 'success');
          limpiarFormulario();
          cargarListaDeClientes();
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al eliminar Cliente: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al eliminar Cliente:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        cerrarModalEliminar();
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const mostrarMensaje = (texto, tipo) => {
      mensaje.value = texto;
      tipoMensaje.value = tipo;
    };

    const limpiarMensaje = () => {
      mensaje.value = '';
      tipoMensaje.value = '';
    };

    const cargarListaDeClientes = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}clientes/`;
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          datos.value = data.data;
        } else {
          console.error('Error al cargar la lista de Clientes:', response.statusText);
          mostrarMensaje('Error al cargar la lista de Clientes.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión al cargar la lista de Clientes:', error);
        mostrarMensaje('Error de conexión al cargar la lista de Clientes.', 'error');
      }
    };

    onMounted(() => {
      cargarListaDeClientes();
    });

    return {
      formData,
      handleSubmit,
      obtenerClientePorRut,
      cargarDatosCliente,
      crearRegistro,
      modificarRegistro,
      eliminarRegistro,
      eliminarRegistroConfirmado,
      mensaje,
      tipoMensaje,
      cargarListaDeClientes,
      datos,
      rutValido,
      handleRutInput,
      correoValido,
      handleCorreoInput,
      limpiarFormulario,
      abrirModalEliminar,
      cerrarModalEliminar,
      registroAEliminarId,
      registroAEliminarId,
      mostrarModalEliminar,
      nivel,
    };
  },
};
</script>

<template>
  <Header></Header>

  <div class="container mt-3">
    <div class="card shadow-sm mt-3 mb-3">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Ingreso
        Clientes</div>
      <div class="card-body mt-3">
        <br />
        <br />
        <form @submit.prevent="handleSubmit">
          <div class="mb-3 row align-items-center">
            <label for="rut" class="col-md-1 col-form-label negrita">Rut</label>
            <div class="col-md-3">
              <input type="text" class="form-control form-control-sm negrita" id="rut" v-model="formData.rut" required
                @input="handleRutInput" :class="{ 'is-invalid': !rutValido && formData.rut }" />
              <div v-if="!rutValido && formData.rut" class="invalid-feedback">
                Por favor, ingrese un RUT válido.
              </div>
            </div>
            <div class="col-md-auto ms-4">
              <button type="button" class="btn btn-secondary btn-sm" @click="cargarDatosCliente(formData.rut)">
                Buscar
              </button>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <div class="card-title" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);"> Gestión
                de Clientes</div>
            </div>
            <div class="card-body left">

              <div class="mb-3">
                <label for="nombres" class="form-label negrita">Nombres</label>
                <input type="text" class="form-control form-control-sm" id="nombres" v-model="formData.nombres"
                  required />
              </div>
              <div class="mb-3">
                <label for="apellidos" class="form-label negrita">Apellidos</label>
                <input type="text" class="form-control form-control-sm" id="apellidos" v-model="formData.apellidos"
                  required />
              </div>
              <div class="mb-3">
                <label for="fono" class="form-label negrita">Teléfono</label>
                <input type="text" class="form-control form-control-sm" id="fono" v-model="formData.fono" required />
              </div>
              <div class="mb-3">
                <label for="correo" class="form-label negrita">Correo Electrónico</label>
                <input type="email" class="form-control form-control-sm" id="correo" v-model="formData.correo" required
                  @input="handleCorreoInput" :class="{ 'is-invalid': !correoValido && formData.correo }" />
                <div v-if="!correoValido && formData.correo" class="invalid-feedback">
                  Por favor, ingrese un correo electrónico válido.
                </div>
              </div>
              <div class="mb-3">
                <label for="direccion" class="form-label negrita">Dirección</label>
                <input type="text" class="form-control form-control-sm" id="direccion" v-model="formData.direccion"
                  required />
              </div>

              <div class="mb-3">
                <label for="ciudad" class="form-label negrita">Ciudad</label>
                <input type="text" class="form-control form-control-sm" id="ciudad" v-model="formData.ciudad"
                  required />
              </div>

              <div class="mb-3 negrita">
                <div>
                  <label for="observacion" class="form-label negrita">Observaciones</label>
                </div>
                <textarea v-model="formData.observacion" class="form-control form-control-sm" id="observacion"
                  style="width: 800px; box-sizing: border-box;"></textarea>
              </div>

              <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="habilitado" v-model="formData.habilitado">
                <label class="form-check-label negrita" for="habilitado">Habilitado</label>
              </div>
              <br>
              <strong>
                <div :class="{ 'texto-verde': formData.habilitado, 'texto-rojo': !formData.habilitado }">
                  {{ formData.habilitado ? 'Sí esta habilitado para compras!' : 'No esta hablitado para compras!' }}
                </div>
              </strong>
              <br>
              <br>
              <div class="d-flex justify-content-center">
                <div class="col-md-auto ms-2">
                  <button type="submit" class="btn btn-sm btn-secondary">Crear</button>
                </div>
                <div class="col-md-auto ms-2">
                  <button type="button" class="btn btn-sm btn-secondary" @click="modificarRegistro(formData.rut)">
                    Modificar
                  </button>
                </div>
                <div class="col-md-auto ms-2" v-if="nivel === 'ADMIN'">
                  <button type="button" class="btn btn-sm btn-secondary" @click="eliminarRegistro">
                    Eliminar
                  </button>
                </div>
                <div class="col-md-auto ms-2">
                  <button type="button" class="btn btn-sm btn-secondary" @click="limpiarFormulario">
                    Limpiar
                  </button>
                </div>
                <br>
                <br>
              </div>
            </div>
          </div>

        </form>

        <div v-if="mensaje" class="mt-3 alert"
          :class="{ 'alert-success': tipoMensaje === 'success', 'alert-danger': tipoMensaje === 'error' }">
          {{ mensaje }}
        </div>

        <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Lista de
          Clientes
        </h3>
        <table class="table table-striped">
          <thead>
            <tr>

              <th>Rut</th>
              <th>Nombres</th>
              <th>Apellidos</th>
              <th>Teléfono</th>
              <th>Correo Electrónico</th>
              <th>Habilitado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cliente in datos" :key="cliente.id">

              <td>{{ cliente.rut }}</td>
              <td>{{ cliente.nombres }}</td>
              <td>{{ cliente.apellidos }}</td>
              <td>{{ cliente.fono }}</td>
              <td>{{ cliente.correo }}</td>
              <td>{{ cliente.habilitado ? 'Sí' : 'No' }}</td>
              <td>
                <button v-if="nivel === 'ADMIN'" @click="abrirModalEliminar(cliente.rut)"
                  class="btn btn-danger btn-sm">Eliminar</button>
              </td>
            </tr>
            <tr v-if="datos.length === 0">
              <td colspan="7">No hay clientes registrados.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div v-if="mostrarModalEliminar" class="modal fade show d-block" tabindex="-1" role="dialog"
    aria-labelledby="eliminarModalLabel" aria-hidden="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="eliminarModalLabel">Confirmar Eliminación</h5>
          <button type="button" class="btn-close" @click="cerrarModalEliminar" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          ¿Estás seguro de que deseas eliminar este registro (RUT: {{ registroAEliminarId }})?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="cerrarModalEliminar">Cancelar</button>
          <button type="button" class="btn btn-danger" @click="eliminarRegistroConfirmado">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
  <Footer></Footer>
</template>


<style scoped>
/* Puedes agregar estilos personalizados aquí si lo deseas */
.negrita {
  font-weight: bold;
  font-size: small;
}

.left {
  padding-left: 10px;
  padding-right: 10px;
}

/* Estilos para el modal overlay (si no usas una librería de modales) */
.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
  /* Oscurece el fondo */
}

.radio-group label {
  margin-right: 15px;
  cursor: pointer;
}

input[type="radio"] {
  margin-right: 5px;
}

.texto-verde {
  color: blanchedalmond;
  background-color: green;
  text-align: center;
}

.texto-rojo {
  color: blanchedalmond;
  background-color: red;
  text-align: center;
}
</style>