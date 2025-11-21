"use client";

import { useState, FormEvent } from "react";
import axios, { AxiosError } from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link"; // Para enlazar a la página de registro
import { useRouter } from 'next/navigation'; 


export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // 1. Prepara los datos para el formulario (OAuth2PasswordRequestForm)
      //    FastAPI espera los datos como 'form-data', no como JSON.
      const formData = new URLSearchParams();
      formData.append('username', email); // FastAPI espera 'username' para el email
      formData.append('password', password);

      // 2. Llama al endpoint de login (a través del proxy)
      const response = await axios.post(
        "/api/sbc/users/login", // La ruta del proxy
        formData, // Envía los datos como form-data
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      // 3. ¡Éxito! Guarda el token en el localStorage del navegador
      const { access_token } = response.data;
      localStorage.setItem("sbc_access_token", access_token);
      
      setIsLoading(false);
      
      // Muestra un mensaje y redirige a la página principal
      router.push("/dashboard");

    } catch (err) {
      // 4. Si hay un error...
      const axiosError = err as AxiosError;
      if (axiosError.response) {
        // El backend respondió con un error (ej. "Email o contraseña incorrectos")
        const errorData = axiosError.response.data as { detail: string };
        setError(errorData.detail || "Error al iniciar sesión.");
      } else {
        // Error de red (el backend no responde)
        setError("No se pudo conectar al servidor. Inténtalo de nuevo.");
      }
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-center">Iniciar Sesión</h1>
        <p className="text-center text-gray-400">
          Ingresa a tu cuenta del SBC
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email" className="text-gray-300">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 bg-gray-700 border-gray-600 text-white"
            />
          </div>
          <div>
            <Label htmlFor="password" className="text-gray-300">Contraseña</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 bg-gray-700 border-gray-600 text-white"
            />
          </div>
          
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Ingresando..." : "Iniciar Sesión"}
          </Button>
        </form>

        {error && (
          <div className="p-3 text-center text-red-300 bg-red-900/50 rounded-md">
            {error}
          </div>
        )}
        
        <div className="text-center text-sm text-gray-400">
          ¿No tienes una cuenta?{" "}
          <Link href="/register" className="font-medium text-blue-400 hover:underline">
            Regístrate
          </Link>
        </div>

      </div>
    </main>
  );
}