import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// host: true permite que el contenedor de Docker exponga el servidor
// de desarrollo hacia afuera (sin esto, Vite solo escucharia dentro
// del contenedor, invisible desde tu navegador).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
  },
})