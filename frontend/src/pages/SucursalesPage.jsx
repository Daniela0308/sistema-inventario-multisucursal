import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { SucursalesAPI } from '../api'

function SucursalesPage() {
  const { token } = useAuth()
  const [sucursales, setSucursales] = useState([])
  const [mensaje, setMensaje] = useState("")
  const [editandoId, setEditandoId] = useState(null)
  const [form, setForm] = useState({ nombre: "", ciudad: "", direccion: "" })

  useEffect(() => { cargarSucursales() }, [])

  async function cargarSucursales() {
    try {
      setSucursales(await SucursalesAPI.listar(token))
    } catch (error) {
      setMensaje(error.message)
    }
  }

  function actualizarCampo(campo, valor) {
    setForm({ ...form, [campo]: valor })
  }

  async function handleSubmit(evento) {
    evento.preventDefault()
    try {
      if (editandoId) {
        await SucursalesAPI.actualizar(token, editandoId, form)
      } else {
        await SucursalesAPI.crear(token, form)
      }
      setEditandoId(null)
      setForm({ nombre: "", ciudad: "", direccion: "" })
      cargarSucursales()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  function editar(sucursal) {
    setEditandoId(sucursal.id)
    setForm({ nombre: sucursal.nombre, ciudad: sucursal.ciudad, direccion: sucursal.direccion || "" })
  }

  async function eliminar(id) {
    if (!confirm("¿Eliminar esta sucursal?")) return
    try {
      await SucursalesAPI.eliminar(token, id)
      cargarSucursales()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  return (
    <div className="pagina">
      <h2>Sucursales</h2>
      {mensaje && <div className="mensaje-info">{mensaje}</div>}

      <form className="form-tarjeta" onSubmit={handleSubmit}>
        <div className="fila">
          <input placeholder="Nombre" value={form.nombre} onChange={(e) => actualizarCampo("nombre", e.target.value)} required />
          <input placeholder="Ciudad" value={form.ciudad} onChange={(e) => actualizarCampo("ciudad", e.target.value)} required />
          <input placeholder="Dirección" value={form.direccion} onChange={(e) => actualizarCampo("direccion", e.target.value)} />
          <button type="submit">{editandoId ? "Actualizar" : "Crear"}</button>
        </div>
      </form>

      <table>
        <thead><tr><th>ID</th><th>Nombre</th><th>Ciudad</th><th>Dirección</th><th>Acciones</th></tr></thead>
        <tbody>
          {sucursales.map((s) => (
            <tr key={s.id}>
              <td>{s.id}</td><td>{s.nombre}</td><td>{s.ciudad}</td><td>{s.direccion}</td>
              <td>
                <button onClick={() => editar(s)}>Editar</button>
                <button className="btn-peligro" onClick={() => eliminar(s.id)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default SucursalesPage