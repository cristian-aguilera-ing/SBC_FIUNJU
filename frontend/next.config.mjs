/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configuración de Rewrites (Proxy)
  async rewrites() {
    return [
      {
        // Si el navegador pide '/api/sbc/CUALQUIER_COSA'
        source: '/api/sbc/:path*',
        // Next.js lo reenviará a 'http://backend:8000/CUALQUIER_COSA'
        destination: 'http://backend:8000/:path*',
      },
    ];
  },
};

export default nextConfig;