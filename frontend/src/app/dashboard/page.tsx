"use client";

import { useRouter } from 'next/navigation';
import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { toast } from "sonner";
// Imports UI combinados (Lógica + Estética)
import { Loader2Icon, Lightbulb, User as UserIcon, LogOut, LayoutDashboard } from "lucide-react";
import { motion } from 'framer-motion';
import { NetworkAnimation } from '@/components/auth/NetworkAnimation';
import { Rajdhani, Orbitron } from 'next/font/google';
// import backgroundDetails from '@/img/Grupo_09.png';

// Tipos
import {
  User, MateriaOntology, MateriaPerfil, Alerta, PlanCursadaRecomendado, PlanExamenRecomendado
} from "@/types";

// Componentes
import AlertsPanel from "@/components/dashboard/AlertsPanel";
import PlanResults from "@/components/dashboard/PlanResults";
import ExamenStrategy from "@/components/dashboard/ExamenStrategy";
import QuickActions from "@/components/dashboard/QuickActions";
import TopicResults from "@/components/dashboard/TopicResults";

// Fuentes (UI Preservada)
const rajdhani = Rajdhani({ subsets: ['latin'], weight: ['300', '400', '500', '600', '700'], variable: '--font-rajdhani' });
const orbitron = Orbitron({ subsets: ['latin'], weight: ['400', '500', '600', '700'], variable: '--font-orbitron' });

export default function Home() {
  const router = useRouter();

  // --- LÓGICA TRASPLANTADA DESDE page.tsx (ORIGINAL) ---
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [materiasPerfil, setMateriasPerfil] = useState<MateriaPerfil[]>([]);

  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [isLoadingAlerts, setIsLoadingAlerts] = useState(true);

  // Vistas de Resultados
  const [planRecomendado, setPlanRecomendado] = useState<PlanCursadaRecomendado | null>(null);
  const [planExamenes, setPlanExamenes] = useState<PlanExamenRecomendado | null>(null);
  const [showTopicResults, setShowTopicResults] = useState(false);

  const [isLoadingPlan, setIsLoadingPlan] = useState(false);
  const [isLoadingExamenes, setIsLoadingExamenes] = useState(false);

  useEffect(() => {
    const storedToken = localStorage.getItem("sbc_access_token");
    if (storedToken) {
      setToken(storedToken);
      fetchUserProfile(storedToken);
    } else {
      router.push("/login");
    }
  }, [router]);

  // Efecto de alertas (Lógica Original: depende de token e isLoading)
  useEffect(() => {
    if (token && !isLoading) {
      const fetchAlertas = async () => {
        setIsLoadingAlerts(true);
        try {
          const alertasResponse = await axios.get<Alerta[]>(
            "/api/sbc/recomendacion/alerta-riesgos",
            { headers: { Authorization: `Bearer ${token}` } }
          );
          setAlertas(alertasResponse.data);
        } catch (error) {
          console.error("Error al cargar alertas", error);
        }
        setIsLoadingAlerts(false);
      };
      fetchAlertas();
    }
  }, [token, isLoading]);

  const fetchUserProfile = async (token: string) => {
    try {
      const [userResponse, ontologyResponse] = await Promise.all([
        axios.get<User>("/api/sbc/users/me", { headers: { Authorization: `Bearer ${token}` } }),
        axios.get<MateriaOntology[]>("/api/sbc/ontologia/materias", { headers: { Authorization: `Bearer ${token}` } })
      ]);

      const userData = userResponse.data;
      const allMateriasData = ontologyResponse.data;
      setUser(userData);

      const enrichedMaterias = userData.materias_cursadas.map(materia => {
        const ontologyData = allMateriasData.find(om => om.uri === materia.materia_uri);
        return { ...materia, label: ontologyData?.label || materia.materia_uri.split('#')[1] };
      });
      setMateriasPerfil(enrichedMaterias);
      setIsLoading(false);
    } catch (error) {
      console.error("Error al cargar datos del dashboard", error);
      handleLogout();
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("sbc_access_token");
    setUser(null); setToken(null); setMateriasPerfil([]);
    setAlertas([]);
    setPlanRecomendado(null);
    setPlanExamenes(null);
    setShowTopicResults(false);
    setIsLoading(true);
    router.push("/login");
  }

  const clearResults = () => {
    setPlanRecomendado(null);
    setPlanExamenes(null);
    setShowTopicResults(false);
  }

  const handleGetPlanCursada = async () => {
    if (!token) return;
    setIsLoadingPlan(true);
    clearResults();
    try {
      const response = await axios.get<PlanCursadaRecomendado>(
        "/api/sbc/recomendacion/plan-cursada-optimo",
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPlanRecomendado(response.data);
    } catch (error) {
      toast.error("Error al generar el plan");
    }
    setIsLoadingPlan(false);
  };

  const handleGetPlanExamenes = async () => {
    if (!token) return;
    setIsLoadingExamenes(true);
    clearResults();
    try {
      const response = await axios.get<PlanExamenRecomendado>(
        "/api/sbc/recomendacion/finales-prioritarios",
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPlanExamenes(response.data);
    } catch (error) {
      toast.error("Error al generar estrategia");
    }
    setIsLoadingExamenes(false);
  };

  const handleGetTopics = () => {
    clearResults();
    setShowTopicResults(true);
  }

  // Cálculo de estado derivado (Lógica Original)
  const isAnyLoading = isLoadingPlan || isLoadingExamenes;
  // --- FIN LÓGICA TRASPLANTADA ---

  // --- INTERFAZ VISUAL (COPIA PRESERVADA) ---
  if (isLoading || !user) {
    return (
      <div className={`relative w-full h-screen overflow-hidden bg-slate-950 flex items-center justify-center ${rajdhani.variable} ${orbitron.variable} font-sans`}>
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-black to-slate-900" />
        <NetworkAnimation />
        <div className="relative z-30 flex flex-col items-center gap-4 backdrop-blur-md p-10 rounded-2xl border border-cyan-500/20 bg-slate-900/40 shadow-[0_0_50px_rgba(6,182,212,0.1)]">
          <Loader2Icon className="h-12 w-12 text-cyan-400 animate-spin drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
          <p className="text-cyan-100 font-display tracking-[0.3em] uppercase text-sm animate-pulse mt-2">Sincronizando Núcleo...</p>
        </div>
      </div>
    );
  }

  return (
    // Importante: bg-slate-950 base, pero el contenido interno será transparente
    <div className={`relative min-h-screen w-full bg-slate-950 ${rajdhani.variable} ${orbitron.variable} font-sans selection:bg-cyan-500/30`}>

      {/* --- CAPA 0: FONDO FIJO (Gradients) --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Fondo base */}
        <div className="absolute inset-0 bg-slate-950" />

        {/* Nebulosas de color */}
        <div className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] bg-purple-900/20 rounded-full blur-[120px] opacity-60" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[60vw] h-[60vw] bg-cyan-900/20 rounded-full blur-[120px] opacity-60" />
      </div>

      {/* --- CAPA 1: ANIMACIÓN --- */}
      <div className="fixed inset-0 z-10 pointer-events-none">
        <NetworkAnimation />
      </div>

      {/* --- CAPA 2: CONTENIDO PRINCIPAL --- */}
      {/* bg-transparent es clave aquí para no tapar el fondo fixed */}
      <div className="relative z-30 min-h-screen overflow-y-auto overflow-x-hidden bg-transparent">
        <div className="container mx-auto px-4 py-4 md:py-6 lg:px-8 max-w-7xl">

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="w-full"
          >
            {/* TARJETA GLASS CONTAINER */}
            <div className="relative backdrop-blur-xl bg-slate-900/20 border border-white/5 rounded-3xl shadow-[0_8px_32px_0_rgba(0,0,0,0.5)] min-h-[85vh] overflow-hidden">

              {/* Gradiente Sutil Overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />

              {/* Borde Brillante Superior */}
              <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent opacity-50" />

              <div className="p-4 md:p-6">

                {/* HEADER */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-6 border-b border-white/10 pb-6">
                  <div className="flex items-center gap-5">
                    <div className="p-3 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-2xl border border-white/10 shadow-[0_0_15px_rgba(6,182,212,0.2)] hidden md:block">
                      <LayoutDashboard className="text-cyan-300 w-8 h-8 drop-shadow-md" />
                    </div>
                    <div>
                      <h1 className="text-3xl md:text-4xl font-display font-bold text-white tracking-wider uppercase drop-shadow-lg">
                        Panel de Control
                      </h1>
                      <p className="text-slate-300 mt-1 font-light text-sm md:text-base tracking-wide">
                        Bienvenido, <span className="text-cyan-300 font-medium text-shadow-sm">{user.full_name || user.email}</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-3 w-full md:w-auto">
                    <Link href="/perfil" className="flex-1 md:flex-none">
                      <Button variant="ghost" className="w-full h-11 bg-white/5 text-cyan-100 border border-white/10 hover:bg-cyan-500/20 hover:text-white hover:border-cyan-400/50 transition-all duration-300 backdrop-blur-sm">
                        <UserIcon className="mr-2 h-4 w-4" /> Mi Perfil
                      </Button>
                    </Link>
                    <Button variant="ghost" onClick={handleLogout} className="flex-1 md:flex-none h-11 bg-white/5 text-slate-300 border border-white/10 hover:bg-red-500/20 hover:text-red-300 hover:border-red-400/50 transition-all duration-300 backdrop-blur-sm">
                      <LogOut className="mr-2 h-4 w-4" /> Salir
                    </Button>
                  </div>
                </div>

                {/* GRID PRINCIPAL */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                  {/* COLUMNA IZQUIERDA: Sidebar */}
                  <div className="lg:col-span-4 xl:col-span-3 space-y-6 flex flex-col">

                    {/* 1. ALERTAS */}
                    <AlertsPanel alertas={alertas} isLoading={isLoadingAlerts} />

                    {/* 2. ACCIONES RÁPIDAS (Siempre visibles) */}
                    <div className="backdrop-blur-md bg-white/[0.02] rounded-2xl border border-white/5 p-4 shadow-lg relative overflow-hidden">
                      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-purple-500/5 pointer-events-none" />
                      <QuickActions
                        handleGetPlanCursada={handleGetPlanCursada}
                        handleGetPlanExamenes={handleGetPlanExamenes}
                        handleGetTopics={handleGetTopics}
                        isLoadingPlan={isLoadingPlan}
                        isLoadingExamenes={isLoadingExamenes}
                        isAnyLoading={isAnyLoading}
                      />
                    </div>
                  </div>

                  {/* COLUMNA DERECHA: Resultados */}
                  <div className="lg:col-span-8 xl:col-span-9 space-y-6">
                    <div className="min-h-[400px]">

                      {/* Placeholder de espera */}
                      {!planRecomendado && !planExamenes && !showTopicResults && !isAnyLoading && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="h-full flex flex-col items-center justify-center p-12 border border-dashed border-white/10 rounded-3xl bg-white/[0.01]"
                        >
                          <div className="p-6 bg-slate-800/50 rounded-full mb-6 border border-white/5 shadow-[0_0_30px_rgba(0,0,0,0.5)]">
                            <Lightbulb className="w-12 h-12 text-slate-500" />
                          </div>
                          <p className="font-display tracking-widest text-xl text-slate-400 uppercase">Sistema en Espera</p>
                          <p className="text-base text-slate-500 mt-2 font-light text-center max-w-md leading-relaxed">
                            Selecciona una instrucción en el panel lateral para iniciar el motor de inferencia.
                          </p>
                        </motion.div>
                      )}

                      {/* Spinner de Carga de Resultados */}
                      {isAnyLoading && (
                        <div className="h-[400px] flex flex-col justify-center items-center p-12 bg-white/[0.01] rounded-3xl border border-white/5">
                          <Loader2Icon className="mb-6 h-12 w-12 animate-spin text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.5)]" />
                          <p className="animate-pulse font-display tracking-[0.2em] text-cyan-400/80 uppercase text-sm">Procesando Datos...</p>
                        </div>
                      )}

                      {/* Resultados Renderizados */}
                      <div className="space-y-6">
                        <PlanResults plan={planRecomendado} isLoading={isLoadingPlan} />
                        <ExamenStrategy plan={planExamenes} isLoading={isLoadingExamenes} />
                        {showTopicResults && (
                          <TopicResults materiasPerfil={materiasPerfil} token={token} />
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          <div className="mt-8 text-center text-slate-600/50 text-[10px] font-display tracking-[0.4em] uppercase select-none">
            SBC Core v.1.0 // System Operational
          </div>
        </div>
      </div>
    </div>
  );
}