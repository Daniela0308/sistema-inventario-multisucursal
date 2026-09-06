import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { ProductosAPI } from '../api'

function ProductosPage() {
  const { token } = useAuth() // el token ya no viene de props ni de fetch propio, sale del contexto

  const [productos, setProductos] = useState([])
  const [mensaje, setMensaje] = useState("")
  const [editandoId, setEditandoId] = useState(null) // null = creando, con valor = editando

  const [form, setForm] = useState({
    sku: "", nombre: "", descripcion: "", unidad_medida: "unidad", stock_minimo: 5, precio_venta: 0,
  })

  /**
   * useEffect: código que corre DESPUÉS de que el componente se dibuja.
   * El array [] al final significa "ejecuta esto UNA SOLA VEZ, cuando
   * el componente aparece por primera vez" (equivale a lo que hacías
   * con cargarProductos() suelto al final del JS vanilla). Sin el
   * useEffect, el fetch se ejecutaria en cada re-render sin control.
   */
  useEffect(() => {
    cargarProductos()
  }, [])

  async function cargarProductos() {
    try {
      const datos = await ProductosAPI.listar(token)
      setProductos(datos)
    } catch (error) {
      setMensaje(error.message)
    }
  }

  function actualizarCampo(campo, valor) {
    setForm({ ...form, [campo]: valor }) // "...form" copia los campos existentes, sobreescribe solo uno
  }

  async function handleSubmit(evento) {
    evento.preventDefault()
    try {
      if (editandoId) {
        await ProductosAPI.actualizar(token, editandoId, form)
        setMensaje("Producto actualizado.")
      } else {
        await ProductosAPI.crear(token, form)
        setMensaje("Producto creado.")
      }
      limpiarFormulario()
      cargarProductos()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  function editar(producto) {
    setEditandoId(producto.id)
    setForm({
      sku: producto.sku,
      nombre: producto.nombre,
      descripcion: producto.descripcion || "",
      unidad_medida: producto.unidad_medida,
      stock_minimo: producto.stock_minimo,
      precio_venta: producto.precio_venta,
    })
  }

  function limpiarFormulario() {
    setEditandoId(null)
    setForm({ sku: "", nombre: "", descripcion: "", unidad_medida: "unidad", stock_minimo: 5, precio_venta: 0 })
  }

  async function eliminar(id) {
    if (!confirm("¿Desactivar este producto?")) return
    try {
      await ProductosAPI.eliminar(token, id)
      cargarProductos()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  return (
    <div className="pagina">
      <h2>Productos</h2>
      {mensaje && <div className="mensaje-info">{mensaje}</div>}

      <form className="form-tarjeta" onSubmit={handleSubmit}>
        <div className="fila">
          <input placeholder="SKU" value={form.sku} onChange={(e) => actualizarCampo("sku", e.target.value)} required />
          <input placeholder="Nombre" value={form.nombre} onChange={(e) => actualizarCampo("nombre", e.target.value)} required />
          <input placeholder="Descripción" value={form.descripcion} onChange={(e) => actualizarCampo("descripcion", e.target.value)} />
        </div>
        <div className="fila">
          <input placeholder="Unidad" value={form.unidad_medida} onChange={(e) => actualizarCampo("unidad_medida", e.target.value)} />
          <input type="number" placeholder="Stock mínimo" value={form.stock_minimo} onChange={(e) => actualizarCampo("stock_minimo", Number(e.target.value))} />
          <input type="number" step="0.01" placeholder="Precio" value={form.precio_venta} onChange={(e) => actualizarCampo("precio_venta", Number(e.target.value))} />
          <button type="submit">{editandoId ? "Actualizar" : "Crear"}</button>
          {editandoId && <button type="button" className="btn-secundario" onClick={limpiarFormulario}>Cancelar</button>}
        </div>
      </form>

      <table>
        <thead>
          <tr><th>ID</th><th>SKU</th><th>Nombre</th><th>Stock mín.</th><th>Precio</th><th>Acciones</th></tr>
        </thead>
        <tbody>
          {productos.map((producto) => (
            <tr key={producto.id}>
              <td>{producto.id}</td>
              <td>{producto.sku}</td>
              <td>{producto.nombre}</td>
              <td>{producto.stock_minimo}</td>
              <td>${Number(producto.precio_venta).toLocaleString()}</td>
              <td>
                <button onClick={() => editar(producto)}>Editar</button>
                <button className="btn-peligro" onClick={() => eliminar(producto.id)}>Desactivar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ProductosPage