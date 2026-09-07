import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { InventarioAPI, SucursalesAPI, ProductosAPI } from '../api'

function InventarioPage() {

  // Contexto de autenticación y rol del usuario actual.
  const { usuario, token } = useAuth()
  const esAdmin = usuario.rol === "admin_general"

  // Estados locales para manejar sucursales, productos, inventario, movimientos y mensajes.
  const [sucursales, setSucursales] = useState([])
  const [productos, setProductos] = useState([])
  const [inventario, setInventario] = useState([])
  const [movimientos, setMovimientos] = useState([])
  const [mensaje, setMensaje] = useState("")

  // Para el admin: qué sucursal está mirando (elige libremente).
  // Para el no-admin: arranca viendo la SUYA, pero puede activar
  // "viendoOtra" para consultar cualquier otra (requisito 2.1).
  const [sucursalSeleccionada, setSucursalSeleccionada] = useState("")
  const [viendoOtra, setViendoOtra] = useState(false)
  // Estado para manejar el formulario de registro de movimientos.
  const [form, setForm] = useState({
    sucursal_id: "", producto_id: "", tipo: "ingreso_ajuste", cantidad: "", motivo: "",
  })
  // Efectos para cargar datos iniciales: sucursales, productos e inventario según el rol del usuario.
  useEffect(() => {
    SucursalesAPI.listar(token).then(setSucursales).catch((e) => setMensaje(e.message))
    ProductosAPI.listar(token).then(setProductos).catch((e) => setMensaje(e.message))
    if (esAdmin) cargarHistorial() // el historial de movimientos es exclusivo del admin
  }, [])

  // Al entrar, si NO es admin, carga directamente SU inventario
  // (mi-sucursal) sin pedirle que elija nada.
  useEffect(() => {
    if (!esAdmin && !viendoOtra) cargarMiSucursal()
  }, [])

  // Si el admin (o alguien viendo "otra sucursal") elige una sucursal
  // distinta, recarga el inventario de esa sucursal puntual.
  useEffect(() => {
    if (sucursalSeleccionada) cargarPorSucursal(sucursalSeleccionada)
  }, [sucursalSeleccionada])
  // Funciones para cargar inventario según la sucursal seleccionada o la sucursal del usuario, y para cargar el historial de movimientos (solo admin).
  async function cargarMiSucursal() {
    try {
      setInventario(await InventarioAPI.miSucursal(token))
    } catch (error) {
      setMensaje(error.message)
    }
  }
  // Función para cargar inventario de la sucursal del usuario autenticado.
  async function cargarPorSucursal(id) {
    try {
      setInventario(await InventarioAPI.porSucursal(token, id))
    } catch (error) {
      setMensaje(error.message)
    }
  }
  // Función para cargar el historial de movimientos (solo admin).
  async function cargarHistorial() {
    try {
      setMovimientos(await InventarioAPI.movimientos(token))
    } catch (error) {
      setMensaje(error.message)
    }
  }
  // Función auxiliar para obtener el nombre de un producto a partir de su ID.
  function nombreProducto(id) {
    const p = productos.find((p) => p.id === id)
    return p ? p.nombre : id
  }

  function nombreSucursal(id) {
    const s = sucursales.find((s) => s.id === id)
    return s ? s.nombre : id
  }
  // Función para registrar un nuevo movimiento de inventario, diferenciando entre admin y no-admin.

  async function registrarMovimiento(evento) {
    evento.preventDefault()
    // Prepara los datos base del movimiento de inventario.
    try {
      const datosBase = {
        producto_id: Number(form.producto_id),
        tipo: form.tipo,
        cantidad: Number(form.cantidad),
        motivo: form.motivo,
      }
      // Si es admin, se añade la sucursal seleccionada al paquete de datos.
      if (esAdmin) {
        await InventarioAPI.registrarMovimiento(token, {
          ...datosBase,
          sucursal_id: Number(form.sucursal_id),
        })
      } else {
        await InventarioAPI.registrarMovimientoMiSucursal(token, datosBase)
      }
      // Actualiza el inventario y el historial según el rol del usuario y la sucursal seleccionada.
      setMensaje("Movimiento registrado correctamente.")
      setForm({ sucursal_id: "", producto_id: "", tipo: "ingreso_ajuste", cantidad: "", motivo: "" })
      // Refresca la vista del inventario y el historial de movimientos según el rol y la sucursal seleccionada.
      if (esAdmin && sucursalSeleccionada) cargarPorSucursal(sucursalSeleccionada)
      if (!esAdmin) cargarMiSucursal()
      if (esAdmin) cargarHistorial()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  return (
    <div className="pagina">
      <h2>Inventario</h2>
      {mensaje && <div className="mensaje-info">{mensaje}</div>}

      {/* ================= SECCIÓN: CONSULTAR STOCK ================= */}
      <div className="form-tarjeta">
        {esAdmin ? (
          <div className="campo">
            <label>Sucursal a consultar (administrador ve cualquiera)</label>
            <select value={sucursalSeleccionada} onChange={(e) => setSucursalSeleccionada(e.target.value)}>
              <option value="">-- Selecciona una sucursal --</option>
              {sucursales.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
            </select>
          </div>
        ) : (
          <>
            <div className="campo">
              <label>
                <input
                  type="checkbox"
                  checked={viendoOtra}
                  onChange={(e) => {
                    setViendoOtra(e.target.checked)
                    if (!e.target.checked) {
                      setSucursalSeleccionada("")
                      cargarMiSucursal()
                    }
                  }}
                />
                {" "}Consultar el inventario de otra sucursal de la red
              </label>
            </div>

            {viendoOtra && (
              <div className="campo">
                <select value={sucursalSeleccionada} onChange={(e) => setSucursalSeleccionada(e.target.value)}>
                  <option value="">-- Selecciona una sucursal --</option>
                  {sucursales.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                </select>
              </div>
            )}
          </>
        )}
      </div>

      <table>
        <thead><tr><th>Producto</th><th>Cantidad</th><th>Costo promedio</th></tr></thead>
        <tbody>
          {inventario.map((item) => (
            <tr key={item.id}>
              <td>{nombreProducto(item.producto_id)}</td>
              <td>{item.cantidad}</td>
              <td>${Number(item.costo_promedio).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* ================= SECCIÓN: REGISTRAR MOVIMIENTO ================= */}
      <h3>Registrar movimiento</h3>
      <form className="form-tarjeta" onSubmit={registrarMovimiento}>
        <div className="fila">
          {esAdmin && (
            <select
              value={form.sucursal_id}
              onChange={(e) => setForm({ ...form, sucursal_id: e.target.value })}
              required
            >
              <option value="">-- Sucursal --</option>
              {sucursales.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
            </select>
          )}

          <select
            value={form.producto_id}
            onChange={(e) => setForm({ ...form, producto_id: e.target.value })}
            required
          >
            <option value="">-- Producto --</option>
            {productos.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
          </select>

          <select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
            <option value="ingreso_ajuste">Ingreso (ajuste)</option>
            <option value="ingreso_devolucion">Ingreso (devolución)</option>
            <option value="retiro_ajuste">Retiro (ajuste)</option>
            <option value="retiro_merma">Retiro (merma)</option>
          </select>

          <input
            type="number"
            placeholder="Cantidad"
            value={form.cantidad}
            onChange={(e) => setForm({ ...form, cantidad: e.target.value })}
            required
          />
          <input
            placeholder="Motivo"
            value={form.motivo}
            onChange={(e) => setForm({ ...form, motivo: e.target.value })}
          />
          <button type="submit">Registrar</button>
        </div>
      </form>

      {/* ================= SECCIÓN: HISTORIAL COMPLETO (solo admin) ================= */}
      {esAdmin && (
        <>
          <h3>Historial de movimientos</h3>
          <table>
            <thead>
              <tr><th>Fecha</th><th>Sucursal</th><th>Producto</th><th>Tipo</th><th>Cantidad</th><th>Motivo</th></tr>
            </thead>
            <tbody>
              {movimientos.map((m) => (
                <tr key={m.id}>
                  <td>{new Date(m.fecha_registro).toLocaleString()}</td>
                  <td>{nombreSucursal(m.sucursal_id)}</td>
                  <td>{nombreProducto(m.producto_id)}</td>
                  <td>{m.tipo}</td>
                  <td>{m.cantidad}</td>
                  <td>{m.motivo}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  )
}

export default InventarioPage