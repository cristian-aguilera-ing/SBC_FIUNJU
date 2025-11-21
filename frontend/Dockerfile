# Usa una imagen oficial de Node.js
FROM node:20-alpine

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de manifiesto del proyecto
# (Esto solo se ejecuta si package.json cambia, ahorrando tiempo)
COPY package.json package-lock.json* ./

# Instala las dependencias
RUN npm install

# Copia el resto del código del frontend
COPY . .

# Expone el puerto de Next.js
EXPOSE 3000

# El comando para iniciar el servidor de desarrollo
CMD ["npm", "run", "dev"]