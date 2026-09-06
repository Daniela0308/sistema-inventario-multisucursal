import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { UsuariosAPI, SucursalesAPI } from '../api'

function UsuariosPage() {
  const { token } = useAuth()
  const [usuarios, setUsuarios] = useState([])
  const [sucursales, setSucursales] = useState([])
  const [roles, setRoles] = useState([])
  const [mensaje, setMensaje] = useState("")

  const [form, setForm] = useState({
    nombre: "", email: "", password: "", rol: "operador_inventario", sucursal_id: "",
  })

  const [editandoId, setEditandoId] = useState(null)
  const [formPerfil, setFormPerfil] = useState({ nombre: "", email: "", sucursal_id: "" })

  useEffect(() => {
    cargarUsuarios()
    UsuariosAPI.roles(token).then(setRoles).catch((e) => setMensaje(e.message))
    SucursalesAPI.listar(token).then(setSucursales).catch((e) => setMensaje(e.message))
  }, [])

  async function cargarUsuarios() {
    try {
      setUsuarios(await UsuariosAPI.listar(token))
    } catch (error) {
      setMensaje(error.message)
    }
  }

  async function handleCrear(evento) {
    evento.preventDefault()
    try {
      await UsuariosAPI.crear(token, {
        ...form,
        sucursal_id: form.sucursal_id ? Number(form.sucursal_id) : null,
      })
      setMensaje("Usuario creado.")
      setForm({ nombre: "", email: "", password: "", rol: "operador_inventario", sucursal_id: "" })
      cargarUsuarios()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  function iniciarEdicionPerfil(usuario) {
    setEditandoId(usuario.id)
    setFormPerfil({
      nombre: usuario.nombre,
      email: usuario.email,
      sucursal_id: usuario.sucursal_id || "",
    })
  }

  async function guardarPerfil(id) {
    try {
      await UsuariosAPI.actualizarPerfil(token, id, {
        ...formPerfil,
        sucursal_id: formPerfil.sucursal_id ? Number(formPerfil.sucursal_id) : null,
      })
      setMensaje("Perfil actualizado.")
      setEditandoId(null)
      cargarUsuarios()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  async function cambiarRol(id, nuevoRol) {
    try {
      await UsuariosAPI.cambiarRol(token, id, nuevoRol)
      setMensaje("Rol actualizado.")
      cargarUsuarios()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  // Son dos endpoints DISTINTOS en el backend (no un único "toggle"),
  // así que el botón que se muestra depende del estado actual.
  async function alternarEstado(usuario) {
    try {
      if (usuario.activo) {
        await UsuariosAPI.desactivar(token, usuario.id)
        setMensaje(`${usuario.nombre} desactivado.`)
      } else {
        await UsuariosAPI.activar(token, usuario.id)
        setMensaje(`${usuario.nombre} activado.`)
      }
      cargarUsuarios()
    } catch (error) {
      setMensaje(error.message)
    }
  }

  return (
    <div className="pagina">
      <h2>Usuarios</h2>
      {mensaje && <div className="mensaje-info">{mensaje}</div>}

      <form className="form-tarjeta" onSubmit={handleCrear}>
        <div className="fila">
          <input placeholder="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required />
          <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <input type="password" placeholder="Contraseña" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        </div>
        <div className="fila">
          <select value={form.rol} onChange={(e) => setForm({ ...form, rol: e.target.value })}>
            {roles.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
          <select value={form.sucursal_id} onChange={(e) => setForm({ ...form, sucursal_id: e.target.value })}>
            <option value="">Sin sucursal (admin)</option>
            {sucursales.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
          </select>
          <button type="submit">Crear usuario</button>
        </div>
      </form>

      <table>
        <thead>
          <tr><th>ID</th><th>Nombre</th><th>Email</th><th>Sucursal</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr>
        </thead>
        <tbody>
          {usuarios.map((u) => (
            <tr key={u.id}>
              {editandoId === u.id ? (
                <>
                  <td>{u.id}</td>
                  <td><input value={formPerfil.nombre} onChange={(e) => setFormPerfil({ ...formPerfil, nombre: e.target.value })} /></td>
                  <td><input value={formPerfil.email} onChange={(e) => setFormPerfil({ ...formPerfil, email: e.target.value })} /></td>
                  <td>
                    <select value={formPerfil.sucursal_id} onChange={(e) => setFormPerfil({ ...formPerfil, sucursal_id: e.target.value })}>
                      <option value="">Sin sucursal</option>
                      {sucursales.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                    </select>
                  </td>
                  <td>{u.rol}</td>
                  <td>{u.activo ? "Activo" : "Inactivo"}</td>
                  <td>
                    <button onClick={() => guardarPerfil(u.id)}>Guardar</button>
                    <button className="btn-secundario" onClick={() => setEditandoId(null)}>Cancelar</button>
                  </td>
                </>
              ) : (
                <>
                  <td>{u.id}</td>
                  <td>{u.nombre}</td>
                  <td>{u.email}</td>
                  <td>{u.sucursal_id ? sucursales.find((s) => s.id === u.sucursal_id)?.nombre : "—"}</td>
                  <td>
                    <select value={u.rol} onChange={(e) => cambiarRol(u.id, e.target.value)}>
                      {roles.map((r) => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </td>
                  <td>{u.activo ? "Activo" : "Inactivo"}</td>
                  <td>
                    <button onClick={() => iniciarEdicionPerfil(u)}>Editar</button>
                    <button
                      className={u.activo ? "btn-peligro" : ""}
                      onClick={() => alternarEstado(u)}
                    >
                      {u.activo ? "Desactivar" : "Activar"}
                    </button>
                  </td>
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default UsuariosPage