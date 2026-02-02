<script setup>
import { ref, onMounted } from 'vue'; // Importa onMounted
import { useRouter } from 'vue-router'; // Importa useRouter si quieres botón de logout

// Reactive variable to store the user's level
const userNivel = ref(null);

// Function to check user level from localStorage
const checkUserLevel = () => {
  userNivel.value = localStorage.getItem('user_nivel');
};

// Call checkUserLevel when the component is mounted
onMounted(() => {
  checkUserLevel();
});

// Opcional: Si quieres un botón de logout
const router = useRouter();
const logout = () => {
  localStorage.removeItem('user_nivel');
  localStorage.removeItem('user_usuario');
  localStorage.removeItem('user_id');
  // localStorage.removeItem('logged_in_user'); // Si guardaste el objeto completo
  router.push('/'); // Redirige al login
};

// ... (resto de tus variables ref)
const mostrarClientesSubmenu = ref(false);
const mostrarVehiculosSubmenu = ref(false);
const mostrarTipoVehiculoSubmenu = ref(false);
const mostrarTipoCombustibleSubmenu = ref(false);
const mostrarTipoTrasmisionSubmenu = ref(false);
const mostrarSobreNosotrosSubmenu = ref(false);
</script>

<template>
    <header class="header-area">
        <div class="delicious-main-menu">
            <div class="classy-nav-container breakpoint-off">
                <div class="container">
                    <router-link class="nav-brand" to="/">
                        <img src="/img/core-img/logo.png" alt="logo" style="width:280px; height:100px" /></router-link>
                    <div class="classy-navbar-toggler">
                        <span class="navbarToggler"><span></span><span></span><span></span></span>
                    </div>
                    <nav class="classy-navbar justify-content-between" id="deliciousNav">
                        <div class="classy-menu">
                            <div class="classynav">
                                <ul>
                                    <nav>
                                        <ul>
                                            <li>
                                                <router-link to="/inicio" title="Home">Inicio</router-link>
                                            </li>
                                            <li>
                                                <router-link to="/Clientes" title="Clientes">Clientes</router-link>
                                            </li>

                                            <li v-if="userNivel === 'ADMIN'">
                                                <router-link to="/Vendedores" title="Usuarios">Usuarios</router-link>
                                            </li>
                                            <li v-if="userNivel === 'ADMIN'">
                                                <router-link to="/TempAdmin" title="Privilegios Temporales">Admin Temporal</router-link>
                                            </li>
                                            <li>
                                                <router-link to="/Costos" title="Costos Asociados">Gastos</router-link>
                                            </li>

                                            <li>
                                                <router-link to="/TipoVehiculos" title="Tipo De Vehiculo">Tipo
                                                    Vehiculo</router-link>
                                            </li>
                                            <li>
                                                <router-link to="/TipoCombustible"
                                                    title="Tipo Combustible">Combustible</router-link>
                                            </li>
                                            <li>
                                                <router-link to="/TipoTrasmision"
                                                    title="Tipo Trasmision">Transmisión</router-link>
                                            </li>
                                            <li>
                                                <router-link to="/TipoPago" title="Tipo De Pago">Pago</router-link>
                                            </li>
                                            <li>
                                                <router-link to="/Marca" title="Marcas vehículos">Marca
                                                    Vehículos</router-link>
                                            </li>
                                            <li>
                                                <router-link to="/Vehiculos" title="Vehiculos">Vehiculos</router-link>
                                            </li>

                                            <li>
                                                <a href="#" @click.prevent="logout">Cerrar Sesión</a>
                                            </li>

                                        </ul>
                                    </nav>
                                </ul>
                            </div>
                        </div>
                    </nav>
                </div>
            </div>
        </div>
    </header>
    <br>
    <br>
    <br>
    <br>
</template>