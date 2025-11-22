"use client";

import { useRouter } from 'next/navigation';
import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { toast } from "sonner"; 
import { Loader2Icon, Lightbulb, User as UserIcon } from "lucide-react";

import {
  User, MateriaOntology, MateriaPerfil, Alerta, PlanCursadaRecomendado, PlanExamenRecomendado
} from "@/types";

import AlertsPanel from "@/components/dashboard/AlertsPanel";
import PlanResults from "@/components/dashboard/PlanResults";
import ExamenStrategy from "@/components/dashboard/ExamenStrategy";
import QuickActions from "@/components/dashboard/QuickActions";
import TopicConsultation from "@/components/dashboard/TopicConsultation";

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true); 
  const [materiasPerfil, setMateriasPerfil] = useState<MateriaPerfil[]>([]);
  
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [isLoadingAlerts, setIsLoadingAlerts] = useState(true);

  const [planRecomendado, setPlanRecomendado] = useState<PlanCursadaRecomendado | null>(null);
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);
  const [planExamenes, setPlanExamenes] = useState<PlanExamenRecomendado | null>(null);
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
        axios.get<User>("/api/sbc/users/me", { headers: { Authorization: `Bearer ${token}` }}),
        axios.get<MateriaOntology[]>("/api/sbc/ontologia/materias", { headers: { Authorization: `Bearer ${token}` }})
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
    setIsLoading(true);
    router.push("/login");
  }

  const handleGetPlanCursada = async () => {
    if (!token) return;
    setIsLoadingPlan(true);
    try {
      const response = await axios.get<PlanCursadaRecomendado>(
        "/api/sbc/recomendacion/plan-cursada-optimo",
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setPlanRecomendado(response.data);
      setPlanExamenes(null);
    } catch (error) {
      toast.error("Error al generar el plan");
    }
    setIsLoadingPlan(false);
  };

  const handleGetPlanExamenes = async () => {
    if (!token) return;
    setIsLoadingExamenes(true);
    try {
      const response = await axios.get<PlanExamenRecomendado>(
        "/api/sbc/recomendacion/finales-prioritarios",
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setPlanExamenes(response.data);
      setPlanRecomendado(null);
    } catch (error) {
      toast.error("Error al generar estrategia");
    }
    setIsLoadingExamenes(false);
  };
  
  if (isLoading || !user) {
    return <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">Cargando datos del usuario...</main>
  }

  const isAnyLoading = isLoadingPlan || isLoadingExamenes;

  return (
    <main className="flex min-h-screen flex-col items-center p-8 md:p-24 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 animate-gradient text-white">
      <div className="w-full max-w-4xl p-8 bg-gray-800/90 backdrop-blur-md rounded-lg shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
          <div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
              Bienvenido, {user.full_name || user.email}
            </h1>
            <p className="text-gray-400">Este es tu panel de control inteligente.</p>
          </div>
          <div className="flex gap-2">
             <Link href="/perfil">
                <Button variant="secondary" className="bg-blue-900/50 text-blue-200 border border-blue-800 hover:bg-blue-900 transition-all hover:scale-105">
                     <UserIcon className="mr-2 h-4 w-4"/> Mi Perfil
                </Button>
             </Link>
            <Button variant="outline" onClick={handleLogout} className="bg-gray-700 text-white border-gray-600 hover:bg-gray-600 transition-all hover:scale-105">Cerrar Sesión</Button>
          </div>
        </div>

        {/* Contenido */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Columna Izquierda: Acciones Rápidas */}
          <div className="lg:col-span-1 space-y-6">

            <AlertsPanel alertas={alertas} isLoading={isLoadingAlerts} />

            <QuickActions
              handleGetPlanCursada={handleGetPlanCursada}
              handleGetPlanExamenes={handleGetPlanExamenes}
              isLoadingPlan={isLoadingPlan}
              isLoadingExamenes={isLoadingExamenes}
              isAnyLoading={isAnyLoading}
            />

            <TopicConsultation materiasPerfil={materiasPerfil} token={token} />

          </div>

          {/* Columna Derecha: Resultados */}
          <div className="lg:col-span-2 space-y-6">

               {/* Placeholder inicial */}
               {!planRecomendado && !planExamenes && !isAnyLoading && (
                   <div className="h-full flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-700 rounded-lg text-gray-500 bg-gray-800/50">
                       <Lightbulb className="w-12 h-12 mb-4 opacity-20" />
                       <p className="text-center">Selecciona una opción a la izquierda para comenzar.</p>
                   </div>
               )}

              {/* Loading State */}
              {isAnyLoading && (
                <div className="flex flex-col justify-center items-center p-12 text-gray-400 bg-gray-800/50 rounded-lg">
                    <Loader2Icon className="mb-3 h-8 w-8 animate-spin text-blue-500" />
                    <p className="animate-pulse">Analizando perfil y ontología...</p>
                </div>
              )}

              {/* Resultados */}
              <PlanResults plan={planRecomendado} isLoading={isLoadingPlan} />

              <ExamenStrategy plan={planExamenes} isLoading={isLoadingExamenes} />

          </div>
        </div>
      </div>
    </main>
  );
}
