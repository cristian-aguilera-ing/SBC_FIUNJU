"use client";

import { useState, FormEvent } from "react";
import axios, { AxiosError } from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Esta función se llama cuando se envía el formulario
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault(); // Evita que la página se recargue
    setError(null);
    setSuccess(null);
    setIsLoading(true);

    try {
      // 1. Llama al proxy de Next.js (que reenvía a FastAPI)
      const response = await axios.post(
        "/api/sbc/users/register", // La ruta del proxy
        {
          email: email,
          password: password,
          full_name: fullName,
        }
      );

      // 2. Si todo va bien...
      console.log(response.data);
      setSuccess(`¡Usuario ${response.data.email} creado con éxito!`);
      setIsLoading(false);
      
      // (Aquí, en el futuro, podrías redirigir al login)
      // router.push("/login");

    } catch (err) {
      // 3. Si hay un error...
      const axiosError = err as AxiosError;
      if (axiosError.response) {
        // El backend respondió con un error (ej. "Email ya existe")
        const errorData = axiosError.response.data as { detail: string };
        setError(errorData.detail || "Error al registrar el usuario.");
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
        <h1 className="text-3xl font-bold text-center">Crear una Cuenta</h1>
        <p className="text-center text-gray-400">
          Ingresa tus datos para registrarte en el SBC
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="fullName" className="text-gray-300">Nombre Completo (Opcional)</Label>
            <Input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 bg-gray-700 border-gray-600 text-white"
            />
          </div>
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
            {isLoading ? "Creando cuenta..." : "Registrarse"}
          </Button>
        </form>

        {/* --- Mensajes de Éxito o Error --- */}
        {success && (
          <div className="p-3 text-center text-green-300 bg-green-900/50 rounded-md">
            {success}
          </div>
        )}
        {error && (
          <div className="p-3 text-center text-red-300 bg-red-900/50 rounded-md">
            {error}
          </div>
        )}

      </div>
    </main>
  );
}