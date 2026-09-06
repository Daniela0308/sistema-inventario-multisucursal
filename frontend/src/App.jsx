import { useState } from 'react'
import { useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import Navbar from './components/Navbar'
import ProductosPage from './pages/ProductosPage'
import SucursalesPage from './pages/SucursalesPage'
import InventarioPage from './pages/InventarioPage'
import UsuariosPage from './pages/UsuariosPage'
import './App.css'

/**
 * En vez de una libreria de rutas (react-router), usamos un simple
 * useState con el "nombre" de la pagina activa. Es menos flexible que
 * una libreria real (no cambia la URL del navegador, por ejemplo), pero
 * para tu proyecto es suficiente y evita aprender una herramienta mas.
 */
function App() {
  const { token } = useAuth() // si no hay token, mostramos el login
  const [paginaActual, setPaginaActual] = useState("productos")

  if (!token) {
    return <LoginPage />
  }

  function renderizarPagina() {
    switch (paginaActual) {
      case "productos": return <ProductosPage />
      case "sucursales": return <SucursalesPage />
      case "inventario": return <InventarioPage />
      case "usuarios": return <UsuariosPage />
      default: return <ProductosPage />
    }
  }

  return (
    <div>
      <Navbar paginaActual={paginaActual} onCambiarPagina={setPaginaActual} />
      <main className="contenido-app">
        {renderizarPagina()}
      </main>
    </div>
  )
}

export default App