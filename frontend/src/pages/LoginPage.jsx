import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

function LoginPage() {
  const { login } = useAuth() // trae SOLO la función login del contexto compartido
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  async function handleSubmit(evento) {
    evento.preventDefault()
    setError("")
    try {
      await login(email, password) // esto actualiza el token/usuario EN EL CONTEXTO
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="contenedor-login">
      <div className="tarjeta-login">
        <h1>OptiPlant</h1>
        <p>Inicia sesión para continuar</p>

        {error && <div className="mensaje-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="campo">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="campo">
            <label>Contraseña</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit">Iniciar sesión</button>
        </form>
      </div>
    </div>
  )
}

export default LoginPage