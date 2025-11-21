"use client";

import { useRouter } from 'next/navigation';
import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { toast } from "sonner"; 
import { Loader2Icon, TriangleAlertIcon, LockKeyhole, Lightbulb, BookOpen, AlertCircle, MapPin, BrainCircuit, User as UserIcon } from "lucide-react";

// --- Tipos ---
interface MateriaOntology { uri: string; label: string; }
interface UserMateria { id: number; materia_uri: string; estado: string; }
interface MateriaPerfil extends UserMateria { label: string; }
interface User {
  id: number;
  email: string;
  full_name: string | null;
  materias_cursadas: UserMateria[]; 
}
interface ConsejoResponse { consejos: string[]; }
interface TopicoOntology { uri: string; label: string; }

enum TipoAlerta {
  RIESGO_REGULARIDAD = "riesgo_regularidad",
  CUELLO_DE_BOTELLA = "cuello_de_botella",
  SOBRECARGA = "sobrecarga"
}
interface Alerta {
  tipo: TipoAlerta;
  mensaje: string;
  materia_uri: string | null;
  materia_label: string | null;
}

interface MateriaRecomendada {
  uri: string;
  label: string;
  score: number;
  año: number;
  dificultad: number;
  desbloquea_count: number;
  creditos_otorgados: number;
}

interface ArquetipoInfo {
    nombre: string;
    color: string;
    consejos: string[];
}

interface PlanCursadaRecomendado {
  plan_recomendado: MateriaRecomendada[];
  materias_omitidas: MateriaRecomendada[];
  arquetipo: ArquetipoInfo; // Agregado
  consejos_adicionales: string[];
}

interface MateriaExamenRecomendada {
  uri: string;
  label: string;
  dificultad_examen_label: string;
  dificultad_examen_valor: number;
  modalidades: string[];
  esta_habilitada: boolean;
  motivo_bloqueo: string | null;
  correlativas_pendientes: string[];
  consejo_personalizado: string | null;
}
interface PlanExamenRecomendado {
  plan_recomendado: MateriaExamenRecomendada[];
  consejos_adicionales: string[];
}

// --- Componentes de Widget Dinámico ---
const WidgetDinamico = ({ arquetipo }: { arquetipo: ArquetipoInfo }) => {
    const color = arquetipo.color;

    switch (color) {
        case "red": // Superviviente
            return (
                <div className="border-l-4 border-red-500 bg-red-900/20 p-4 rounded mb-4">
                    <h4 className="text-red-400 font-bold mb-2 flex items-center gap-2"><BatteryLowIcon className="w-5 h-5"/> Modo Ahorro Energía</h4>
                    <p className="text-xs text-gray-300">Tu lista de tareas está simplificada al máximo. Solo lo esencial.</p>
                </div>
            );
        case "orange": // Malabarista
            return (
                <div className="border-l-4 border-orange-500 bg-orange-900/20 p-4 rounded mb-4">
                    <h4 className="text-orange-400 font-bold mb-2 flex items-center gap-2"><ClockIcon className="w-5 h-5"/> Horario Familiar Bloqueado</h4>
                    <p className="text-xs text-gray-300">Recuerda: De 18hs a 21hs es tiempo familiar. No intentes estudiar ahí.</p>
                </div>
            );
        case "yellow": // Guerrero
             return (
                <div className="border-l-4 border-yellow-500 bg-yellow-900/20 p-4 rounded mb-4">
                    <h4 className="text-yellow-400 font-bold mb-2 flex items-center gap-2"><BusIcon className="w-5 h-5"/> Calculadora de Viaje</h4>
                    <p className="text-xs text-gray-300">Has ganado +5hs de estudio esta semana aprovechando el viaje en bus.</p>
                </div>
            );
        case "green": // Equilibrado
             return (
                <div className="border-l-4 border-green-500 bg-green-900/20 p-4 rounded mb-4">
                    <h4 className="text-green-400 font-bold mb-2 flex items-center gap-2"><TrendingUpIcon className="w-5 h-5"/> Progreso Constante</h4>
                    <div className="w-full bg-gray-700 rounded-full h-2.5 mb-1">
                        <div className="bg-green-500 h-2.5 rounded-full" style={{ width: '70%' }}></div>
                    </div>
                    <p className="text-xs text-gray-300">Mantienes un ritmo excelente. ¡Sigue así!</p>
                </div>
            );
        case "blue": // Ermitaño
             return (
                <div className="border-l-4 border-blue-500 bg-blue-900/20 p-4 rounded mb-4">
                    <h4 className="text-blue-400 font-bold mb-2 flex items-center gap-2"><WifiOffIcon className="w-5 h-5"/> Modo Offline Ready</h4>
                    <p className="text-xs text-gray-300">Todo tu material está listo para descargar. No dependas de la red.</p>
                </div>
            );
        case "violet": // Heredero
             return (
                <div className="border-l-4 border-violet-500 bg-violet-900/20 p-4 rounded mb-4">
                    <h4 className="text-violet-400 font-bold mb-2 flex items-center gap-2"><RocketIcon className="w-5 h-5"/> Planificador Acelerado</h4>
                    <p className="text-xs text-gray-300">Estás adelantando materias del próximo año. ¡Excelente ritmo!</p>
                </div>
            );
        case "brown": // Padre/Madre
             return (
                <div className="border-l-4 border-amber-700 bg-amber-900/20 p-4 rounded mb-4">
                    <h4 className="text-amber-500 font-bold mb-2 flex items-center gap-2"><TargetIcon className="w-5 h-5"/> Micro-Objetivos</h4>
                    <ul className="text-xs text-gray-300 list-disc pl-4">
                        <li>Leer 10 págs (15 min)</li>
                        <li>Resumir unidad 1 (20 min)</li>
                    </ul>
                </div>
            );
        default:
            return null;
    }
}

// Iconos simples para no depender de librerías externas pesadas si faltan
const BatteryLowIcon = (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="16" height="10" x="2" y="7" rx="2" ry="2"/><line x1="22" x2="22" y1="11" y2="13"/></svg>
const ClockIcon = (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
const BusIcon = (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 6v6"/><path d="M15 6v6"/><path d="M2 12h19.6"/><path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3"/><circle cx="7" cy="18" r="2"/><path d="M9 18h5"/><circle cx="16" cy="18" r="2"/></svg>
const TrendingUpIcon = (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
const WifiOffIcon = (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="2" x2="22" y1="2" y2="22"/><path d="M8.5 16.5a5 5 0 0 1 7 0"/><path d="M2 8.82a15 15 0 0 1 4.17-2.68"/><path d="M10.66 5c1.34-.33 2.76-.33 4.1 0"/><path d="M16.85 8.65A14.98 14.98 0 0 1 22 12"/><path d="M5 12a10 10 0 0 1 4.24-2.83"/></svg>
const RocketIcon = (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>
const TargetIcon = (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>


export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true); 
  const [materiasPerfil, setMateriasPerfil] = useState<MateriaPerfil[]>([]);
  
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [isLoadingAlerts, setIsLoadingAlerts] = useState(true);

  const [isLoadingAdvice, setIsLoadingAdvice] = useState(false); 
  const [materiaActiva, setMateriaActiva] = useState<MateriaPerfil | null>(null);
  const [tipoDeConsejo, setTipoDeConsejo] = useState<'cursada' | 'examen' | null>(null);
  const [topicos, setTopicos] = useState<TopicoOntology[]>([]);
  const [consejoGeneral, setConsejoGeneral] = useState<string[] | null>(null);
  const [consejoEspecifico, setConsejoEspecifico] = useState<string[] | null>(null);

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
    setConsejoGeneral(null); setConsejoEspecifico(null);
    setAlertas([]); 
    setPlanRecomendado(null);
    setPlanExamenes(null);
    setIsLoading(true);
    router.push("/login");
  }

  const clearAllResults = () => {
    setConsejoGeneral(null); 
    setConsejoEspecifico(null);
    setMateriaActiva(null);
    setTopicos([]);
    // No limpiamos el plan recomendado si ya lo tenemos, para que persista en pantalla
    // setPlanRecomendado(null);
    // setPlanExamenes(null);
  }

  const handleGetPlanCursada = async () => {
    if (!token) return;
    setIsLoadingPlan(true);
    // clearAllResults(); // Opcional
    try {
      const response = await axios.get<PlanCursadaRecomendado>(
        "/api/sbc/recomendacion/plan-cursada-optimo",
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setPlanRecomendado(response.data);
      // Limpiar otros paneles para dar foco
      setPlanExamenes(null);
      setConsejoGeneral(null);
      setConsejoEspecifico(null);
    } catch (error) {
      toast.error("Error al generar el plan");
    }
    setIsLoadingPlan(false);
  };

  const handleGetPlanExamenes = async () => {
    if (!token) return;
    setIsLoadingExamenes(true);
    // clearAllResults();
    try {
      const response = await axios.get<PlanExamenRecomendado>(
        "/api/sbc/recomendacion/finales-prioritarios",
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setPlanExamenes(response.data);
       // Limpiar otros paneles para dar foco
      setPlanRecomendado(null);
      setConsejoGeneral(null);
      setConsejoEspecifico(null);
    } catch (error) {
      toast.error("Error al generar estrategia");
    }
    setIsLoadingExamenes(false);
  };
  
  const handleGetGeneralAdvice = async (tipo: 'cursada' | 'examen') => {
    if (!token) return;
    setIsLoadingAdvice(true);
    clearAllResults();
    const endpoint = tipo === 'cursada' ? '/api/sbc/consejos/cursada/general' : '/api/sbc/consejos/examen/general';
    try {
      const response = await axios.get<ConsejoResponse>(
        endpoint,
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setConsejoGeneral(response.data.consejos);
    } catch (error) {
      toast.error("Error al pedir consejo general");
    }
    setIsLoadingAdvice(false);
  };

  const handleSelectMateria = async (materia: MateriaPerfil, tipo: 'cursada' | 'examen') => {
    if (!token) return;
    setIsLoadingAdvice(true);
    clearAllResults();
    setMateriaActiva(materia); 
    setTipoDeConsejo(tipo); 
    try {
      const response = await axios.get<TopicoOntology[]>(
        `/api/sbc/ontologia/materias/topicos`,
        { 
          headers: { Authorization: `Bearer ${token}` },
          params: { materia_uri: materia.materia_uri, tipo: tipo }
        }
      );
      setTopicos(response.data); 
    } catch (error) {
      toast.error("Error", { description: "No se pudieron encontrar tópicos." });
    }
    setIsLoadingAdvice(false);
  };

  const handleSelectTopico = async (topico: TopicoOntology) => {
    if (!token || !materiaActiva || !tipoDeConsejo) return;
    setIsLoadingAdvice(true);
    const endpoint = tipoDeConsejo === 'cursada' 
      ? '/api/sbc/consejos/cursada/especifico'
      : '/api/sbc/consejos/examen/especifico';
    const body = {
      materia_uris_request: [materiaActiva.materia_uri], 
      topico_uri: topico.uri 
    };
    try {
      const response = await axios.post<ConsejoResponse>(
        endpoint, body, { headers: { Authorization: `Bearer ${token}` }}
      );
      setConsejoEspecifico(response.data.consejos);
    } catch (error) {
      toast.error("Error al pedir consejo");
    } finally {
      setIsLoadingAdvice(false);
      setMateriaActiva(null);
      setTopicos([]);
    }
  };
  
  if (isLoading || !user) {
    return <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">Cargando datos del usuario...</main>
  }

  const isAnyLoading = isLoadingAdvice || isLoadingPlan || isLoadingExamenes;

  return (
    <main className="flex min-h-screen flex-col items-center p-8 md:p-24 bg-gray-900 text-white">
      <div className="w-full max-w-4xl p-8 bg-gray-800 rounded-lg shadow-lg">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
          <div>
            <h1 className="text-2xl font-bold">Bienvenido, {user.full_name || user.email}</h1>
            <p className="text-gray-400">Este es tu panel de control inteligente.</p>
          </div>
          <div className="flex gap-2">
             <Link href="/perfil">
                <Button variant="secondary" className="bg-blue-900/50 text-blue-200 border border-blue-800 hover:bg-blue-900">
                     <UserIcon className="mr-2 h-4 w-4"/> Mi Perfil
                </Button>
             </Link>
            <Button variant="outline" onClick={handleLogout} className="bg-gray-700 text-white border-gray-600 hover:bg-gray-600">Cerrar Sesión</Button>
          </div>
        </div>

        {/* Contenido */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Columna Izquierda: Acciones Rápidas */}
          <div className="lg:col-span-1 space-y-6">
                {/* Alertas */}
                {isLoadingAlerts && (
                    <div className="p-4 bg-gray-700 rounded-lg text-center text-gray-400 text-xs">
                    <Loader2Icon className="h-4 w-4 animate-spin inline-block" /> Buscando alertas...
                    </div>
                )}
                {!isLoadingAlerts && alertas.length > 0 && (
                    <div className="p-4 bg-yellow-900/50 text-yellow-200 rounded-lg space-y-3 border border-yellow-700 animate-in fade-in-0">
                    <div className="flex items-center gap-2">
                        <TriangleAlertIcon className="h-5 w-5 text-yellow-300 flex-shrink-0" />
                        <h3 className="text-sm font-bold uppercase tracking-wider">Atención</h3>
                    </div>
                    <ul className="list-disc pl-4 space-y-1">
                        {alertas.map((alerta, index) => (
                        <li key={index} className="text-xs">
                            {alerta.mensaje}
                        </li>
                        ))}
                    </ul>
                    </div>
                )}

                <div className="p-4 bg-gray-700 rounded-lg border border-gray-600 shadow-lg">
                    <h3 className="text-sm font-bold text-gray-300 mb-3 uppercase tracking-wider">Generador de Planes</h3>
                    <div className="space-y-3">
                    <Button onClick={handleGetPlanCursada} disabled={isAnyLoading} className="w-full bg-blue-600 hover:bg-blue-700 h-auto py-3 flex flex-col items-center">
                        {isLoadingPlan ? <Loader2Icon className="h-5 w-5 animate-spin mb-1" /> : <BrainCircuit className="h-5 w-5 mb-1" />}
                        <span className="font-bold">Plan de Cursada</span>
                        <span className="text-[10px] font-normal opacity-80">Según tu Arquetipo</span>
                    </Button>
                    <Button onClick={handleGetPlanExamenes} disabled={isAnyLoading} className="w-full bg-indigo-600 hover:bg-indigo-700 h-auto py-3 flex flex-col items-center">
                        {isLoadingExamenes ? <Loader2Icon className="h-5 w-5 animate-spin mb-1" /> : <TargetIcon className="h-5 w-5 mb-1" />}
                        <span className="font-bold">Estrategia Finales</span>
                        <span className="text-[10px] font-normal opacity-80">Prioridad Inteligente</span>
                    </Button>
                    </div>
                </div>

                <div className="p-4 bg-gray-700 rounded-lg border border-gray-600">
                    <h3 className="text-sm font-bold text-gray-300 mb-3 uppercase tracking-wider">Consultas Rápidas</h3>
                    <div className="space-y-2">
                        <Button size="sm" variant="ghost" onClick={() => handleGetGeneralAdvice('cursada')} disabled={isAnyLoading} className="w-full justify-start text-gray-300 hover:text-white hover:bg-gray-600">
                            • Evaluar Cursada Actual
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => handleGetGeneralAdvice('examen')} disabled={isAnyLoading} className="w-full justify-start text-gray-300 hover:text-white hover:bg-gray-600">
                            • Evaluar Finales Pendientes
                        </Button>
                    </div>
                </div>
          </div>

          {/* Columna Derecha: Resultados */}
          <div className="lg:col-span-2 space-y-6">

               {/* Placeholder inicial si no hay nada */}
               {!planRecomendado && !planExamenes && !consejoGeneral && !consejoEspecifico && !isAnyLoading && (
                   <div className="h-full flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-700 rounded-lg text-gray-500">
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

              {/* --- RESULTADO PLAN CURSADA --- */}
              {planRecomendado && !isLoadingPlan && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* Tarjeta de Perfil Detectado */}
                    <div className={`p-5 rounded-lg shadow-lg border-l-4 bg-gray-800`} style={{ borderLeftColor: planRecomendado.arquetipo.color }}>
                         <div className="flex justify-between items-start mb-4">
                            <div>
                                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                    Arquetipo: <span style={{ color: planRecomendado.arquetipo.color }}>{planRecomendado.arquetipo.nombre}</span>
                                </h2>
                                <p className="text-sm text-gray-400 mt-1">Detectado por tu perfil laboral, familiar y ubicación.</p>
                            </div>
                            {/* Badge de color */}
                            <div className="w-8 h-8 rounded-full shadow-inner" style={{ backgroundColor: planRecomendado.arquetipo.color }}></div>
                         </div>

                         {/* Widget Dinámico */}
                         <WidgetDinamico arquetipo={planRecomendado.arquetipo} />

                         {/* Consejos Tácticos del Arquetipo */}
                         <div className="space-y-2">
                             {planRecomendado.consejos_adicionales.map((c, idx) => (
                                 <div key={idx} className="bg-gray-900/50 p-3 rounded border border-gray-700 text-sm text-gray-300 flex gap-3">
                                     <Lightbulb className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5"/>
                                     {c}
                                 </div>
                             ))}
                         </div>
                    </div>

                    {/* Lista de Materias */}
                    <div className="bg-gray-800 p-5 rounded-lg shadow-lg border border-gray-700">
                        <h3 className="font-bold text-lg text-blue-300 mb-4 flex items-center gap-2">
                            <BookOpen className="w-5 h-5"/> Plan Sugerido
                        </h3>
                        <RenderPlan plan={planRecomendado} />
                    </div>
                </div>
              )}

              {/* --- RESULTADO EXÁMENES --- */}
              {planExamenes && !isLoadingExamenes && (
                <div className="bg-gray-800 p-5 rounded-lg shadow-lg border border-gray-700 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <h3 className="font-bold text-lg text-indigo-300 mb-4 flex items-center gap-2">
                      <TargetIcon className="w-5 h-5"/> Estrategia de Finales
                  </h3>

                  {/* Consejos Globales de Examen */}
                  {planExamenes.consejos_adicionales.length > 0 && (
                      <div className="mb-6 space-y-2">
                          {planExamenes.consejos_adicionales.map((c, i) => (
                              <div key={i} className="p-3 bg-indigo-900/20 border border-indigo-800 rounded text-indigo-200 text-sm">
                                  {c}
                              </div>
                          ))}
                      </div>
                  )}

                  <div className="space-y-4">
                    {planExamenes.plan_recomendado.length > 0 ? (
                      <ul className="list-none pl-0 text-sm space-y-3">
                        {planExamenes.plan_recomendado.map(m => (
                          <li key={m.uri} className={`relative overflow-hidden p-4 rounded-lg border transition-all ${m.esta_habilitada ? 'border-green-800/50 bg-gradient-to-br from-gray-800 to-green-900/10' : 'border-red-800/50 bg-gradient-to-br from-gray-800 to-red-900/10 opacity-80'}`}>
                            
                            <div className="flex justify-between items-start mb-3 relative z-10">
                                <div className="flex items-center gap-2">
                                    {!m.esta_habilitada && <LockKeyhole className="w-4 h-4 text-red-400" />}
                                    <strong className={`text-lg ${m.esta_habilitada ? 'text-green-300' : 'text-red-300'}`}>
                                        {m.label}
                                    </strong>
                                </div>
                                {m.esta_habilitada ? (
                                    <span className="text-[10px] font-bold uppercase tracking-wider bg-green-900 text-green-400 px-2 py-1 rounded border border-green-800">Habilitada</span>
                                ) : (
                                    <span className="text-[10px] font-bold uppercase tracking-wider bg-red-900 text-red-400 px-2 py-1 rounded border border-red-800">Bloqueada</span>
                                )}
                            </div>

                            <div className="relative z-10 pl-0 md:pl-6 space-y-3">
                                {!m.esta_habilitada && (
                                    <div className="p-2 rounded bg-red-900/20 border border-red-900/50 text-red-200 text-xs flex gap-2 items-center">
                                         <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                         <span>
                                            {m.correlativas_pendientes.length > 0
                                                ? `Falta aprobar: ${m.correlativas_pendientes.join(", ")}`
                                                : m.motivo_bloqueo}
                                         </span>
                                    </div>
                                )}

                                <div className="grid grid-cols-2 gap-4 text-xs text-gray-400 bg-gray-900/30 p-2 rounded">
                                    <div>
                                        <span className="block font-bold text-gray-500 uppercase text-[10px]">Modalidad</span>
                                        <span className="text-gray-200 capitalize">{m.modalidades.join(", ") || "Estándar"}</span>
                                    </div>
                                    <div>
                                        <span className="block font-bold text-gray-500 uppercase text-[10px]">Dificultad</span>
                                        <span className="text-gray-200">{m.dificultad_examen_label} ({m.dificultad_examen_valor}/5)</span>
                                    </div>
                                </div>

                                {m.consejo_personalizado && (
                                    <div className="text-sm text-gray-300 italic border-l-2 border-yellow-600 pl-3 py-1">
                                        "{m.consejo_personalizado}"
                                    </div>
                                )}
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : <p className="text-sm text-gray-400 text-center italic">¡Estás al día! No tienes finales pendientes.</p>}
                  </div>
                </div>
              )}

              {/* --- OTROS RESULTADOS (TOPICOS, CONSEJOS SIMPLES) --- */}
              {topicos.length > 0 && materiaActiva && (
                <div className="p-5 bg-gray-800 rounded-lg shadow-lg border border-gray-700 animate-in fade-in-0">
                  <h3 className="font-bold text-lg mb-2">Consulta Específica: {materiaActiva.label}</h3>
                  <p className="text-sm text-gray-400 mb-4">Selecciona un tema para recibir orientación puntual.</p>
                  <div className="flex flex-wrap gap-2">
                    {topicos.map(topico => (
                      <Button key={topico.uri} variant="outline" className="bg-gray-700 border-gray-600 hover:bg-gray-600" onClick={() => handleSelectTopico(topico)}>{topico.label}</Button>
                    ))}
                  </div>
                </div>
              )}

              {consejoGeneral && (
                <div className="p-5 bg-gray-800 rounded-lg shadow-lg border border-yellow-700/50 animate-in fade-in-0">
                  <h3 className="font-bold text-lg text-yellow-400 mb-3">Diagnóstico General</h3>
                  <ul className="list-disc pl-4 space-y-2 text-gray-300">
                     {consejoGeneral.map((c, index) => <li key={index}>{c}</li>)}
                  </ul>
                </div>
              )}

              {consejoEspecifico && (
                <div className="p-5 bg-gray-800 rounded-lg shadow-lg border border-green-700/50 animate-in fade-in-0">
                  <h3 className="font-bold text-lg text-green-400 mb-3">Recomendación Puntual</h3>
                   <ul className="list-disc pl-4 space-y-2 text-gray-300">
                     {consejoEspecifico.map((c, index) => <li key={index}>{c}</li>)}
                  </ul>
                </div>
              )}

          </div>
        </div>
      </div>
    </main>
  );
}

// --- Componente Auxiliar ---
const RenderPlan = ({ plan }: { plan: PlanCursadaRecomendado | null }) => {
  if (!plan) return null;
  return (
    <div className="space-y-4">
      {plan.plan_recomendado.length > 0 ? (
        <div className="grid gap-3">
            {plan.plan_recomendado.map(m => (
            <div key={m.uri} className="flex items-center justify-between p-3 bg-gray-900/40 rounded border border-gray-700">
                <div>
                    <strong className="text-green-300 block">{m.label}</strong>
                    <span className="text-xs text-gray-500">Score: {m.score.toFixed(2)} | Año: {m.año}</span>
                </div>
                {m.creditos_otorgados > 0 && (
                    <span className="text-xs bg-yellow-900/30 text-yellow-500 px-2 py-1 rounded border border-yellow-900/50">
                        +{m.creditos_otorgados} Créditos
                    </span>
                )}
            </div>
            ))}
        </div>
      ) : <p className="text-sm text-gray-400 italic">No hay materias recomendadas disponibles por el momento.</p>}

      {plan.materias_omitidas.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-700">
              <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Materias Postergadas (Estrategia)</h4>
              <div className="flex flex-wrap gap-2">
                  {plan.materias_omitidas.map(m => (
                      <span key={m.uri} className="text-xs text-gray-500 bg-gray-900 px-2 py-1 rounded border border-gray-800 line-through opacity-50">
                          {m.label}
                      </span>
                  ))}
              </div>
          </div>
      )}
    </div>
  );
}
