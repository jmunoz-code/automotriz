import Clientes from '@/views/Clientes.vue'

import Gastos from '@/views/Gastos.vue'
import Informe_arriendo from '@/views/Informe_arriendo.vue'

import Tipo_arriendo from '@/views/Tipo_arriendo.vue'
import Ingreso_arriendo from '@/views/Ingreso_arriendo.vue'
import InformeVehiculos from '@/views/InformeVehiculos.vue'
import resumen from '@/views/resumen.vue'
import Comprobante from '@/views/Comprobante.vue' 
import InformePagos1 from '@/views/InformePagos1.vue'
import CuotasImpagas from '@/views/CuotasImpagas.vue'
import Inicio from '@/views/Inicio.vue'
import Informes from '@/views/Informes.vue'
import AbonoCuotas from '@/views/AbonoCuotas.vue'
import ListaCuotas from '@/views/ListaCuotas.vue'
import Presupuesto from '@/views/Presupuesto.vue'
import ContratoCompraVenta from '@/views/ContratoCompraVenta.vue'
import CartaResponsabilidad from '@/views/Carta.vue'
import Vendedores from '@/views/Vendedores.vue'
import Marca from '@/views/Marca.vue'
import Vehiculos from '@/views/Vehiculos.vue'
import Costos from '@/views/Costos.vue'
import TipoVehiculos from '@/views/TipoVehiculos.vue'
import TipoCombustible from '@/views/TipoCombustible.vue'
import TipoTrasmision from '@/views/TipoTrasmision.vue'
import TipoPago from '@/views/TipoPago.vue'
import Contratos from '@/views/Contratos.vue'
import Administracion from '@/views/Administracion.vue'
import Error404 from '@/views/Error404.vue'

import { createRouter, createWebHistory } from 'vue-router'
import 'vue-select/dist/vue-select.css'; // Importa los estilos de vue-select


//  component: () => import('@/views/LoginForm.vue'),

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
     {
      path: '/', // <--- Aquí tienes el LoginForm
      component: () => import('@/views/LoginForm.vue'),
      name: 'Home'
    },  
    {
      path: '/Inicio',
      component: () => import('@/views/Inicio.vue'),
      name: 'Inicio'
    },
    {
      path: '/Informes',
      component: Informes,
      name: 'Informes'
    },
     {
      path: '/Ingreso_arriendo',
      component: Ingreso_arriendo,
      name: 'Ingreso_arriendo'
    },
    {
      path: '/Gastos',
      component: Gastos,
      name: 'Gastos'
    },
    {
      path: '/Tipo_arriendo',
      component: Tipo_arriendo,
      name: 'Tipo_arriendo'
    },

    {
      path: '/Informe_arriendo',
      component: Informe_arriendo,
      name: 'Informe_arriendo'
    },

    
     {
      path: '/Comprobante',
      component: Comprobante,
      name: 'Comprobante'
    },
    {
      path: '/InformePagos1',
      component: InformePagos1,
      name: 'InformePagos1'
    },
      {
      path: '/resumen',
      component: resumen,
      name: 'resumen'
    },
    
    {
      path: '/CuotasImpagas',
      component: CuotasImpagas,
      name: 'CuotasImpagas'
    },
    {
      path: '/Administracion',
      component: Administracion,
      name: 'Administracion'
    },
    {
      path: '/Clientes',
      component: Clientes,
      name: 'Clientes'
    },
    {
      path: '/Vehiculos',
      component: Vehiculos,
      name: 'Vehiculos'
    },
    {
      path: '/Costos',
      component: Costos,
      name: 'Costos'
    },
    {
      path: '/TipoVehiculos',
      component: TipoVehiculos,
      name: 'TipoVehiculos'
    },
    {
      path: '/TipoCombustible',
      component: TipoCombustible,
      name: 'TipoCombustible'
    },
    {
      path: '/TipoTrasmision',
      component: TipoTrasmision,
      name: 'TipoTrasmision'
    },
    {
      path: '/TipoPago',
      component: TipoPago,
      name: 'TipoPago'
    },
    {
      path: '/Contratos',
      component: Contratos,
      name: 'Contratos'
    },
    
   
    {
      // ¡Esta es la parte CRÍTICA!
      path: '/ContratoCompraVenta/:rut/:idPrep/:patente/:pagina', // <--- Asegúrate que tu path esté así
      name: 'ContratoCompraVenta',
      component: ContratoCompraVenta,
      props: true // <--- Esto también es fundamental
    },
    {
      // ¡Esta es la parte CRÍTICA!
      path: '/CartaResponsabilidad/:rut/:patente', // <--- Asegúrate que tu path esté así
      name: 'CartaResponsabilidad',
      component: CartaResponsabilidad,
      props: true // <--- Esto también es fundamental
    },
    {
      path: '/Presupuesto',
      name: 'Presupuesto',
      component: Presupuesto
    },
    {
      path: '/ListaCuotas',
      component: ListaCuotas,
    	 name: 'ListaCuotas',
    },
     {
      path: '/InformeVehiculos',
      component: InformeVehiculos,
      name: 'InformeVehiculos',
    },
  	 {
      path: '/Marca',
      component: Marca,
      name: 'Marca',
    },
   
    {
      path: '/Vendedores',
      component: Vendedores,
      name: 'Vendedores',

    },
    {
      path: '/AbonoCuotas', // <-- Nueva ruta para la nueva pantalla
      name: 'AbonoCuotas',
      component: AbonoCuotas,
    },
    {
      path: '/:pathMatch(.*)*',
      component: Error404,
    },
  ],
})

export default router