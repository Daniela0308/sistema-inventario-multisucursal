FROM node:20-alpine

WORKDIR /app

# Copiamos solo el package.json primero (no todo el codigo) para
# aprovechar el "cache" de Docker: si no cambias las dependencias,
# Docker no vuelve a correr npm install en cada build, ahorrando tiempo.
COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Modo DESARROLLO de Vite: recarga en caliente, mensajes de error
# claros en el navegador. Antes de entregar el proyecto final, esto se
# reemplaza por un build de produccion servido con Nginx (mas liviano
# y rapido, pero sin recarga automatica -- no lo necesitas mientras
# aprendes).
CMD ["npm", "run", "dev", "--", "--host"]