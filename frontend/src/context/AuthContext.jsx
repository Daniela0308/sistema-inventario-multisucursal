import { createContext, useContext, useState } from 'react'
import { AuthAPI } from '../api'

/**
 * PROBLEMA que resuelve esto: sin Context, si LoginPage guarda el token
 * en su propio useState, NINGUN otro componente (ProductosPage,
 * Navbar...) podria verlo -- cada componente tiene su estado aislado.
 * Tendrias que pasar el token como "prop" de padre a hijo en cascada
 * por cada componente intermedio, aunque no lo usen ("prop drilling").
 *
 * Context es una "caja compartida": cualquier componente, sin importar
 * que tan anidado este, puede leer o cambiar lo que hay adentro usando
 * el hook useAuth() de mas abajo.
 */
const AuthContext = createContext(null)

/** Envuelve TODA la app (ver main.jsx). Todo lo de adentro puede usar useAuth(). */
export function AuthProvider({ children }) {

  // Recuperamos el token guardado si existe.
  // Asi la sesion NO se pierde al refrescar la pagina.
  const [token, setToken] = useState(
    () => localStorage.getItem('token')
  )

  // Recuperamos tambien los datos del usuario.
  const [usuario, setUsuario] = useState(
    () => {
      const usuarioGuardado = localStorage.getItem('usuario')

      return usuarioGuardado
        ? JSON.parse(usuarioGuardado)
        : null
    }
  )

  async function login(email, password) {
    const datos = await AuthAPI.login(email, password)

    // Guardamos los datos en el estado de React
    setToken(datos.access_token)
    setUsuario(datos.usuario)

    // Y tambien los guardamos en el navegador.
    // Esto permite mantener la sesion despues de un F5.
    localStorage.setItem('token', datos.access_token)
    localStorage.setItem('usuario', JSON.stringify(datos.usuario))
  }

  function logout() {
    // Limpiamos el estado de React
    setToken(null)
    setUsuario(null)

    // Y eliminamos la sesion guardada en el navegador.
    localStorage.removeItem('token')
    localStorage.removeItem('usuario')
  }

  const value = {
    token,
    usuario,
    login,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

/** Hook corto para leer el contexto desde cualquier componente. */
export function useAuth() {
  return useContext(AuthContext)
}