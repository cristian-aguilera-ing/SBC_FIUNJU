// Este es el archivo: frontend/src/app/page.tsx (La Bienvenida)
"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation'; // <-- Importa el Router

export default function WelcomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Comprueba si el token existe al cargar la página
    const token = localStorage.getItem("sbc_access_token");
    if (token) {
      // --- ¡CORRECCIÓN! ---
      // Si hay token, redirige inmediatamente al dashboard
      router.push("/dashboard");
      // --------------------
    } else {
      // Si no hay token, deja de cargar y muestra la bienvenida
      setIsLoading(false);
    }
  }, [router]); // Añade 'router' a las dependencias

  // Muestra "Cargando..." mientras comprueba el token
  if (isLoading) {
    return <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">Comprobando sesión...</main>
  }

  // Si no está cargando y no hay token, muestra la bienvenida
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">
      <div className="w-full max-w-2xl p-8 text-center bg-gray-800 rounded-lg shadow-lg">
        
        <h1 className="text-4xl font-bold mb-4">
          Bienvenido al Sistema Basado en Conocimiento
        </h1>
        <p className="text-xl text-gray-400 mb-8">
          Tu asistente personal para estrategias de cursada y exámenes finales en la FI-UNJU.
        </p>

        {/* Muestra los botones de Login/Registro */}
        <div className="flex gap-4 justify-center">
          <Link href="/login">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white text-lg p-6">
              Iniciar Sesión
            </Button>
          </Link>
          <Link href="/register">
            <Button variant="outline" className="bg-gray-700 text-white text-lg p-6">
              Registrarse
            </Button>
          </Link>
        </div>

      </div>
    </main>
  );
}