const API_URL = "http://localhost:8000";

// URL base de la API (cambiar según el entorno)
// Esta constante define la URL base de la API a la que se realizarán las solicitudes.
// Se puede cambiar esta URL según el entorno de desarrollo o producción. 
async function apiRequest(path, token, options = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  // Realiza la petición a la API con los headers y opciones proporcionadas.
  const respuesta = await fetch(`${API_URL}${path}`, { ...options, headers });
  // Si la respuesta no es exitosa, lanza un error con el detalle.
  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => ({}));
    throw new Error(cuerpo.detail || `Error ${respuesta.status}`);
  }
  if (respuesta.status === 204) return null;
  return respuesta.json();
}


// ---------------------------------------------------------------------
// AUTENTICACIÓN
// ---------------------------------------------------------------------
// Esta sección contiene las funciones relacionadas con la autenticación de usuarios. 
// Verifica las credenciales del usuario y obtiene un token de autenticación.
export const AuthAPI = {
  login: (email, password) =>
    apiRequest("/auth/login", null, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
};


// ---------------------------------------------------------------------
// PRODUCTOS
// Esta sección contiene las funciones relacionadas con la gestión de productos en el inventario.
// Proporciona funciones para listar, crear, actualizar y eliminar productos.
// ---------------------------------------------------------------------
export const ProductosAPI = {
  listar: (token) => apiRequest("/productos", token),
  crear: (token, datos) =>
    apiRequest("/productos", token, { method: "POST", body: JSON.stringify(datos) }),
  actualizar: (token, id, datos) =>
    apiRequest(`/productos/${id}`, token, { method: "PUT", body: JSON.stringify(datos) }),
  eliminar: (token, id) => apiRequest(`/productos/${id}`, token, { method: "DELETE" }),
};


// ---------------------------------------------------------------------
// SUCURSALES
// Esta sección contiene las funciones relacionadas con la gestión de sucursales en el inventario.
// Proporciona funciones para listar, crear, actualizar y eliminar sucursales.
// ---------------------------------------------------------------------
export const SucursalesAPI = {
  listar: (token) => apiRequest("/sucursales", token),
  crear: (token, datos) =>
    apiRequest("/sucursales", token, { method: "POST", body: JSON.stringify(datos) }),
  actualizar: (token, id, datos) =>
    apiRequest(`/sucursales/${id}`, token, { method: "PUT", body: JSON.stringify(datos) }),
  eliminar: (token, id) => apiRequest(`/sucursales/${id}`, token, { method: "DELETE" }),
};

// ---------------------------------------------------------------------
// USUARIOS
// Esta sección contiene las funciones relacionadas con la gestión de usuarios en el sistema.
// Proporciona funciones para listar, obtener, crear, actualizar y eliminar usuarios, así como para gestionar roles y estados.
// ---------------------------------------------------------------------

export const UsuariosAPI = {
  listar: (token) => apiRequest("/usuarios", token),
  obtener: (token, id) => apiRequest(`/usuarios/${id}`, token),
  roles: (token) => apiRequest("/usuarios/roles", token),

  crear: (token, datos) =>
    apiRequest("/usuarios", token, { method: "POST", body: JSON.stringify(datos) }),

  actualizarPerfil: (token, id, datos) =>
    apiRequest(`/usuarios/${id}/perfil`, token, { method: "PUT", body: JSON.stringify(datos) }),

  cambiarRol: (token, id, rol) =>
    apiRequest(`/usuarios/${id}/rol`, token, { method: "PUT", body: JSON.stringify({ rol }) }),

  // Estos dos son endpoints DISTINTOS en tu backend (no un solo
  // "toggle"): activar falla si ya está activo, desactivar falla si ya
  // está inactivo. El frontend debe llamar al correcto según el estado
  // actual del usuario (ver el botón condicional en UsuariosPage).
  activar: (token, id) => apiRequest(`/usuarios/${id}/estado`, token, { method: "PUT" }),
  desactivar: (token, id) => apiRequest(`/usuarios/${id}`, token, { method: "DELETE" }),
};

// ---------------------------------------------------------------------
// INVENTARIO
// ---------------------------------------------------------------------
export const InventarioAPI = {
  porSucursal: (token, sucursalId) => apiRequest(`/inventarios/${sucursalId}`, token),
  miSucursal: (token) => apiRequest("/inventarios/mi-sucursal", token),
  movimientos: (token) => apiRequest("/inventarios/movimientos", token),
  alertaStockBajo: (token) => apiRequest("/inventarios/alerta-stock-bajo", token),

  // Admin: manda sucursal_id explícito en el "paquete"
  registrarMovimiento: (token, datos) =>
    apiRequest("/inventarios/movimientos", token, { method: "POST", body: JSON.stringify(datos) }),

  // No-admin: el backend ya sabe la sucursal por el token, no se manda sucursal_id
  registrarMovimientoMiSucursal: (token, datos) =>
    apiRequest("/inventarios/movimientos/mi-sucursal", token, { method: "POST", body: JSON.stringify(datos) }),

  ajustarStock: (token, datos) =>
    apiRequest("/inventarios/movimientos/ajustar-stock", token, { method: "POST", body: JSON.stringify(datos) }),
};

// ---------------------------------------------------------------------
// PROVEEDORES
// ---------------------------------------------------------------------
export const ProveedoresAPI = {
  listar: (token) => apiRequest("/proveedores", token),
  crear: (token, datos) =>
    apiRequest("/proveedores", token, { method: "POST", body: JSON.stringify(datos) }),
  
};

// ---------------------------------------------------------------------
// COMPRAS
// ---------------------------------------------------------------------
export const ComprasAPI = {
  listar: (token) => apiRequest("/compras", token),
  crear: (token, datos) =>
    apiRequest("/compras", token, { method: "POST", body: JSON.stringify(datos) }),
  confirmar: (token, id) => apiRequest(`/compras/${id}/confirmar`, token, { method: "POST" }),
  recibir: (token, id) => apiRequest(`/compras/${id}/recibir`, token, { method: "POST" }),
};

// ---------------------------------------------------------------------
// VENTAS
// ---------------------------------------------------------------------
export const VentasAPI = {
  listar: (token) => apiRequest("/ventas", token),
  crear: (token, datos) =>
    apiRequest("/ventas", token, { method: "POST", body: JSON.stringify(datos) }),
};