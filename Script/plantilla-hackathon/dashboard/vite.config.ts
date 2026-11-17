import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base './' para que el build funcione desde cualquier ruta
export default defineConfig({ base: './', plugins: [react()] })
