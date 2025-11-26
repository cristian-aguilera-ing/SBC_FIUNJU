"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios, { AxiosError } from "axios";
import { 
    BrainCircuit, ArrowRight, User, Lock, Sparkles, Mail, 
    Eye, EyeOff, Loader2, Check, CheckCircle2 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { NetworkAnimation } from '@/components/auth/NetworkAnimation';
import { Rajdhani, Orbitron } from 'next/font/google';
import backgroundDetails from '@/img/Grupo_09.png';

// Fuentes para el estilo "Cyberpunk/Sci-Fi"
const rajdhani = Rajdhani({ subsets: ['latin'], weight: ['300', '400', '500', '600', '700'], variable: '--font-rajdhani' });
const orbitron = Orbitron({ subsets: ['latin'], weight: ['400', '500', '600', '700'], variable: '--font-orbitron' });

export default function SmartGlassLoginPage() {
  const router = useRouter();
  
  // Estados de UI
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Estados de Formulario
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");

  // Lógica de Toggle entre Login y Registro
  const toggleMode = () => {
    setIsLogin(!isLogin);
    setShowPassword(false);
    // Limpiar errores visuales si los hubiera
  };

  // Manejo del Envío del Formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isLogin) {
        // --- LÓGICA DE LOGIN ---
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await axios.post(
          "/api/sbc/users/login",
          formData,
          { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );

        const { access_token } = response.data;
        localStorage.setItem("sbc_access_token", access_token);
        
        toast.success("Acceso Concedido", { description: "Iniciando sistema..." });
        router.push("/dashboard");

      } else {
        // --- LÓGICA DE REGISTRO ---
        await axios.post(
          "/api/sbc/users/register",
          {
            email: email,
            password: password,
            full_name: fullName,
          }
        );

        toast.success("Identidad Creada", { description: "Tu usuario ha sido registrado. Iniciando sesión..." });
        
        // Auto-login después del registro
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        const loginRes = await axios.post(
            "/api/sbc/users/login",
            formData,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );
        
        localStorage.setItem("sbc_access_token", loginRes.data.access_token);
        router.push("/dashboard");
      }

    } catch (err) {
      const axiosError = err as AxiosError;
      let errorMessage = "Error de conexión con el Núcleo.";
      
      if (axiosError.response) {
        const data = axiosError.response.data as { detail: string };
        errorMessage = data.detail || "Credenciales inválidas.";
      }
      
      toast.error("Acceso Denegado", { description: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`relative w-full h-screen overflow-hidden bg-slate-950 flex items-center justify-center ${rajdhani.variable} ${orbitron.variable} font-sans`}>
      
      {/* --- CAPA DE FONDO (IMAGEN) --- */}
      <div className="absolute inset-0 z-0">
         <img 
             //scr="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop"
            src={backgroundDetails.src} 
            alt="Fondo Grupo 09"
            className="w-full h-full object-cover opacity-40"
         />
         {/* Overlay Oscuro */}
         <div className="absolute inset-0 bg-slate-950/80" />
      </div>

      {/* --- CAPA DE ANIMACIÓN (Red Neuronal) --- */}
      <NetworkAnimation />
      
      {/* --- CAPA UI (Login) --- */}
      <motion.div 
        layout
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-30 w-full max-w-[480px] px-6"
      >
        {/* Brillos Ambientales alrededor de la tarjeta */}
        <div className="absolute -top-20 -left-20 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl opacity-40 mix-blend-screen animate-pulse pointer-events-none" />
        <div className="absolute -bottom-20 -right-20 w-64 h-64 bg-cyan-500/20 rounded-full blur-3xl opacity-40 mix-blend-screen animate-pulse delay-1000 pointer-events-none" />

        {/* Tarjeta de Cristal Principal */}
        <div className="relative backdrop-blur-xl bg-slate-900/40 border border-white/10 rounded-3xl shadow-[0_8px_32px_0_rgba(0,0,0,0.5)] overflow-hidden transition-all duration-500">
          
          {/* Gradiente Sutil Overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
          
          {/* Borde Superior Brillante */}
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent opacity-50" />

          <div className="relative p-8 flex flex-col gap-6">
            
            {/* Cabecera / Logo */}
            <div className="flex flex-col items-center justify-center text-center">
              <div className="relative mb-4">
                  <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full" />
                  <motion.div 
                    layoutId="logo"
                    className="relative w-16 h-16 bg-gradient-to-tr from-cyan-500/10 to-purple-500/10 rounded-2xl border border-white/10 flex items-center justify-center backdrop-blur-md shadow-inner"
                  >
                      <BrainCircuit className="text-cyan-300 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]" size={32} />
                  </motion.div>
                  <div className="absolute -top-1 -right-1">
                      <Sparkles className="text-purple-400 animate-bounce" size={14} />
                  </div>
              </div>
              
              <motion.div
                key={isLogin ? 'login-header' : 'signup-header'}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <h1 className="text-2xl font-display font-bold text-white tracking-wider uppercase">
                  {isLogin ? 'Acceso SBC' : 'Nueva Identidad'}
                </h1>
                <p className="text-slate-400 text-sm mt-1 font-light tracking-wide">
                  {isLogin ? 'Ingrese sus credenciales neuronales' : 'Inicialice su perfil académico'}
                </p>
              </motion.div>
            </div>

            {/* Formulario */}
            <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
              <AnimatePresence mode="popLayout">
                  
                  {/* Nombre Completo (Solo Registro) */}
                  {!isLogin && (
                      <motion.div 
                          key="fullname-field"
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="space-y-1.5 overflow-hidden"
                      >
                          <label className="text-xs font-medium text-slate-400 ml-1 uppercase tracking-widest">Nombre Completo</label>
                          <div className="relative group">
                              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500 group-focus-within:text-cyan-400 transition-colors duration-300">
                                  <User size={18} />
                              </div>
                              <input 
                                  type="text"
                                  required={!isLogin}
                                  value={fullName}
                                  onChange={(e) => setFullName(e.target.value)}
                                  className="w-full bg-black/40 border border-white/10 rounded-xl py-3 pl-11 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:bg-black/60 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all duration-300"
                                  placeholder="Ej: Ana Turing"
                              />
                          </div>
                      </motion.div>
                  )}

                  {/* Email Input */}
                  <motion.div layout key="email-field" className="space-y-1.5">
                      <label className="text-xs font-medium text-slate-400 ml-1 uppercase tracking-widest">Email</label>
                      <div className="relative group">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500 group-focus-within:text-cyan-400 transition-colors duration-300">
                              <Mail size={18} />
                          </div>
                          <input 
                              type="email"
                              required
                              value={email}
                              onChange={(e) => setEmail(e.target.value)}
                              className="w-full bg-black/40 border border-white/10 rounded-xl py-3 pl-11 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:bg-black/60 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all duration-300"
                              placeholder="usuario@fi.unju.edu.ar"
                          />
                      </div>
                  </motion.div>

                  {/* Password Input */}
                  <motion.div layout key="password-field" className="space-y-1.5">
                      <div className="flex justify-between ml-1">
                          <label className="text-xs font-medium text-slate-400 uppercase tracking-widest">Contraseña</label>
                      </div>
                      <div className="relative group">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500 group-focus-within:text-cyan-400 transition-colors duration-300">
                              <Lock size={18} />
                          </div>
                          <input 
                              type={showPassword ? "text" : "password"}
                              required
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              className="w-full bg-black/40 border border-white/10 rounded-xl py-3 pl-11 pr-12 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:bg-black/60 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all duration-300"
                              placeholder="••••••••••••"
                          />
                          <button 
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-500 hover:text-slate-300 transition-colors focus:outline-none"
                          >
                              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                          </button>
                      </div>
                  </motion.div>

                  {/* Confirmación y Términos (Solo Registro) */}
                  {!isLogin && (
                      <motion.div 
                          key="terms-field"
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="space-y-1.5 overflow-hidden"
                      >
                           <div className="pt-2 flex items-start gap-2">
                               <div className="relative flex items-center pt-0.5">
                                   <input type="checkbox" required id="terms" className="peer h-4 w-4 appearance-none border border-slate-600 rounded bg-black/30 checked:bg-cyan-500 checked:border-cyan-500 transition-all cursor-pointer" />
                                   <Check size={12} className="absolute left-0.5 top-1 text-white opacity-0 peer-checked:opacity-100 pointer-events-none" />
                               </div>
                               <label htmlFor="terms" className="text-[10px] text-slate-500 leading-tight cursor-pointer select-none">
                                   Acepto ser parte del sistema de recomendación y comparto mis datos académicos.
                               </label>
                           </div>
                      </motion.div>
                  )}

              </AnimatePresence>

              {/* Botón Inteligente */}
              <button 
                  type="submit"
                  disabled={isLoading}
                  className="relative group mt-4 w-full overflow-hidden rounded-xl bg-white text-black font-bold py-3.5 shadow-[0_0_20px_rgba(255,255,255,0.1)] hover:shadow-[0_0_25px_rgba(6,182,212,0.4)] transition-all duration-300 transform active:scale-[0.98] disabled:opacity-80 disabled:cursor-wait"
              >
                  {/* Gradiente en Hover */}
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  
                  <div className="relative flex items-center justify-center gap-2">
                      {isLoading ? (
                          <Loader2 className="animate-spin text-black group-hover:text-white" size={20} />
                      ) : (
                          <>
                              <span className="group-hover:text-white transition-colors duration-300 uppercase tracking-wider text-sm">
                                  {isLogin ? 'Iniciar Sistema' : 'Crear Cuenta'}
                              </span>
                              <ArrowRight size={18} className="group-hover:text-white group-hover:translate-x-1 transition-all duration-300" />
                          </>
                      )}
                  </div>
              </button>
            </form>

            {/* Switcher de Modo */}
            <div className="text-center pt-2 border-t border-white/5">
              <p className="text-xs text-slate-500">
                  {isLogin ? "¿No tienes identidad?" : "¿Ya eres parte de la red?"}{" "}
                  <button 
                      onClick={toggleMode}
                      className="text-cyan-400 font-medium hover:text-cyan-300 hover:underline transition-colors focus:outline-none ml-1"
                  >
                      {isLogin ? "Regístrate Ahora" : "Inicia Sesión"}
                  </button>
              </p>
            </div>

          </div>
        </div>
      </motion.div>
      
      {/* Footer Branding */}
      <div className="absolute bottom-4 right-6 text-cyan-500/30 text-[10px] font-display tracking-[0.2em] uppercase z-40 select-none animate-pulse">
        SBC Core v.1.0 // Online
      </div>
    </div>
  );
}