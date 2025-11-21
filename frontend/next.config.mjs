/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configuración de Rewrites (Proxy)
  async rewrites() {
    return [
      {
        // Si el navegador pide '/api/sbc/CUALQUIER_COSA'
        source: '/api/sbc/:path*',
        // Next.js lo reenviará al backend. Usamos env var o default a docker service name 'backend'
        // Pero para compatibilidad con desarrollo local sin docker, usaremos localhost si falla
        destination: process.env.BACKEND_URL || 'http://backend:8000/:path*',
      },
    ];
  },
};

export default nextConfig;
