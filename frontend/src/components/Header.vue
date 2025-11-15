<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const nivel = ref(null);

// Variables de submenús... (se mantienen sin cambios)
const mostrarClientesSubmenu = ref(false);
const mostrarVehiculosSubmenu = ref(false);
const mostrarTipoVehiculoSubmenu = ref(false);
const mostrarTipoCombustibleSubmenu = ref(false);
const mostrarTipoTrasmisionSubmenu = ref(false);
const mostrarSobreNosotrosSubmenu = ref(false);

onMounted(() => {
    nivel.value = localStorage.getItem('user_nivel');
});

const logout = () => {
    localStorage.removeItem('user_nivel');
    localStorage.removeItem('user_usuario');
    localStorage.removeItem('user_id');
    nivel.value = null;
    router.push('/');
};
</script>

<template>
    <header class="header-area">
        <div class="top-header-area">
            <div class="container h-100">
                <div class="row h-100 align-items-center justify-content-between">
                    <div class="col-12 col-sm-6">
                        <div class="breaking-news">
                            <div id="breakingNewsTicker" class="ticker">
                                <ul>
                                    <li><a href="mailto:ventas@nicolasautomotriz.cl">ventas@nicolasautomotriz.cl</a>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-sm-6">
                        <div class="top-social-info text-right">
                            <a href="#"><i class="fa fa-pinterest" aria-hidden="true"></i></a>
                            <a href="#"><i class="fa fa-facebook" aria-hidden="true"></i></a>
                            <a href="#"><i class="fa fa-twitter" aria-hidden="true"></i></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="delicious-main-menu">
            <div class="classy-nav-container container-fluid">
                <nav class="classy-navbar justify-content-between" id="deliciousNav">
                    <router-link class="nav-brand" to="/">
                        <img src="/img/core-img/logo.png" alt="logo" style="width:270px; height:100px" />
                    </router-link>

                    <div class="classy-menu">
                        <div class="classycloseIcon">
                            <div class="cross-wrap"><span class="top"></span><span class="bottom"></span></div>
                        </div>
                        <div class="classynav">
                            <ul class="w-100">
                                <nav class="w-100">
                                    <ul class="w-100">
                                        <li>
                                            <router-link to="/" title="Home">Inicio</router-link>
                                        </li>
                                        <li>
                                            <router-link to="/Ingreso_arriendo" title="Ingreso Arriendo">Ingreso Arriendo</router-link>
                                        </li>
                                          <li>
                                            <router-link to="/Tipo_arriendo" title="Tipo Arriendo">Tipo Arriendo</router-link>
                                        </li>
                                          <li>
                                            <router-link to="/Gastos" title="Gastos Arriendo">Gastos Arriendo</router-link>
                                        </li>
                                        
                                        
                                        <li>
                                            <router-link to="/Presupuesto"
                                                title="Creación de Presupuestos">Presupuestos</router-link>
                                        </li>
                                        <li>
                                            <router-link to="/Contratos"
                                                title="Creacion de Contratos">Contratos</router-link>
                                        </li>
                                        <li>
                                            <router-link to="/ListaCuotas" title="Listados CLientes">Pagos</router-link>
                                        </li>
                                        <li>
                                            <router-link to="/CuotasImpagas" title="Informes de Cuotas Impagas">Informe
                                                Cuotas Impagas</router-link>
                                        </li>
                                        <li v-if="nivel === 'ADMIN'">
                                            <router-link to="/Informes"
                                                title="Informes Utilidades Negocios Utilidad Ventas">Informe
                                                Ventas</router-link>
                                        </li>
                                        <li v-if="nivel === 'ADMIN'">
                                            <router-link to="/InformePagos1"
                                                title="Informes 1 Utilidades Créditos">Informe Créditos</router-link>
                                        </li>
                                        <li v-if="nivel === 'ADMIN'">
                                            <router-link to="/InformeVehiculos"
                                                title="Informes Vehiculos Propiedad Automotora">Informe Vehiculos P.A.</router-link>
                                        </li>
                                        <li v-if="nivel === 'ADMIN'">
                                            <router-link to="/resumen" title="Informes Resumen">Informe
                                                Resumen</router-link>
                                        </li>

                                        <li>
                                            <RouterLink to="/Administracion">Admin</RouterLink>
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
    </header>
</template>

<style scoped>
/* Estilos CSS - Se mantiene sin cambios ya que el problema es en la plantilla. */
nav ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
}

nav ul li {
    position: relative;
}

nav ul li a {
    display: block;
    padding: 10px 15px;
    text-decoration: none;
    color: #333;
}

nav ul li a:hover {
    background-color: #f0f0f0;
}

.submenu {
    list-style: none;
    padding: 0;
    margin: 0;
    position: absolute;
    top: 100%;
    left: 0;
    background-color: #fff;
    border: 1px solid #ccc;
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    min-width: 350px;
}

.submenu li a {
    display: block;
    padding: 8px 12px;
    text-decoration: none;
    color: #333;
}

.submenu li a:hover {
    background-color: #eee;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
    transition: opacity 0.3s ease, transform 0.3s ease;
}

.slide-fade-enter-from {
    opacity: 0;
    transform: translateY(-10px);
}

.slide-fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

.submenu[v-show='false'] {
    display: none;
}
</style>