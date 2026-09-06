import { useAuth } from '../context/AuthContext'

/**
 * paginaActual/onCambiarPagina son "props": datos que el componente
 * PADRE (App.jsx) le pasa a este componente HIJO. Es la forma normal
 * en que los componentes de React se comunican -- de padre a hijo.
 */
function Navbar({ paginaActual, onCambiarPagina }) {
  const { usuario, logout } = useAuth()

  const paginas = [
    { id: "productos", label: "Productos" },
    { id: "sucursales", label: "Sucursales" },
    { id: "inventario", label: "Inventario" },
    { id: "usuarios", label: "Usuarios" },
  ]

  return (
    <nav className="navbar">
      <div className="navbar-marca">OptiPlant</div>

      <div className="navbar-links">
        {paginas.map((pagina) => (
          <button
            key={pagina.id}
            className={paginaActual === pagina.id ? "nav-link activo" : "nav-link"}
            onClick={() => onCambiarPagina(pagina.id)}
          >
            {pagina.label}
          </button>
        ))}
      </div>

      <div className="navbar-usuario">
        <span>{usuario?.nombre} ({usuario?.rol})</span>
        <button className="btn-secundario" onClick={logout}>Cerrar sesión</button>
      </div>
    </nav>
  )
}

export default Navbar