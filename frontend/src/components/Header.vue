<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const nivel = ref(null);
const usuario = ref(null);
const isMenuOpen = ref(false);

// Estados para controlar los submenús (Desktop hover / Móvil toggle)
const mostrarClientesSubmenu = ref(false);
const mostrarVehiculosSubmenu = ref(false);
const mostrarInformesSubmenu = ref(false);

const toggleMenu = () => {
    isMenuOpen.value = !isMenuOpen.value;
};

onMounted(() => {
    nivel.value = localStorage.getItem('user_nivel');
    usuario.value = localStorage.getItem('user_usuario');
});

const logout = () => {
    localStorage.clear();
    nivel.value = null;
    usuario.value = null;
    isMenuOpen.value = false;
    router.push('/');
};

// Cerrar el menú lateral al navegar a otra página
watch(route, () => {
    isMenuOpen.value = false;
});
</script>

<template>
    <header class="header-area">
        <div v-if="isMenuOpen" class="menu-overlay" @click="toggleMenu"></div>

        <div class="top-header-area">
            <div class="container h-100">
                <div class="row h-100 align-items-center justify-content-between">
                    <div class="col-12 col-sm-6">
                        <div class="breaking-news">
                            <a href="mailto:ventas@nicolasautomotriz.cl" class="text-white small">ventas@nicolasautomotriz.cl</a>
                        </div>
                    </div>
                    <div class="col-12 col-sm-6 text-end d-none d-sm-block">
                        <div class="top-social-info">
                            <a href="#"><i class="fa fa-facebook"></i></a>
                            <a href="#"><i class="fa fa-instagram"></i></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="delicious-main-menu">
            <div class="classy-nav-container container-fluid">
                <nav class="classy-navbar justify-content-between">
                    <router-link class="nav-brand" to="/">
                        <img src="/img/core-img/logo.png" alt="logo" class="logo-img" />
                    </router-link>

                    <div class="classy-navbar-toggler" @click="toggleMenu">
                        <span class="navbarToggler" :class="{ 'active': isMenuOpen }">
                            <span></span><span></span><span></span>
                        </span>
                    </div>

                    <div class="classy-menu" :class="{ 'menu-on': isMenuOpen }">
                        <div class="classycloseIcon" @click="toggleMenu">
                            <div class="cross-wrap"><span class="top"></span><span class="bottom"></span></div>
                        </div>

                        <div class="classynav">
                            <ul>
                                <li><router-link to="/">Inicio</router-link></li>
                                <li><router-link to="/Presupuesto">Presupuestos</router-link></li>
                              
                                <li v-if="usuario === 'JMUNOZ' || usuario === 'VVERGARA'">
                                    <router-link to="/TempAdmin">Acceso Temporal</router-link>
                                </li>

                                <li><router-link to="/Contratos">Contratos</router-link></li>
                                <li><router-link to="/ListaCuotas">Pagos</router-link></li>

                                <li @mouseenter="mostrarInformesSubmenu = true" @mouseleave="mostrarInformesSubmenu = false" v-if="usuario === 'JMUNOZ' || usuario === 'VVERGARA'">
                                    <a href="javascript:void(0)">Informes <i class="fa fa-angle-down"></i></a>
                                    <ul class="dropdown" v-show="mostrarInformesSubmenu">
                                        <li><router-link to="/CuotasImpagas">Informe Cuotas</router-link></li>
                                        <li><router-link to="/Informes">Informe Ventas</router-link></li>
                                        <li><router-link to="/InformePagos1">Informe Créditos</router-link></li>
                                        <li><router-link to="/Auditoria">Auditoria</router-link></li>
                                    </ul>
                                </li>
                               
                                <li><router-link to="/Administracion">Admin</router-link></li>
                                
                                <li class="logout-item">
                                    <a href="#" @click.prevent="logout">Cerrar Sesión</a>
                                </li>
                            </ul>
                        </div>
                    </div>
                </nav>
            </div>
        </div>
    </header>
</template>

<style scoped>
.logo-img { width: 200px; height: auto; }

/* Desktop Styles */
.classy-navbar { display: flex; align-items: center; height: 90px; }
.classynav ul { display: flex; list-style: none; margin: 0; padding: 0; }
.classynav ul li { position: relative; }
.classynav ul li a { padding: 15px 12px; font-weight: 600; color: #444; font-size: 14px; text-decoration: none; }

/* Submenu / Dropdown */
.dropdown {
    position: absolute;
    background: #fff;
    width: 220px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    top: 100%;
    left: 0;
    z-index: 100;
    padding: 10px 0;
    border-top: 3px solid #fc6c27;
}
.dropdown li a { padding: 8px 20px !important; font-size: 13px; }

/* Mobile Overlay */
.menu-overlay {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 998;
}

/* --- RESPONSIVE LOGIC --- */
.classy-navbar-toggler { display: none; cursor: pointer; }
.navbarToggler span { display: block; width: 25px; height: 3px; background: #333; margin: 4px 0; }

@media screen and (max-width: 1100px) {
    .classy-navbar-toggler { display: block; }
    
    .classy-menu {
        position: fixed;
        top: 0; left: -310px;
        width: 300px; height: 100%;
        background: #fff;
        z-index: 999;
        transition: 0.4s;
        padding: 60px 20px;
        overflow-y: auto;
    }
    
    .classy-menu.menu-on { left: 0; }
    
    .classynav ul { flex-direction: column; }
    .classynav ul li { width: 100%; border-bottom: 1px solid #f5f5f5; }
    
    /* En móvil los dropdowns se integran verticalmente */
    .dropdown {
        position: static;
        width: 100%;
        box-shadow: none;
        border: none;
        display: block; /* Visibles en el menú móvil para facilitar navegación */
        background: #fafafa;
        padding-left: 15px;
    }
    
    .classycloseIcon { position: absolute; top: 20px; right: 20px; }
    .logout-item a { color: #d9534f !important; }
}
</style>