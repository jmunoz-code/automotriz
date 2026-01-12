<script>
import Header from '@/components/HeaderAdmin.vue';
import Footer from '@/components/Footer.vue';
import { ref } from 'vue';

export default {
  components: {
    Header,
    Footer,
  },
  data() {
    return {
      numero: 1234567.89, // Este campo parece ser de ejemplo o no relacionado directamente con el CRUD de Vendedores
    };
  },
  methods: {
    formatearMilesConPunto(valor) {
      const formatter = new Intl.NumberFormat('de-DE'); // Usa el locale alemán
      return formatter.format(valor);
    },
  },


  setup() {
    const formData = ref({
      id: '',
      rut: '',
      nombres: '',
      apellidos: '',
      comision: '0',
      usuario: '',          // NUEVO CAMPO
      clave: '',            // NUEVO CAMPO (para la contraseña)
      nivel: 'VENDEDOR', // NUEVO CAMPO, con un valor por defecto
    });

    const mensaje = ref('');
    const tipoMensaje = ref('');

    const nivel = ref(localStorage.getItem('user_nivel'));

    const datos = ref([]); // Aquí almacenarás la lista de vendedores

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

    const handleSubmit = () => {
      // Validaciones para campos existentes
      if (!formData.value.rut.trim()) {
        mostrarMensaje('Por favor, ingrese Rut.', 'error');
        return;
      }

      if (!formData.value.nombres.trim()) {
        mostrarMensaje('Por favor, ingrese Nombres.', 'error');
        return;
      }

      if (!formData.value.apellidos.trim()) {
        mostrarMensaje('Por favor, ingrese Apellidos.', 'error');
        return;
      }

      // --- NUEVAS VALIDACIONES PARA USUARIO, CLAVE Y NIVEL DE ACCESO ---
      if (!formData.value.usuario.trim()) {
        mostrarMensaje('Por favor, ingrese el nombre de Usuario.', 'error');
        return;
      }

      // La clave solo se requiere al crear o si el ID está vacío (asumiendo que es un nuevo registro)
      // Si el ID tiene valor, significa que es una edición y la clave no es obligatoria para cada actualización
      if (!formData.value.id && !formData.value.clave.trim()) {
        mostrarMensaje('Por favor, ingrese la Clave para el nuevo usuario.', 'error');
        return;
      } else if (formData.value.id && !formData.value.clave.trim()) {
        // En caso de edición, si la clave está vacía, no se enviará para no modificarla en el backend.
        // Si el usuario quiere cambiarla, la ingresará.
      }


      if (!formData.value.nivel.trim()) {
        mostrarMensaje('Por favor, seleccione un Nivel de Acceso.', 'error');
        return;
      }
      // --- FIN NUEVAS VALIDACIONES ---

      // Determinar si es una creación o una actualización
      if (formData.value.id) {
        actualizarRegistro();
      } else {
        crearRegistro();
      }
    };

    const obtenerVendedorPorRut = async (rutABuscar) => { // Cambiado 'id' a 'rutABuscar' para claridad
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vendedores/${rutABuscar}/`; // Asumiendo que tu backend usa RUT como lookup_field
        console.log(`Consultando URL: ${apiUrl}`);
        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!respuesta.ok) {
          console.error(`Error al consultar Usuario con rut ${rutABuscar}: ${respuesta.status} - ${respuesta.statusText}`);
          if (respuesta.status === 404) {
            return null; // No se encontró el vendedor
          }
          throw new Error(`Error en la consulta: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        // Asumiendo que tu API devuelve los datos directamente en el cuerpo de la respuesta,
        // no dentro de un objeto 'data' anidado.
        return data.data; // Si tu backend envía { "data": {...} }, cambia a data.data
      } catch (error) {
        console.error('Error al consultar Usuario:', error);
        return null;
      }
    };

    const limpiarFormulario = () => {
      formData.value.id = '';
      formData.value.rut = '';
      formData.value.nombres = '';
      formData.value.apellidos = '';
      formData.value.comision = '';
      formData.value.usuario = '';         // NUEVO
      formData.value.clave = '';           // NUEVO
      formData.value.nivel = 'USUARIO'; // NUEVO, resetear a valor por defecto

      mensaje.value = '';
      tipoMensaje.value = '';
    };

    const cargarDatosVendedorPorRut = async (rutABuscar) => { // Cambiado 'idABuscar' a 'rutABuscar'
      try {
        const vendedorData = await obtenerVendedorPorRut(rutABuscar);
        if (vendedorData) {
          formData.value.id = vendedorData.id;
          formData.value.rut = vendedorData.rut;
          formData.value.nombres = vendedorData.nombres;
          formData.value.apellidos = vendedorData.apellidos;
          formData.value.comision = vendedorData.comision;
          formData.value.usuario = vendedorData.usuario;
          formData.value.clave = '';
          formData.value.nivel = vendedorData.nivel; // NUEVO
          mostrarMensaje('Datos del Usuario cargados para edición.', 'success');
        } else {
          console.warn('No se encontraron datos para Rut:', rutABuscar);
          limpiarFormulario();
          mostrarMensaje('No se encontró un Usuario con ese Rut. Puede crear uno nuevo.', 'info');
        }
      } catch (error) {
        console.error('Error al cargar datos para Rut:', error);
        mostrarMensaje('Error al cargar datos del Usuario.', 'error');
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };


    const crearRegistro = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vendedores/`;
        console.log("URL de creación:", apiUrl);

        // Prepara los datos a enviar, mapeando 'usuario' a 'username' para el backend
        const dataToSend = {
          ...formData.value,

          // nivel: formData.value.nivel_acceso, // Mapea el campo 'usuario' del frontend a 'username' del backend
          // Mapea el campo 'usuario' del frontend a 'username' del backend
          // 'clave' ya está en formData.value, si se va a enviar la contraseña
        };
        // Elimina el campo 'usuario' duplicado si no quieres enviarlo dos veces
        //  delete dataToSend.usuario;
        // Si 'clave' está vacío, no lo envíes para no sobreescribir la contraseña existente
        if (dataToSend.clave === '') {
          delete dataToSend.clave;
        }

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(dataToSend),
        });

        if (response.ok) {
          // const data = await response.json(); // Si necesitas la respuesta del nuevo registro
          mostrarMensaje('Usuario creado exitosamente!', 'success');
          limpiarFormulario(); // Limpiar el formulario después de crear
          cargarListaDeVendedores(); // Recargar la lista después de crear
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al crear Usuario: ${JSON.stringify(errorData) || response.statusText}`, 'error');
          console.error('Error al crear Usuario:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const actualizarRegistro = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vendedores/${formData.value.rut}/`; // Usa el ID para la actualización
        console.log("URL de actualización:", apiUrl);

        // Prepara los datos a enviar
        const dataToSend = {
          ...formData.value,
          usuario: formData.value.usuario, // Mapea el campo 'usuario' del frontend a 'username' del backend
        };
        delete dataToSend.usuario; // Elimina el campo 'usuario' duplicado

        // Si la clave está vacía, significa que no se desea cambiar, así que no la envíes
        if (dataToSend.clave === '') {
          delete dataToSend.clave;
        }

        const response = await fetch(apiUrl, {
          method: 'PUT', // O PATCH, dependiendo de cómo lo configures en Django
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(dataToSend),
        });

        if (response.ok) {
          // const data = await response.json();
          mostrarMensaje('Usuario actualizado exitosamente!', 'success');
          limpiarFormulario();
          cargarListaDeVendedores(); // Recargar la lista después de actualizar
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al actualizar Usuario: ${JSON.stringify(errorData) || response.statusText}`, 'error');
          console.error('Error al actualizar Usuario:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const eliminarRegistroConfirmado = async () => {
      if (!registroAEliminarId.value) {
        console.error('No se ha especificado el ID del registro a eliminar.');
        mostrarMensaje('Error: ID de Usuario no especificado para eliminar.', 'error');
        return;
      }

      try {
        // Asumiendo que tu endpoint DELETE usa el ID (pk) del vendedor, no el RUT
        // Si tu lookup_field en Django es 'rut', entonces sería `/vendedores/${registroAEliminarId.value}/`
        const apiUrl = `${import.meta.env.VITE_API_URL}vendedores/${registroAEliminarId.value}/`;
        console.log('URL de eliminación:', apiUrl);
        const response = await fetch(apiUrl, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          mostrarMensaje('Usuario Eliminado exitosamente!', 'success');
          cargarListaDeVendedores(); // Recargar la lista después de eliminar
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al eliminar Usuario: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al eliminar Usuario:', errorData);
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

    const cargarListaDeVendedores = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vendedores/`; // Endpoint para obtener la lista completa
        const response = await fetch(apiUrl);
        console.log(apiUrl);
        if (response.ok) {
          const data = await response.json();
          // Ajusta esto según la estructura real de tu respuesta de la API
          // Si tu API devuelve la lista directamente: datos.value = data;
          // Si tu API devuelve { "results": [...], "count": N }: datos.value = data.results;
          // Si tu API devuelve { "data": [...] }: datos.value = data.data;
          datos.value = data.data; // Ajustado, asumí que la lista viene directamente.

        } else {
          console.error('Error al cargar la lista de Usuarios:', response.statusText);
          mostrarMensaje('Error al cargar la lista Usuarios.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión al cargar la lista de Usuarios:', error);
        mostrarMensaje('Error de conexión al cargar la lista de Usuarios.', 'error');
      }
    };

    // Cargar la lista de vendedores al montar el componente
    cargarListaDeVendedores();

    return {
      formData,
      handleSubmit,
      obtenerVendedorPorRut,
      cargarDatosVendedorPorRut,
      crearRegistro,
      actualizarRegistro, // Añadido al return
      mensaje,
      tipoMensaje,
      datos,
      limpiarFormulario,
      registroAEliminarId,
      mostrarModalEliminar,
      abrirModalEliminar,
      cerrarModalEliminar,
      eliminarRegistroConfirmado,
      nivel,
    };
  },
};
</script>

<template>
  <Header></Header>

  <div class="container mt-3">
    <div class="card shadow-sm mt-3 mb-3">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Mantención
        De Usuarios
      </div>
      <div class="card-body mt-3">

        <form @submit.prevent="handleSubmit">

          <div class="mb-3 row align-items-center">
            <label for="rut" class="col-md-2 col-form-label negrita">Rut</label>
            <div class="col-md-3">
              <input type="text" class="form-control form-control-sm negrita" id="rut" v-model="formData.rut" />
            </div>
            <div class="col-md-auto ms-4">
              <button type="button" class="btn btn-secondary btn-sm" @click="cargarDatosVendedorPorRut(formData.rut)">
                Buscar
              </button>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <div class="card-title" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);"> Gestión
                de Usuarios</div>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <label for="nombres" class="form-label negrita">Nombres</label>
                <input type="text" :size="5" class="form-control form-control-sm" id="nombres"
                  v-model="formData.nombres" required />
              </div>

              <div class="mb-3">
                <label for="apellidos" class="form-label negrita">Apellidos</label>
                <input type="text" :size="5" class="form-control form-control-sm" id="apellidos"
                  v-model="formData.apellidos" required />
              </div>

              <div class="mb-3">
                <label for="comision" class="form-label negrita"> % Comisión- Si corresponde</label>
                <input type="number" class="form-control form-control-sm" id="comision"
                  v-model.number="formData.comision" step="0.1" required />
              </div>

              <div class="mb-3">
                <label for="usuario" class="form-label negrita">Usuario</label>
                <input type="text" class="form-control form-control-sm" id="usuario" v-model="formData.usuario"
                  required />
              </div>

              <div class="mb-3">
                <label for="clave" class="form-label negrita">Clave</label>

                <input type="password" class="form-control form-control-sm" id="clave" v-model="formData.clave"
                  :required="!formData.id" />
              </div>

              <div class="mb-3">
                <div class="ms-2">
                  <label for="nivel_acceso" class="form-label negrita">Nivel de Acceso </label>
                </div>
                <div class="ms-2">
                  <select class="form-select form-control-sm" id="nivel_acceso" v-model="formData.nivel" required>
                    <option value="ADMIN">Administrador</option>

                    <option value="USUARIO">Usuario</option>
                  </select>
                </div>
              </div>
              <div class="d-flex justify-content-center">
                <div class="col-md-auto ms-2">
                  <button v-if="nivel === 'ADMIN' || !formData.rut" type="submit" class="btn btn-sm btn-secondary">
                    {{ formData.rut ? 'Actualizar' : 'Crear' }} </button>
                </div>

                <div class="col-md-auto ms-2">
                  <button type="button" class="btn btn-sm btn-secondary" @click="limpiarFormulario">
                    Limpiar
                  </button>
                </div>
              </div>
            </div>
          </div>

        </form>

        <div v-if="mensaje" class="mt-3 alert"
          :class="{ 'alert-success': tipoMensaje === 'success', 'alert-danger': tipoMensaje === 'error' }">
          {{ mensaje }}
        </div>

        <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Lista de Usuarios
        </h3>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Rut</th>
              <th>Nombres</th>
              <th>Apellidos</th>
              <th>Comisión</th>
              <th>Usuario</th>
              <th>Nivel</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vendedor in datos" :key="vendedor.id">
              <td>{{ vendedor.rut }}</td>
              <td>{{ vendedor.nombres }}</td>
              <td>{{ vendedor.apellidos }}</td>
              <td>{{ vendedor.comision }}</td>
              <td>{{ vendedor.usuario }}</td>
              <td>{{ vendedor.nivel }}</td>
              <td>
                <button v-if="nivel === 'ADMIN'" @click="abrirModalEliminar(vendedor.rut)"
                  class="btn btn-danger btn-sm">Eliminar</button>
              </td>
            </tr>
            <tr v-if="datos.length === 0">
              <td colspan="7">No hay usuarios registrados.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="mostrarModalEliminar" class="modal fade show" style="display: block;" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirmar Eliminación</h5>
            <button type="button" class="btn-close" @click="cerrarModalEliminar" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            ¿Estás seguro de que deseas eliminar el usuario con ID: {{ registroAEliminarId }}?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary btn-sm" @click="cerrarModalEliminar">Cancelar</button>
            <button type="button" class="btn btn-danger btn-sm" @click="eliminarRegistroConfirmado">Eliminar</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="mostrarModalEliminar" class="modal-backdrop fade show"></div>
  </div>
  <Footer></Footer>
</template>

<style scoped>
/* Puedes agregar estilos personalizados aquí si lo deseas */
.negrita {
  font-weight: bold;
  font-size: small;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-dialog {
  background-color: white;
  border-radius: 5px;
  padding: 20px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.modal-title {
  font-size: 1.2rem;
  font-weight: bold;
}

.modal-body {
  margin-bottom: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
}

.modal-footer button {
  margin-left: 10px;
}
</style>
