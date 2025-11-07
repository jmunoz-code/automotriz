// clientesServices.js
export async function getDatosClientes() {
    let resultado; // Declaramos la variable resultado
   // console.log("API URL:", `${import.meta.env.VITE_API_URL}Clientes`);
  
    try {
     let respuesta = await fetch(`${import.meta.env.VITE_API_URL}Clientes/`,{ headers: { 'content-type': 'application/json' } });
    
  
  
     if (!respuesta.ok) {
       console.error(`Error al obtener datos de clientes: ${respuesta.status} - ${respuesta.statusText}`);
       return null; // O lanza un error más específico
     }
  
     const data = await respuesta.json();
     resultado = data; // Asignamos los datos de la respuesta a resultado
  
     return resultado;
    } catch (error) {
     console.error("Error al obtener los datos de clientes:", error);
     return null; // O lanza el error, dependiendo de cómo quieras manejarlo
    }
   }

   // clientesServices.js
export async function getDatosClientePorRut(rut) {
  let resultado;
  console.log("API URL (por RUT):", `${import.meta.env.VITE_API_URL}Clientes${rut}/`);

  try {
      const respuesta = await fetch(`${import.meta.env.VITE_API_URL}Clientes${rut}/`, {
          headers: {
              'Content-Type': 'application/json'
          }
      });

      if (!respuesta.ok) {
          console.error(`Error al obtener datos del cliente con RUT ${rut}: ${respuesta.status} - ${respuesta.statusText}`);
          return null; // O lanza un error más específico
      }

      const data = await respuesta.json();
      resultado = data; // Asignamos los datos de la respuesta a resultado

      return resultado;
  } catch (error) {
      console.error(`Error al obtener los datos del cliente con RUT ${rut}:`, error);
      return null; // O lanza el error, dependiendo de cómo quieras manejarlo
  }
}


  


  