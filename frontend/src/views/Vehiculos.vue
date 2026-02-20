<script>
import Header from '@/components/HeaderAdmin.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';


export default {
  components: {
    Header,
    Footer,
    'v-select': vSelect
  },

  setup() {
    const route = useRoute();
    const routeName = route.name || route.path.split('/').filter(s => s).pop() || 'Vehiculos';
    const paginaOrigen = ref(routeName);

    const formData = ref({
      valorTotalFormateado: 0,
      tipo_vehiculo_id: null,
      TipoTransmision: null,
      TipoCombustible: null,
      tipo_marca_id: null,
      total_valor_patente: 0,
      modelo: '',
      agno: '',
      numero_motor: '',
      numero_chasis: '',
      color: '',
      patente: '',
      kilometraje: 0,
      precio_compra: 0,

      precio_venta: 0,
      patenteBuscar: '',
      // NUEVO: Campo para el radio button (Booleano: true = Sí, false = No)
      propiedad_automotriz: false,
      revision_tecnica_al_dia: false,
      permiso_circulacion: false,
      seguro_vigente: false,
      habilitado_venta: false,
    });

    const nivel = ref(localStorage.getItem('user_nivel'));
    const usuario = ref(localStorage.getItem('user_usuario'));

    const opcionestipo_vehiculo_id = ref([]);
    const opcionestipo_marca_id = ref([]);
    const opcionesTipoCombustible = ref([]);
    const opcionesTipoTransmision = ref([]);

    const isLoading = ref(false);
    const mensaje = ref('');
    const tipoMensaje = ref('');
    const datos = ref([]);

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

    const ontipo_vehiculo_idChange = (selectedValue) => {
      console.log('Valor seleccionado (Tipo Vehículo):', selectedValue);
    };

    const onTipoTransmisionChange = (selectedValue) => {
      console.log('Valor seleccionado (Tipo Transmisión):', selectedValue);
    };

    const onTipoCombustibleChange = (selectedValue) => {
      console.log('Valor seleccionado (Tipo Combustible):', selectedValue);
    };

    const ontipo_marca_idChange = (selectedValue) => {
      console.log('Valor seleccionado (Tipo Marca):', selectedValue);
    };

    const cargarOpcionesDesdeApi = async (apiUrl) => {
      isLoading.value = true;
      try {
        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (!respuesta.ok) {
          console.error(`Error al cargar opciones desde ${apiUrl}: ${respuesta.status} - ${respuesta.statusText}`);
          throw new Error(`Error en la consulta: ${respuesta.status}`);
        }
        const data = await respuesta.json();
        if (data && Array.isArray(data.data)) {
          return data.data;
        } else if (Array.isArray(data)) {
          return data;
        } else {
          console.error(`Error: La respuesta de la API desde ${apiUrl} no tiene la estructura esperada.`, data);
          mostrarMensaje('Error al cargar las opciones.', 'error');
          return [];
        }
      } catch (error) {
        console.error(`Error al cargar opciones desde ${apiUrl}:`, error);
        mostrarMensaje('Error al cargar las opciones.', 'error');
        return [];
      } finally {
        isLoading.value = false;
      }
    };

    const obtenerVehiculo = async (id) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vehiculos/${id}/`;

        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!respuesta.ok) {
          console.error(`Error al consultar tipo patente ${id}: ${respuesta.status} - ${respuesta.statusText}`);
          if (respuesta.status === 404) {
            return null;
          }
          throw new Error(`Error en la consulta: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        return data.data;
      } catch (error) {
        console.error('Error al consultar tipo pago:', error);
        return null;
      }
    };


    const obtenerTotalGastosPorPatente = async (patente) => {
      try {

        const apiUrl = `${import.meta.env.VITE_API_URL}costos/${patente}/`;


        console.log('Consultando total gastos:', apiUrl);

        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        // --- CAMBIO CRÍTICO AQUÍ: Leer la respuesta como texto, no como JSON ---
        // El backend devuelve un string directamente, no un objeto JSON.
        const valorTotalFormateado = await respuesta.text();

        console.log('Valor total recibido:', valorTotalFormateado);

        return valorTotalFormateado;

      } catch (error) {
        console.error('Error al obtener el total de gastos por patente:', error);
        return "0"; // Devolver "0" como string, consistente con el backend
      }
    };

    // ... (resto del código de tu setup y return)
    // Función auxiliar para limpiar el formato de miles y convertir a número
    const limpiarFormatoNumerico = (valor) => {
      if (typeof valor === 'string' && valor !== '') {
        const cleaned = valor.replace(/\./g, '').replace(/,/g, '.');
        return parseFloat(cleaned);
      }
      return valor === '' || valor === null || valor === undefined ? 0 : parseFloat(valor);
    };

    const formatearMilesConPunto = (valor) => {
      if (valor === null || valor === undefined || valor === '') {
        return '0';
      }

      const numeroLimpio = limpiarFormatoNumerico(valor);

      if (isNaN(numeroLimpio)) {
        return '0';
      }

      if (numeroLimpio === 0) {
        return '0';
      }

      const formatter = new Intl.NumberFormat('de-DE');
      return formatter.format(numeroLimpio);
    };


    const cargarDatosVehiculo = async (idABuscar) => {
      console.log('Iniciando cargarDatosVehiculo para patente:', idABuscar); // NEW
      if (!idABuscar) {
        mostrarMensaje('Por favor, ingrese una patente para buscar.', 'error');
        limpiarFormulario();
        return;
      }
      try {
        const Data = await obtenerVehiculo(idABuscar);
        console.log('Datos del vehículo obtenidos:', Data); // NEW
        if (Data) {
          formData.value.id = Data.id;
          formData.value.tipo_vehiculo_id = Data.tipo_vehiculo_id;
          formData.value.TipoTransmision = Data.tipo_trasmision;
          formData.value.TipoCombustible = Data.tipo_combustible;
          formData.value.tipo_marca_id = Data.tipo_marca_id;
          formData.value.modelo = Data.modelo;
          formData.value.agno = Data.agno;
          formData.value.numero_motor = Data.numero_motor;
          formData.value.numero_chasis = Data.numero_chasis;
          formData.value.color = Data.color;
          formData.value.patente = Data.patente;

          formData.value.kilometraje = formatearMilesConPunto(Data.kilometraje);
          formData.value.precio_compra = formatearMilesConPunto(Data.precio_compra);
          formData.value.precio_venta = formatearMilesConPunto(Data.precio_venta);

          // NUEVO: Cargar el valor de propiedad_automotriz
          // El backend devuelve un booleano, Vue lo puede manejar directamente
          formData.value.propiedad_automotriz = Data.propiedad_automotriz === 1;
          formData.value.revision_tecnica_al_dia = Data.revision_tecnica_al_dia === 1;
          formData.value.permiso_circulacion = Data.permiso_circulacion === 1;
          formData.value.seguro_vigente = Data.seguro_vigente === 1;
          formData.value.habilitado_venta = Data.habilitado_venta === 1;

          // ¡AQUÍ ESTÁ LA MODIFICACIÓN CLAVE!
          // Cargar el total de gastos y asignarlo a formData.value.valorTotalFormateado

          const totalGastos = await obtenerTotalGastosPorPatente(Data.patente);

          console.log('totalGastos:', totalGastos);

          // Mantén esta línea si también usas total_valor_patente en otro lugar
          formData.value.total_valor_patente = formatearMilesConPunto(totalGastos);

          mostrarMensaje('Datos del vehículo cargados.', 'success');
        } else {
          console.warn('No se encontraron datos para patente:', idABuscar);
          limpiarFormulario();
          mostrarMensaje('No se encontró el vehículo con esa patente.', 'error');
        }
      } catch (error) {
        console.error('Error al cargar datos para Id:', error);
        mostrarMensaje('Error al cargar datos del vehículo.', 'error');
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const cargartipo_vehiculo_id = async () => {
      const url = `${import.meta.env.VITE_API_URL}tipoVehiculo/`;
      opcionestipo_vehiculo_id.value = await cargarOpcionesDesdeApi(url);
    };

    const cargarTipoCombustibles = async () => {
      const url = `${import.meta.env.VITE_API_URL}tipoCombustible/`;
      opcionesTipoCombustible.value = await cargarOpcionesDesdeApi(url);
    };

    const cargarTipoTransmision = async () => {
      const url = `${import.meta.env.VITE_API_URL}trasmision/`;
      opcionesTipoTransmision.value = await cargarOpcionesDesdeApi(url);
    };

    const cargartipo_marca_id = async () => {
      const url = `${import.meta.env.VITE_API_URL}marca/`;
      opcionestipo_marca_id.value = await cargarOpcionesDesdeApi(url);
    };

    const handleSubmit = () => {
      // ... (Tus validaciones existentes) ...

      if (!formData.value.tipo_marca_id) {
        mostrarMensaje('Por favor, seleccione una opción de marca de vehículo.', 'error');
        return;
      }

      if (!formData.value.modelo) {
        mostrarMensaje('Por favor, ingrese el modelo.', 'error');
        return;
      }

      if (!formData.value.tipo_vehiculo_id) {
        mostrarMensaje('Por favor, seleccione una opción de tipo de vehículo.', 'error');
        return;
      }

      if (!formData.value.TipoCombustible) {
        mostrarMensaje('Por favor, seleccione una opción de tipo de combustible.', 'error');
        return;
      }

      if (!formData.value.TipoTransmision) {
        mostrarMensaje('Por favor, seleccione una opción de tipo de transmisión.', 'error');
        return;
      }

      if (!formData.value.agno) {
        mostrarMensaje('Por favor, ingrese el año.', 'error');
        return;
      }

      if (!formData.value.numero_motor) {
        mostrarMensaje('Por favor, ingrese el número de motor.', 'error');
        return;
      }

      if (!formData.value.numero_chasis) {
        mostrarMensaje('Por favor, ingrese el número de chasis.', 'error');
        return;
      }

      if (!formData.value.color) {
        mostrarMensaje('Por favor, ingrese el color.', 'error');
        return;
      }

      if (!formData.value.patente) {
        mostrarMensaje('Por favor, ingrese la patente.', 'error');
        return;
      }

      if (!formData.value.kilometraje && limpiarFormatoNumerico(formData.value.kilometraje) !== 0) {
        mostrarMensaje('Por favor, ingrese kilometraje.', 'error');
        return;
      }

      if (!formData.value.precio_compra && limpiarFormatoNumerico(formData.value.precio_compra) !== 0) {
        mostrarMensaje('Por favor, ingrese el precio de compra.', 'error');
        return;
      }

      // Se omite la validación explícita para el radio button, 
      // ya que siempre tendrá un valor (true/false) en formData.value.propiedad_automotriz.

      crearRegistro();
    };

    const crearRegistro = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vehiculos/`;

        const payload = {
          modelo: formData.value.modelo,
          agno: formData.value.agno,
          numero_motor: formData.value.numero_motor,
          numero_chasis: formData.value.numero_chasis,
          color: formData.value.color,
          patente: formData.value.patente,
          kilometraje: limpiarFormatoNumerico(formData.value.kilometraje),
          tipo_combustible: formData.value.TipoCombustible,
          tipo_vehiculo_id: formData.value.tipo_vehiculo_id,
          tipo_trasmision: formData.value.TipoTransmision,
          tipo_marca_id: formData.value.tipo_marca_id,
          precio_compra: limpiarFormatoNumerico(formData.value.precio_compra),

          precio_venta: limpiarFormatoNumerico(formData.value.precio_venta),
          estado: 0,
          // NUEVO CAMPO: Se envía el valor booleano
          propiedad_automotriz: formData.value.propiedad_automotriz,
          revision_tecnica_al_dia: formData.value.revision_tecnica_al_dia,
          permiso_circulacion: formData.value.permiso_circulacion,
          permiso_circulacion: formData.value.permiso_circulacion,
          seguro_vigente: formData.value.seguro_vigente,
          habilitado_venta: formData.value.habilitado_venta ? 1 : 0


        };
        const nuevoHabilitado = formData.value.propiedad_automotriz;
        if (nuevoHabilitado === false) {
          payload.propiedad_automotriz = 0;
        } else {
          payload.propiedad_automotriz = 1;
        }

        if (formData.value.revision_tecnica_al_dia === false) {
          payload.revision_tecnica_al_dia = 0;
        } else {
          payload.revision_tecnica_al_dia = 1;
        }

        if (formData.value.permiso_circulacion === false) {
          payload.permiso_circulacion = 0;
        } else {
          payload.permiso_circulacion = 1;
        }

        if (formData.value.seguro_vigente === false) {
          payload.seguro_vigente = 0;
        } else {
          payload.seguro_vigente = 1;
        }

        console.log("URL de la API:", apiUrl);
        console.log("Datos a enviar (Payload):", JSON.stringify(payload));

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Usuario-Sesion': usuario.value || 'Anónimo',
            'X-Pagina-Origen': paginaOrigen.value,
          },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          mostrarMensaje('Vehículo creado exitosamente!', 'success');
          limpiarFormulario();
          cargarListaDeVehiculos();

        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al crear Vehículo: ${errorData.mensaje || response.statusText}`, 'error');
          console.error('Error al crear vehículo:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };

    onMounted(() => {
      cargartipo_vehiculo_id();
      cargarTipoCombustibles();
      cargarTipoTransmision();
      cargartipo_marca_id();
      cargarListaDeVehiculos();
    });

    const limpiarFormulario = () => {
      formData.value = {
        tipo_vehiculo_id: null,
        TipoTransmision: null,
        TipoCombustible: null,
        tipo_marca_id: null,
        modelo: '',
        agno: '',
        numero_motor: '',
        numero_chasis: '',
        color: '',
        patente: '',
        kilometraje: 0,
        precio_compra: 0,
        gastos_asociados: 0,
        precio_venta: 0,
        patenteBuscar: '',
        total_gastos_cargados: 0, // Reiniciar también el campo calculado
        // NUEVO: Se reinicia al valor por defecto
        propiedad_automotriz: false,
        revision_tecnica_al_dia: false,
        permiso_circulacion: false,
        permiso_circulacion: false,
        seguro_vigente: false,
        habilitado_venta: false,
      };
      mostrarMensaje('Formulario limpiado.', 'info');
    };

    const modificarRegistro = async (patente) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vehiculos/${patente}/`;

        console.log('URL de PUT:', apiUrl);
        console.log('Contenido de formData.value ANTES de enviar el PUT:', formData.value);

        const payload = {
          ...formData.value,
          kilometraje: limpiarFormatoNumerico(formData.value.kilometraje),
          precio_compra: limpiarFormatoNumerico(formData.value.precio_compra),

          precio_venta: limpiarFormatoNumerico(formData.value.precio_venta),
          // total_gastos_cargados NO se envía porque es un valor calculado, no parte del modelo del vehículo
          // propiedad_automotriz se incluye por el spread (...formData.value)
        };
        const nuevoHabilitado = formData.value.propiedad_automotriz;
        //  payload.propiedad_automotriz = nuevoHabilitado ? 0 : 1;

        if (nuevoHabilitado == false) {
          payload.propiedad_automotriz = 0;
        } else {
          payload.propiedad_automotriz = 1;
        }


        /// payload.propiedad_automotriz = formData.value.propiedad_automotriz;

        if (formData.value.revision_tecnica_al_dia === false) {
          payload.revision_tecnica_al_dia = 0;
        } else {
          payload.revision_tecnica_al_dia = 1;
        }

        if (formData.value.permiso_circulacion === false) {
          payload.permiso_circulacion = 0;
        } else {
          payload.permiso_circulacion = 1;
        }

        if (formData.value.seguro_vigente === false) {
          payload.seguro_vigente = 0;
        } else {
          payload.seguro_vigente = 1;
        }

        if (formData.value.habilitado_venta === false) {
          payload.habilitado_venta = 0;
        } else {
          payload.habilitado_venta = 1;
        }


        const response = await fetch(apiUrl, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-Usuario-Sesion': usuario.value || 'Anónimo',
            'X-Pagina-Origen': paginaOrigen.value,
          },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          mostrarMensaje('Vehículo Modificado exitosamente!', 'success');
          limpiarFormulario();
          cargarListaDeVehiculos();
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al modificar Vehiculo: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al modificar Vehiculo:', errorData);
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
        return;
      }

      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vehiculos/${registroAEliminarId.value}/`;
        console.log('URL de eliminación:', apiUrl);
        const response = await fetch(apiUrl, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'X-Usuario-Sesion': usuario.value || 'Anónimo',
            'X-Pagina-Origen': paginaOrigen.value,
          },
        });

        if (response.ok) {
          mostrarMensaje('Vehículo Eliminado exitosamente!', 'success');
          cargarListaDeVehiculos();
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al eliminar Vehículo: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al eliminar Vehículo:', errorData);
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

    const cargarListaDeVehiculos = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vehiculos/`;
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          datos.value = await Promise.all(data.data.map(async vehiculo => {
            // También cargamos el total de gastos para la lista

            return {
              ...vehiculo,
              kilometraje: formatearMilesConPunto(vehiculo.kilometraje),
              precio_compra: formatearMilesConPunto(vehiculo.precio_compra),
              precio_venta: formatearMilesConPunto(vehiculo.precio_venta),
              // NUEVO: Agregamos el campo para mostrarlo en la tabla si es necesario
              propiedad_automotriz: vehiculo.propiedad_automotriz,
              revision_tecnica_al_dia: vehiculo.revision_tecnica_al_dia,
              permiso_circulacion: vehiculo.permiso_circulacion,
              permiso_circulacion: vehiculo.permiso_circulacion,
              seguro_vigente: vehiculo.seguro_vigente,
              habilitado_venta: vehiculo.habilitado_venta,

            };
          }));
        } else {
          console.error('Error al cargar la lista de vehiculo:', response.statusText);
          mostrarMensaje('Error al cargar la lista de vehiculo.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión al cargar la lista de vehiculos:', error);
        mostrarMensaje('Error de conexión al cargar la lista de vehiculos.', 'error');
      }
    };

    const setupWatchers = () => {
      const createNumberWatcher = (propName) => {
        watch(() => formData.value[propName], (newValue, oldValue) => {
          if (document.activeElement.id !== propName) {
            const currentFormattedValue = String(formData.value[propName]);
            const expectedFormattedValue = formatearMilesConPunto(limpiarFormatoNumerico(newValue));

            if (currentFormattedValue !== expectedFormattedValue) {
              const cleanedValue = limpiarFormatoNumerico(newValue);
              formData.value[propName] = isNaN(cleanedValue) ? '0' : formatearMilesConPunto(cleanedValue);
            }
          }
        }, { immediate: false });
      };

      createNumberWatcher('kilometraje');
      createNumberWatcher('precio_compra');
      createNumberWatcher('gastos_asociados');
      createNumberWatcher('precio_venta');

    };

    onMounted(() => {
      setupWatchers();
    });

    return {
      formData,
      opcionestipo_vehiculo_id,
      opcionestipo_marca_id,
      opcionesTipoTransmision,
      opcionesTipoCombustible,
      isLoading,
      handleSubmit,
      limpiarFormulario,
      crearRegistro,
      modificarRegistro,
      mensaje,
      tipoMensaje,
      ontipo_vehiculo_idChange,
      onTipoCombustibleChange,
      onTipoTransmisionChange,
      ontipo_marca_idChange,
      mostrarMensaje,
      limpiarMensaje,
      cargarDatosVehiculo,
      cargartipo_vehiculo_id,
      cargarTipoCombustibles,
      cargarTipoTransmision,
      cargartipo_marca_id,
      registroAEliminarId,
      mostrarModalEliminar,
      abrirModalEliminar,
      cerrarModalEliminar,
      eliminarRegistroConfirmado,
      cargarListaDeVehiculos,
      datos,
      limpiarFormatoNumerico,
      formatearMilesConPunto,
      limpiarFormatoNumerico,
      formatearMilesConPunto,
      obtenerTotalGastosPorPatente,
      nivel,
    };
  },
};
</script>

<template>
  <Header></Header>

  <div class="container-fluid mt-3" style="width: calc(100% - 30px); margin: 0 auto;">
    <div class="card shadow-sm mt-3 ">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Mantención
        Vehículos
      </div>
      <div class="card-body mt-3">

        <form @submit.prevent="handleSubmit">

          <div class="mb-3 row align-items-center">
            <label for="patenteBuscar" class="col-md-2 col-form-label negrita">Patente</label>
            <div class="col-md-3">
              <input type="text" class="form-control form-control-sm negrita" size="10" maxlength="10" :maxlength="8"
                id="patenteBuscar" name="patenteBuscar" v-model="formData.patenteBuscar" style="width: 200px" />
            </div>
            <div class="col-md-auto ms-4">
              <button type="button" class="btn btn-secondary btn-sm"
                @click="cargarDatosVehiculo(formData.patenteBuscar)">
                Buscar
              </button>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <div class="card-title" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                Gestión
                de Vehículos</div>
            </div>
            <div class="card-body left">
              <div class="row mb-3">
                <div class="col-md-4">
                  <label class="form-label negrita">¿Revisión Técnica al día?</label>
                  <div>
                    <div class="form-check form-check-inline">
                      <input class="form-check-input" type="radio" name="revision_tecnica_al_dia" id="revision_si"
                        :value="true" v-model="formData.revision_tecnica_al_dia"
                        :checked="formData.revision_tecnica_al_dia == 1" />
                      <label class="form-check-label" for="revision_si">Sí</label>
                    </div>
                    <div class="form-check form-check-inline">
                      <input class="form-check-input" type="radio" name="revision_tecnica_al_dia" id="revision_no"
                        :value="false" v-model="formData.revision_tecnica_al_dia"
                        :checked="formData.revision_tecnica_al_dia == 0" />
                      <label class="form-check-label" for="revision_no">No</label>
                    </div>
                  </div>
                </div>

                <div class="col-md-4">
                  <label class="form-label negrita">¿Permiso de Circulación?</label>
                  <div>
                    <div class="form-check form-check-inline">
                      <input class="form-check-input" type="radio" name="permiso_circulacion" id="permiso_si"
                        :value="true" v-model="formData.permiso_circulacion"
                        :checked="formData.permiso_circulacion == 1" />
                      <label class="form-check-label" for="permiso_si">Sí</label>
                    </div>
                    <div class="form-check form-check-inline">
                      <input class="form-check-input" type="radio" name="permiso_circulacion" id="permiso_no"
                        :value="false" v-model="formData.permiso_circulacion"
                        :checked="formData.permiso_circulacion == 0" />
                      <label class="form-check-label" for="permiso_no">No</label>
                    </div>
                  </div>
                </div>

                <div class="col-md-4">
                  <label class="form-label negrita">¿Seguro Vigente?</label>
                  <div>
                    <div class="form-check form-check-inline">
                      <input class="form-check-input" type="radio" name="seguro_vigente" id="seguro_si" :value="true"
                        v-model="formData.seguro_vigente" :checked="formData.seguro_vigente == 1" />
                      <label class="form-check-label" for="seguro_si">Sí</label>
                    </div>
                    <div class="form-check form-check-inline">
                      <input class="form-check-input" type="radio" name="seguro_vigente" id="seguro_no" :value="false"
                        v-model="formData.seguro_vigente" :checked="formData.seguro_vigente == 0" />
                      <label class="form-check-label" for="seguro_no">No</label>
                    </div>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label class="form-label negrita">Marca Vehículo</label>
                  <div>
                    <v-select :options="opcionestipo_marca_id" name="tipo_marca_id" id="tipo_marca_id"
                      v-model="formData.tipo_marca_id" label="descripcion" placeholder="Seleccionar tipo de marca"
                      :disabled="isLoading" class="mi-dropdown" @update:modelValue="ontipo_marca_idChange"
                      :reduce="option => option.id"> </v-select>

                    <div v-if="isLoading" class="form-text text-muted">Cargando tipos de marca...</div>
                  </div>
                  <p v-if="formData.tipo_marca_id">ID de la marca seleccionada: {{ formData.tipo_marca_id }}</p>
                </div>

                <div class="col-md-4 mb-3">
                  <label for="modelo" class="form-label negrita">Modelo</label>
                  <input type="text" class="form-control form-control-sm" id="modelo" v-model="formData.modelo"
                    style="width: 100%;" required />
                </div>

                <div class="col-md-4 mb-3">
                  <label class="form-label negrita">Tipo Vehículo</label>
                  <div>
                    <v-select :options="opcionestipo_vehiculo_id" name="tipo_vehiculo_id" id="tipo_vehiculo_id"
                      v-model="formData.tipo_vehiculo_id" label="descripcion" placeholder="Seleccionar tipo de vehículo"
                      :disabled="isLoading" class="mi-dropdown" @update:modelValue="ontipo_vehiculo_idChange"
                      :reduce="option => option.id"> </v-select>

                    <div v-if="isLoading" class="form-text text-muted">Cargando tipos de vehículo...</div>
                  </div>
                  <p v-if="formData.tipo_vehiculo_id">ID del tipo de vehículo seleccionado: {{ formData.tipo_vehiculo_id
                  }}</p>
                </div>
              </div>

              <div class="row">
                <div class="col-md-4 mb-3">
                  <label for="TipoCombustible" class="form-label negrita">Tipo Combustible</label>
                  <div>
                    <v-select name="TipoCombustible" id="TipoCombustible" v-model="formData.TipoCombustible"
                      label="descripcion" placeholder="Seleccionar tipo de combustible"
                      :options="opcionesTipoCombustible" :disabled="isLoading" class="mi-dropdown"
                      @update:modelValue="onTipoCombustibleChange" :reduce="option => option.id"></v-select>
                    <div v-if="isLoading" class="form-text text-muted">Cargando tipos de combustible...</div>
                  </div>
                  <p v-if="formData.TipoCombustible">ID del tipo de combustible seleccionado: {{
                    formData.TipoCombustible
                  }}
                  </p>
                </div>

                <div class="col-md-4 mb-3">
                  <label for="TipoTransmision" class="form-label negrita">Tipo Trasmisión</label>
                  <div>
                    <v-select name="TipoTransmision" id="TipoTransmision" v-model="formData.TipoTransmision"
                      label="descripcion" placeholder="Seleccionar tipo de transmisión"
                      :options="opcionesTipoTransmision" :disabled="isLoading" class="mi-dropdown"
                      @update:modelValue="onTipoTransmisionChange" :reduce="option => option.id"></v-select>
                    <div v-if="isLoading" class="form-text text-muted">Cargando tipos de Transmisión...</div>
                  </div>
                  <p v-if="formData.TipoTransmision">ID del tipo de Transmisión seleccionado: {{
                    formData.TipoTransmision
                  }}
                  </p>
                </div>

                <div class="col-md-4 mb-3">
                  <label for="agno" class="form-label negrita">Año</label>
                  <input placeholder="XXXX" type="number" size="4" class="form-control form-control-sm" id="agno"
                    v-model="formData.agno" style="width: 100%;" required />
                </div>
              </div>

              <div class="row">
                <div class="col-md-4 mb-3">
                  <label for="numero_motor" class="form-label negrita">Número Motor</label>
                  <input type="text" size="20" maxlength="20" class="form-control form-control-sm" id="numero_motor"
                    name="numero_motor" v-model="formData.numero_motor" style="width: 100%;" required />
                </div>

                <div class="col-md-4 mb-3">
                  <label for="chasis" class="form-label negrita">Número Chasis</label>
                  <input type="text" size="20" maxlength="20" class="form-control form-control-sm" id="chasis"
                    v-model="formData.numero_chasis" style="width: 100%;" required />
                </div>

                <div class="col-md-4 mb-3">
                  <label for="color" class="form-label negrita">Color</label>
                  <input type="text" size="50" maxlength="50" class="form-control form-control-sm" id="color"
                    v-model="formData.color" style="width: 100%;" required />
                </div>
              </div>

              <div class="row">
                <div class="col-md-4 mb-3">
                  <label for="patente" class="form-label negrita">Patente</label>
                  <input placeholder=" XX-XX-XX" type="text" size="10" maxlength="10"
                    class="form-control form-control-sm" id="patente" v-model="formData.patente" style="width: 100%;"
                    required />
                </div>

                <div class="col-md-4 mb-3">
                  <label for="kilometraje" class="form-label negrita">Kilometraje</label>
                  <input type="text" size="10" maxlength="20" id="kilometraje" class="form-control form-control-sm"
                    v-model="formData.kilometraje" style="width: 100%;" required
                    @focus="formData.kilometraje = limpiarFormatoNumerico(formData.kilometraje)" />
                </div>

                <div class="col-md-4 mb-3">
                  <label for="precio_compra" class="form-label negrita">Precio compra $</label>
                  <input type="text" size="20" maxlength="20" id="precio_compra" class="form-control form-control-sm"
                    v-model="formData.precio_compra" style="width: 100%;" required
                    @focus="formData.precio_compra = limpiarFormatoNumerico(formData.precio_compra)" />
                </div>
              </div>

              <div class="row">
                <div class="col-md-4 mb-3">
                  <label for="total_gastos_cargados" class="form-label negrita">Total Gastos (Tabla Costos) $</label>
                  <div style="font-size: small;">
                    {{ formData.total_valor_patente }}
                  </div>
                </div>

                <div class="col-md-4 mb-3">
                  <label for="precio_venta" class="form-label negrita">Precio Venta $</label>
                  <input type="text" size="20" maxlength="20" id="precio_venta" class="form-control form-control-sm"
                    v-model="formData.precio_venta" style="width: 100%;"
                    @focus="formData.precio_venta = limpiarFormatoNumerico(formData.precio_venta)" />
                </div>

                <div class="col-md-4 mb-3">
                  <label class="form-label negrita">Propiedad Automotriz</label>
                  <div class="d-flex align-items-center" style="height: 31px;">
                    <div class="form-check form-check-inline">
                      <input class="form-check-input" type="radio" name="propiedad_automotriz" id="propiedad_si"
                        :value="true" v-model="formData.propiedad_automotriz"
                        :checked="formData.propiedad_automotriz == 1" />
                      <label class="form-check-label" for="propiedad_si">Sí</label>
                    </div>
                    <div class="form-check form-check-inline">
                      <input class="form-check-input" type="radio" name="propiedad_automotriz" id="propiedad_no"
                        :value="false" v-model="formData.propiedad_automotriz"
                        :checked="formData.propiedad_automotriz == 0" />
                      <label class="form-check-label" for="propiedad_no">No</label>
                    </div>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-3 mb-3">
                  <label class="form-label negrita">Habilitado para venta</label>
                  <div class="d-flex align-items-center" style="height: 31px;">
                    <div class="form-check form-check-inline">
                      <input class="form-check-input checkbox-grande" type="checkbox" id="habilitado_venta"
                        v-model="formData.habilitado_venta">
                      <label class="form-check-label" for="habilitado_venta">Sí</label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-center">
                <div class="col-md-auto ms-2">
                  <button type="submit" class="btn btn-sm btn-secondary">Crear</button>
                </div>

                <div class="col-md-auto ms-2">
                  <button type="button" class="btn btn-sm btn-secondary" @click="modificarRegistro(formData.patente)">
                    Modificar
                  </button>
                </div>

                <div class="col-md-auto ms-2" v-if="nivel === 'ADMIN'">
                  <button type="button" class="btn btn-sm btn-secondary" @click="abrirModalEliminar(formData.patente)">
                    Eliminar
                  </button>
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

        <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Lista de Vehículos
        </h3>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Patente</th>
              <th>Color</th>
              <th>Marca</th>
              <th>Tipo Vehículo</th>
              <th>Año</th>
              <th>Kilometraje</th>
              <th>Precio Compra</th>
              <th>Precio Venta</th>
              <th>Propiedad Automotriz</th>
              <th>Al día</th>
              <th>Permiso Circulación</th>
              <th>Seguro Vigente</th>
              <th>Habilitado Venta</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vehiculo in datos" :key="vehiculo.id">
              <td>{{ vehiculo.patente }}</td>
              <td>{{ vehiculo.color }}</td>
              <td>{{ vehiculo.marca_descripcion }}</td>
              <td>{{ vehiculo.vehiculo_descripcion }}</td>
              <td>{{ vehiculo.agno }}</td>
              <td>{{ vehiculo.kilometraje }}</td>
              <td>{{ vehiculo.precio_compra }}</td>
              <td>{{ vehiculo.precio_venta }}</td>
              <td>{{ vehiculo.propiedad_automotriz ? 'Sí' : 'No' }}</td>
              <td>{{ vehiculo.revision_tecnica_al_dia ? 'Sí' : 'No' }}</td>
              <td>{{ vehiculo.permiso_circulacion ? 'Sí' : 'No' }}</td>
              <td>{{ vehiculo.seguro_vigente ? 'Sí' : 'No' }}</td>
              <td>
                <span :class="vehiculo.habilitado_venta ? 'badge bg-success' : 'badge bg-danger'">
                  {{ vehiculo.habilitado_venta ? 'Sí' : 'No' }}
                </span>
              </td>

              <td>
                <button v-if="nivel === 'ADMIN'" @click="abrirModalEliminar(vehiculo.patente)"
                  class="btn btn-danger btn-sm">Eliminar</button>
              </td>
            </tr>
            <tr v-if="datos.length === 0">
              <td colspan="13">No hay vehículos registrados.</td>
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
            ¿Estás seguro de que deseas eliminar Vehículo con Patente: **{{ registroAEliminarId }}**?
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
.negrita {
  font-weight: bold;
  font-size: small;
}

.mi-dropdown {
  width: 310px;
}

.checkbox-grande {
  transform: scale(1.25);
  margin-right: 8px;
}
</style>