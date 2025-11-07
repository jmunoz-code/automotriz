<script>
import Header from '@/components/HeaderAdmin.vue';
import Footer from '@/components/Footer.vue';

export default {
    components: {
        Header, // Registra el componente importado
        Footer, // Registra el componente importado
    },
}
</script>

<template>
    <Header></Header>

    <div class="container mt-3">
        <h2 class="text-center"></h2>
    </div>

    <Footer></Footer>
</template>

<style scoped>
/* Puedes agregar estilos personalizados aquí si lo deseas */
</style>