<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const userNivel = ref(null);
const isMenuOpen = ref(false);
const router = useRouter();
const route = useRoute();

const checkUserLevel = () => {
  userNivel.value = localStorage.getItem('user_nivel');
};

const toggleMenu = () => {
    isMenuOpen.value = !isMenuOpen.value;
};

onMounted(() => {
  checkUserLevel();
});

const logout = () => {
  localStorage.removeItem('user_nivel');
  localStorage.removeItem('user_usuario');
  localStorage.removeItem('user_id');
  isMenuOpen.value = false;
  router.push('/');
};

// Cerrar menú al cambiar de página
watch(route, () => {
    isMenuOpen.value = false;
});
</script>

<template>
    <header class="header-area">
        <div v-if="isMenuOpen" class="menu-overlay" @click="toggleMenu"></div>

        <div class="delicious-main-menu">
            <div class="classy-nav-container breakpoint-off">
                <div class="container">
                    <nav class="classy-navbar justify-content-between" id="deliciousNav">
                        <router-link class="nav-brand" to="/">
                            <img src="/img/core-img/logo.png" alt="logo" class="logo-responsive" />
                        </router-link>

                        <div class="classy-navbar-toggler" @click="toggleMenu">
                            <span class="navbarToggler">
                                <span></span><span></span><span></span>
                            </span>
                        </div>

                        <div class="classy-menu" :class="{ 'menu-on': isMenuOpen }">
                            <div class="classycloseIcon" @click="toggleMenu">
                                <div class="cross-wrap"><span class="top"></span><span class="bottom"></span></div>
                            </div>

                            <div class="classynav">
                                <ul>
                                    <li><router-link to="/inicio">Inicio</router-link></li>
                                    <li><router-link to="/Clientes">Clientes</router-link></li>

                                    <li v-if="userNivel === 'ADMIN'">
                                        <router-link to="/Vendedores">Usuarios</router-link>
                                    </li>
                                   
                                    <li><router-link to="/Costos">Gastos</router-link></li>
                                    <li><router-link to="/Vehiculos">Vehículos</router-link></li>
                                    
                                    <li><router-link to="/TipoVehiculos">Tipo Veh.</router-link></li>
                                    <li><router-link to="/TipoCombustible">Combustible</router-link></li>
                                    <li><router-link to="/Marca">Marcas</router-link></li>

                                    <li>
                                        <a href="#" @click.prevent="logout" class="logout-link">Cerrar Sesión</a>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </nav>
                </div>
            </div>
        </div>
    </header>
</template>

<style scoped>
/* --- ESTILOS GENERALES --- */
.logo-responsive {
    width: 220px;
    height: auto;
}

.classy-navbar {
    display: flex;
    align-items: center;
    height: 100px;
}

.classynav ul {
    display: flex;
    list-style: none;
    padding: 0;
    margin: 0;
}

.classynav ul li a {
    padding: 10px 12px;
    font-weight: 600;
    font-size: 14px;
    color: #444;
    transition: 0.3s;
}

.classynav ul li a:hover {
    color: #fc6c27;
}

/* --- OVERLAY --- */
.menu-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 998;
}

/* --- RESPONSIVE LOGIC --- */
.classy-navbar-toggler {
    display: none;
    cursor: pointer;
}

.navbarToggler span {
    display: block;
    width: 25px;
    height: 3px;
    background-color: #333;
    margin: 4px 0;
}

@media screen and (max-width: 991px) {
    .classy-navbar-toggler {
        display: block;
    }

    .classy-menu {
        position: fixed;
        top: 0;
        left: -320px; /* Oculto */
        width: 300px;
        height: 100%;
        background: #fff;
        z-index: 999;
        transition: all 0.4s ease-in-out;
        padding: 60px 30px;
        box-shadow: 5px 0 15px rgba(0,0,0,0.1);
        overflow-y: auto;
    }

    .classy-menu.menu-on {
        left: 0; /* Entra desde la izquierda */
    }

    .classynav ul {
        flex-direction: column;
    }

    .classynav ul li {
        width: 100%;
        border-bottom: 1px solid #f5f5f5;
    }

    .classynav ul li a {
        display: block;
        padding: 15px 0;
        font-size: 16px;
    }

    .classycloseIcon {
        position: absolute;
        top: 20px;
        right: 20px;
    }

    .logout-link {
        color: #d9534f !important;
    }
}
</style>