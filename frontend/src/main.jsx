import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* AuthProvider envuelve TODA la app: por eso App, Navbar, y cada
        pagina pueden usar useAuth() sin que nadie les "pase" el token
        manualmente. */}
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>,
)