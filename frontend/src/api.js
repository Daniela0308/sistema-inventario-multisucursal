const API_URL = "http://localhost:8000";

async function apiRequest(path, token, options = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const respuesta = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => ({}));
    throw new Error(cuerpo.detail || `Error ${respuesta.status}`);
  }
  if (respuesta.status === 204) return null;
  return respuesta.json();
}

export const AuthAPI = {
  login: (email, password) =>
    apiRequest("/auth/login", null, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
};

export const ProductosAPI = {
  listar: (token) => apiRequest("/productos", token),
  crear: (token, datos) =>
    apiRequest("/productos", token, { method: "POST", body: JSON.stringify(datos) }),
  actualizar: (token, id, datos) =>
    apiRequest(`/productos/${id}`, token, { method: "PUT", body: JSON.stringify(datos) }),
  eliminar: (token, id) => apiRequest(`/productos/${id}`, token, { method: "DELETE" }),
};

export const SucursalesAPI = {
  listar: (token) => apiRequest("/sucursales", token),
  crear: (token, datos) =>
    apiRequest("/sucursales", token, { method: "POST", body: JSON.stringify(datos) }),
  actualizar: (token, id, datos) =>
    apiRequest(`/sucursales/${id}`, token, { method: "PUT", body: JSON.stringify(datos) }),
  eliminar: (token, id) => apiRequest(`/sucursales/${id}`, token, { method: "DELETE" }),
};

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