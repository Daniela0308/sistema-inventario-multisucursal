import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { VentasAPI, ProductosAPI, SucursalesAPI } from '../api'

function VentasPage() {
  const { usuario, token } = useAuth()
  const esAdmin = usuario.rol === "admin_general"

  const [productos, setProductos] = useState([])
  const [sucursales, setSucursales] = useState([])
  const [ventas, setVentas] = useState([])
  const [mensaje, setMensaje] = useState("")

  const [sucursalId, setSucursalId] = useState(esAdmin ? "" : usuario.sucursal_id)

  // Carrito de líneas que se van agregando antes de confirmar la venta
  const [detalles, setDetalles] = useState([])
  const [linea, setLinea] = useState({ producto_id: "", cantidad: "", precio_unitario: "", descuento_pct: 0 })

  // Formulario inline para dar de alta un producto nuevo sin salir de la pantalla
  const [mostrarNuevoProducto, setMostrarNuevoProducto] = useState(false)
  const [formProducto, setFormProducto] = useState({ sku: "", nombre: "", unidad_medida: "unidad", stock_minimo: 5, precio_venta: 0 })

  useEffect(() => {
    cargarProductos()
    SucursalesAPI.listar(token).then(setSucursales).catch((e) => setMensaje(e.message))
    cargarVentas()
  }, [])

  async function cargarProductos() {
    try {
      setProductos(await ProductosAPI.listar(token))
    } catch (error) {
      setMensaje(error.message)
    }
  }

  async function cargarVentas() {
    try {
      setVentas(await VentasAPI.listar(token))
    } catch (error) {
      setMensaje(error.message)
    }
  }

  function nombreProducto(id) {
    const p = productos.find((p) => p.id === id)
    return p ? p.nombre : id
  }

  function nombreSucursal(id) {
    const s = sucursales.find((s) => s.id === id)
    return s ? s.nombre : id
  }

  async function crearProductoInline(evento) {
    evento.preventDefault()
    try {
      const nuevo = await ProductosAPI.crear(token, formProducto)
      setMensaje("Producto creado.")
      setFormProducto({ sku: "", nombre: "", unidad_medida: "unidad", stock_minimo: 5, precio_venta: 0 })
      setMostrarNuevoProducto(false)
      await cargarProductos()
      setLinea({ ...linea, producto_id: nuevo.id })
    } catch (error) {
      setMensaje(error.message)
    }
  }

  function agregarLinea() {
    if (!linea.producto_id || !linea.cantidad) {
      setMensaje("Selecciona un producto y una cantidad.")
      return
    }
    setDetalles([
      ...detalles,
      {
        producto_id: Number(linea.producto_id),
        cantidad: Number(linea.cantidad),
        // si no se especifica precio, el backend usa el precio de catálogo del producto
        precio_unitario: linea.precio_unitario ? Number(linea.precio_unitario) : null,
        descuento_pct: Number(linea.descuento_pct) || 0,
      },
    ])
    setLinea({ producto_id: "", cantidad: "", precio_unitario: "", descuento_pct: 0 })
    setMensaje("")
  }

  function quitarLinea(indice) {
    setDetalles(detalles.filter((_, i) => i !== indice))
  }

  function precioLinea(d) {
    if (d.precio_unitario != null) return d.precio_unitario
    const p = productos.find((p) => p.id === d.producto_id)
    return p ? Number(p.precio_venta) : 0
  }

  function totalCarrito() {
    return detalles.reduce((acc, d) => acc + d.cantidad * precioLinea(d) * (1 - d.descuento_pct / 100), 0)
  }

  async function confirmarVenta() {
    if (!sucursalId) return setMensaje("Selecciona una sucursal.")
    if (detalles.length === 0) return setMensaje("Agrega al menos un producto a la venta.")

    try {
      await VentasAPI.crear(token, {
        sucursal_id: Number(sucursalId),
        detalles: detalles.map(({ producto_id, cantidad, precio_unitario, descuento_pct }) => ({
          producto_id, cantidad, precio_unitario, descuento_pct,
        })),
      })
      setMensaje("Venta registrada. Inventario actualizado.")
      setDetalles([])
      cargarVentas()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  return (
    <div className="pagina">
      <h2>Ventas</h2>
      {mensaje && <div className="mensaje-info">{mensaje}</div>}

      {/* ================= NUEVA VENTA ================= */}
      <div className="form-tarjeta">
        <h3>Nueva venta</h3>

        <div className="fila">
          {esAdmin ? (
            <select value={sucursalId} onChange={(e) => setSucursalId(e.target.value)} required>
              <option value="">-- Sucursal --</option>
              {sucursales.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
            </select>
          ) : (
            <span className="badge">Sucursal: {nombreSucursal(usuario.sucursal_id)}</span>
          )}
        </div>

        <hr />

        <div className="fila">
          <select value={linea.producto_id} onChange={(e) => setLinea({ ...linea, producto_id: e.target.value })}>
            <option value="">-- Producto --</option>
            {productos.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
          </select>
          <button type="button" className="btn-secundario" onClick={() => setMostrarNuevoProducto(!mostrarNuevoProducto)}>
            {mostrarNuevoProducto ? "Cancelar" : "+ Nuevo producto"}
          </button>
          <input type="number" placeholder="Cantidad" value={linea.cantidad} onChange={(e) => setLinea({ ...linea, cantidad: e.target.value })} />
          <input type="number" step="0.01" placeholder="Precio (opcional)" value={linea.precio_unitario} onChange={(e) => setLinea({ ...linea, precio_unitario: e.target.value })} />
          <input type="number" placeholder="Descuento %" value={linea.descuento_pct} onChange={(e) => setLinea({ ...linea, descuento_pct: e.target.value })} />
          <button type="button" onClick={agregarLinea}>Agregar línea</button>
        </div>

        {mostrarNuevoProducto && (
          <form className="fila subformulario" onSubmit={crearProductoInline}>
            <input placeholder="SKU" value={formProducto.sku} onChange={(e) => setFormProducto({ ...formProducto, sku: e.target.value })} required />
            <input placeholder="Nombre" value={formProducto.nombre} onChange={(e) => setFormProducto({ ...formProducto, nombre: e.target.value })} required />
            <input placeholder="Unidad" value={formProducto.unidad_medida} onChange={(e) => setFormProducto({ ...formProducto, unidad_medida: e.target.value })} />
            <input type="number" placeholder="Stock mínimo" value={formProducto.stock_minimo} onChange={(e) => setFormProducto({ ...formProducto, stock_minimo: Number(e.target.value) })} />
            <input type="number" step="0.01" placeholder="Precio venta" value={formProducto.precio_venta} onChange={(e) => setFormProducto({ ...formProducto, precio_venta: Number(e.target.value) })} />
            <button type="submit">Guardar producto</button>
          </form>
        )}

        {detalles.length > 0 && (
          <table>
            <thead><tr><th>Producto</th><th>Cantidad</th><th>Precio</th><th>Desc. %</th><th>Subtotal</th><th></th></tr></thead>
            <tbody>
              {detalles.map((d, i) => (
                <tr key={i}>
                  <td>{nombreProducto(d.producto_id)}</td>
                  <td>{d.cantidad}</td>
                  <td>${precioLinea(d).toLocaleString()}{d.precio_unitario == null && " (catálogo)"}</td>
                  <td>{d.descuento_pct}%</td>
                  <td>${(d.cantidad * precioLinea(d) * (1 - d.descuento_pct / 100)).toLocaleString()}</td>
                  <td><button type="button" className="btn-peligro" onClick={() => quitarLinea(i)}>Quitar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div className="fila fila-final">
          <strong>Total estimado: ${totalCarrito().toLocaleString()}</strong>
          <button type="button" onClick={confirmarVenta} disabled={detalles.length === 0}>
            ¿Ya vas a confirmar la venta? Registrar venta
          </button>
          <span className="ayuda">Puedes seguir agregando líneas antes de confirmar.</span>
        </div>
      </div>

      {/* ================= HISTORIAL DE VENTAS ================= */}
      <h3>Historial de ventas</h3>
      <table>
        <thead><tr><th>ID</th><th>Sucursal</th><th>Total</th><th>Fecha</th></tr></thead>
        <tbody>
          {ventas.map((v) => (
            <tr key={v.id}>
              <td>{v.id}</td>
              <td>{nombreSucursal(v.sucursal_id)}</td>
              <td>${Number(v.total).toLocaleString()}</td>
              <td>{new Date(v.fecha_registro).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default VentasPage
