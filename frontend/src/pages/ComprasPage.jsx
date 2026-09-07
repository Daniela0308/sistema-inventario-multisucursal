import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { ComprasAPI, ProveedoresAPI, ProductosAPI, SucursalesAPI } from '../api'

function ComprasPage() {
  const { usuario, token } = useAuth()
  const esAdmin = usuario.rol === "admin_general"
  // admin y gerente pueden confirmar/recibir órdenes (igual que en el backend)
  const puedeGestionar = esAdmin || usuario.rol === "gerente_sucursal"

  const [proveedores, setProveedores] = useState([])
  const [productos, setProductos] = useState([])
  const [sucursales, setSucursales] = useState([])
  const [ordenes, setOrdenes] = useState([])
  const [mensaje, setMensaje] = useState("")

  // Cabecera de la orden que se está armando
  const [proveedorId, setProveedorId] = useState("")
  const [sucursalId, setSucursalId] = useState(esAdmin ? "" : usuario.sucursal_id)
  const [plazoPagoDias, setPlazoPagoDias] = useState("")

  // Carrito de líneas (detalles) que se van agregando antes de crear la orden
  const [detalles, setDetalles] = useState([])
  const [linea, setLinea] = useState({ producto_id: "", cantidad: "", precio_unitario: "", descuento_pct: "" })

  // IDs ya recibidos (persistidos, porque el backend no marca la orden como
  // "recibida") para no dejarla en la lista de pendientes ni permitir un
  // segundo click que duplicaría el ingreso al inventario.
  const [recibidas, setRecibidas] = useState(
    () => JSON.parse(localStorage.getItem("compras_recibidas") || "[]")
  )
  const [procesandoRecepcion, setProcesandoRecepcion] = useState([])

  // Formularios inline para dar de alta un proveedor o producto nuevo sin salir de la pantalla
  const [mostrarNuevoProveedor, setMostrarNuevoProveedor] = useState(false)
  const [formProveedor, setFormProveedor] = useState({ nombre: "", telefono: "", email: "", direccion: "" })

  const [mostrarNuevoProducto, setMostrarNuevoProducto] = useState(false)
  const [formProducto, setFormProducto] = useState({ sku: "", nombre: "", unidad_medida: "unidad", stock_minimo: 5, precio_venta: 0 })

  useEffect(() => {
    cargarProveedores()
    cargarProductos()
    SucursalesAPI.listar(token).then(setSucursales).catch((e) => setMensaje(e.message))
    cargarOrdenes()
  }, [])

  async function cargarProveedores() {
    try {
      setProveedores(await ProveedoresAPI.listar(token))
    } catch (error) {
      setMensaje(error.message)
    }
  }

  async function cargarProductos() {
    try {
      setProductos(await ProductosAPI.listar(token))
    } catch (error) {
      setMensaje(error.message)
    }
  }

  async function cargarOrdenes() {
    try {
      setOrdenes(await ComprasAPI.listar(token))
    } catch (error) {
      setMensaje(error.message)
    }
  }

  function nombreProveedor(id) {
    const p = proveedores.find((p) => p.id === id)
    return p ? p.nombre : id
  }

  function nombreProducto(id) {
    const p = productos.find((p) => p.id === id)
    return p ? p.nombre : id
  }

  function nombreSucursal(id) {
    const s = sucursales.find((s) => s.id === id)
    return s ? s.nombre : id
  }

  async function crearProveedorInline(evento) {
    evento.preventDefault()
    try {
      const nuevo = await ProveedoresAPI.crear(token, formProveedor)
      setMensaje("Proveedor creado.")
      setFormProveedor({ nombre: "", telefono: "", email: "", direccion: "" })
      setMostrarNuevoProveedor(false)
      await cargarProveedores()
      setProveedorId(nuevo.id)
    } catch (error) {
      setMensaje(error.message)
    }
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
    if (!linea.producto_id || !linea.cantidad || !linea.precio_unitario) {
      setMensaje("Selecciona un producto y completa cantidad y precio.")
      return
    }
    setDetalles([
      ...detalles,
      {
        producto_id: Number(linea.producto_id),
        cantidad: Number(linea.cantidad),
        precio_unitario: Number(linea.precio_unitario),
        descuento_pct: Number(linea.descuento_pct) || 0,
      },
    ])
    setLinea({ producto_id: "", cantidad: "", precio_unitario: "", descuento_pct: 0 })
    setMensaje("")
  }

  function quitarLinea(indice) {
    setDetalles(detalles.filter((_, i) => i !== indice))
  }

  function totalCarrito() {
    return detalles.reduce((acc, d) => acc + d.cantidad * d.precio_unitario * (1 - d.descuento_pct / 100), 0)
  }

  async function confirmarCompra() {
    if (!proveedorId) return setMensaje("Selecciona un proveedor.")
    if (!sucursalId) return setMensaje("Selecciona una sucursal.")
    if (detalles.length === 0) return setMensaje("Agrega al menos un producto a la orden.")

    try {
      await ComprasAPI.crear(token, {
        proveedor_id: Number(proveedorId),
        sucursal_id: Number(sucursalId),
        plazo_pago_dias: Number(plazoPagoDias) || 0,
        detalles,
      })
      setMensaje("Orden de compra creada en estado borrador.")
      setProveedorId("")
      setPlazoPagoDias("")
      setDetalles([])
      cargarOrdenes()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  async function confirmarOrden(id) {
    try {
      await ComprasAPI.confirmar(token, id)
      setMensaje(`Orden #${id} confirmada.`)
      cargarOrdenes()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  async function recibirOrden(id) {
    if (procesandoRecepcion.includes(id) || recibidas.includes(id)) return
    setProcesandoRecepcion([...procesandoRecepcion, id])
    try {
      await ComprasAPI.recibir(token, id)
      setMensaje(`Orden #${id} recibida. Inventario actualizado.`)
      const nuevasRecibidas = [...recibidas, id]
      setRecibidas(nuevasRecibidas)
      localStorage.setItem("compras_recibidas", JSON.stringify(nuevasRecibidas))
      cargarOrdenes()
    } catch (error) {
      setMensaje(error.message)
    } finally {
      setProcesandoRecepcion(procesandoRecepcion.filter((i) => i !== id))
    }
  }

  const ordenesBorrador = ordenes.filter((o) => o.estado === "borrador")
  const ordenesConfirmadas = ordenes.filter((o) => o.estado === "confirmada" && !recibidas.includes(o.id))

  return (
    <div className="pagina">
      <h2>Compras</h2>
      {mensaje && <div className="mensaje-info">{mensaje}</div>}

      {/* ================= NUEVA ORDEN DE COMPRA ================= */}
      <div className="form-tarjeta">
        <h3>Nueva orden de compra</h3>

        <div className="fila">
          <select value={proveedorId} onChange={(e) => setProveedorId(e.target.value)} required>
            <option value="">-- Proveedor --</option>
            {proveedores.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
          </select>
          <button type="button" className="btn-secundario" onClick={() => setMostrarNuevoProveedor(!mostrarNuevoProveedor)}>
            {mostrarNuevoProveedor ? "Cancelar" : "+ Nuevo proveedor"}
          </button>

          {esAdmin ? (
            <select value={sucursalId} onChange={(e) => setSucursalId(e.target.value)} required>
              <option value="">-- Sucursal --</option>
              {sucursales.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
            </select>
          ) : (
            <span className="badge">Sucursal: {nombreSucursal(usuario.sucursal_id)}</span>
          )}

          <input
            type="number"
            min="0"
            placeholder="Plazo de pago (días)"
            value={plazoPagoDias}
            onChange={(e) => setPlazoPagoDias(e.target.value)}
          />
        </div>

        {mostrarNuevoProveedor && (
          <form className="fila subformulario" onSubmit={crearProveedorInline}>
            <input placeholder="Nombre" value={formProveedor.nombre} onChange={(e) => setFormProveedor({ ...formProveedor, nombre: e.target.value })} required />
            <input placeholder="Teléfono" value={formProveedor.telefono} onChange={(e) => setFormProveedor({ ...formProveedor, telefono: e.target.value })} required />
            <input type="email" placeholder="Email" value={formProveedor.email} onChange={(e) => setFormProveedor({ ...formProveedor, email: e.target.value })} required />
            <input placeholder="Dirección" value={formProveedor.direccion} onChange={(e) => setFormProveedor({ ...formProveedor, direccion: e.target.value })} />
            <button type="submit">Guardar proveedor</button>
          </form>
        )}

        <hr />

        <div className="fila">
          <select value={linea.producto_id} onChange={(e) => setLinea({ ...linea, producto_id: e.target.value })}>
            <option value="">-- Producto --</option>
            {productos.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
          </select>
          <button type="button" className="btn-secundario" onClick={() => setMostrarNuevoProducto(!mostrarNuevoProducto)}>
            {mostrarNuevoProducto ? "Cancelar" : "+ Nuevo producto"}
          </button>
          <input type="number" min="1" placeholder="Cantidad" value={linea.cantidad} onChange={(e) => setLinea({ ...linea, cantidad: e.target.value })} />
          <input type="number" step="0.01" min="0" placeholder="Precio unitario" value={linea.precio_unitario} onChange={(e) => setLinea({ ...linea, precio_unitario: e.target.value })} />
          <input type="number" min="0" max="100" placeholder="Descuento %" value={linea.descuento_pct} onChange={(e) => setLinea({ ...linea, descuento_pct: e.target.value })} />
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
                  <td>${d.precio_unitario.toLocaleString()}</td>
                  <td>{d.descuento_pct}%</td>
                  <td>${(d.cantidad * d.precio_unitario * (1 - d.descuento_pct / 100)).toLocaleString()}</td>
                  <td><button type="button" className="btn-peligro" onClick={() => quitarLinea(i)}>Quitar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div className="fila fila-final">
          <strong>Total estimado: ${totalCarrito().toLocaleString()}</strong>
          <button type="button" onClick={confirmarCompra} disabled={detalles.length === 0}>
            ¿Ya vas a confirmar la compra? Crear orden
          </button>
          <span className="ayuda">Puedes seguir agregando líneas antes de crear la orden.</span>
        </div>
      </div>

      {/* ================= COMPRAS PENDIENTES (solo admin/gerente) ================= */}
      {puedeGestionar && (
        <>
          <h3>Compras pendientes por confirmar</h3>
          <table>
            <thead><tr><th>ID</th><th>Proveedor</th><th>Sucursal</th><th>Fecha</th><th>Acciones</th></tr></thead>
            <tbody>
              {ordenesBorrador.map((o) => (
                <tr key={o.id}>
                  <td>{o.id}</td>
                  <td>{nombreProveedor(o.proveedor_id)}</td>
                  <td>{nombreSucursal(o.sucursal_id)}</td>
                  <td>{new Date(o.fecha_registro).toLocaleString()}</td>
                  <td><button onClick={() => confirmarOrden(o.id)}>Confirmar</button></td>
                </tr>
              ))}
              {ordenesBorrador.length === 0 && <tr><td colSpan="5">No hay órdenes pendientes.</td></tr>}
            </tbody>
          </table>

          <h3>Compras confirmadas por recibir</h3>
          <table>
            <thead><tr><th>ID</th><th>Proveedor</th><th>Sucursal</th><th>Fecha</th><th>Acciones</th></tr></thead>
            <tbody>
              {ordenesConfirmadas.map((o) => (
                <tr key={o.id}>
                  <td>{o.id}</td>
                  <td>{nombreProveedor(o.proveedor_id)}</td>
                  <td>{nombreSucursal(o.sucursal_id)}</td>
                  <td>{new Date(o.fecha_registro).toLocaleString()}</td>
                  <td>
                    <button onClick={() => recibirOrden(o.id)} disabled={procesandoRecepcion.includes(o.id)}>
                      {procesandoRecepcion.includes(o.id) ? "Recibiendo..." : "Recibir (actualiza inventario)"}
                    </button>
                  </td>
                </tr>
              ))}
              {ordenesConfirmadas.length === 0 && <tr><td colSpan="5">No hay órdenes confirmadas por recibir.</td></tr>}
            </tbody>
          </table>
        </>
      )}

      {/* ================= HISTORIAL COMPLETO ================= */}
      <h3>Historial de órdenes de compra</h3>
      <table>
        <thead><tr><th>ID</th><th>Proveedor</th><th>Sucursal</th><th>Estado</th><th>Fecha</th></tr></thead>
        <tbody>
          {ordenes.map((o) => (
            <tr key={o.id}>
              <td>{o.id}</td>
              <td>{nombreProveedor(o.proveedor_id)}</td>
              <td>{nombreSucursal(o.sucursal_id)}</td>
              <td><span className={`badge badge-${o.estado}`}>{o.estado}</span></td>
              <td>{new Date(o.fecha_registro).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ComprasPage
