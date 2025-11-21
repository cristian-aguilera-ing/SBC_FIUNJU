"use client";

import { useRouter } from 'next/navigation';
import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { toast } from "sonner"; 
import { Loader2Icon, TriangleAlertIcon, LockKeyhole, Lightbulb, BookOpen, AlertCircle } from "lucide-react";

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
interface PlanCursadaRecomendado {
  plan_recomendado: MateriaRecomendada[];
  materias_omitidas: MateriaRecomendada[];
  consejos_adicionales: string[];
}

// --- Tipos para Plan Examen ACTUALIZADOS ---
interface MateriaExamenRecomendada {
  uri: string;
  label: string;
  dificultad_examen_label: string;
  dificultad_examen_valor: number;
  modalidades: string[];
  esta_habilitada: boolean;
  motivo_bloqueo: string | null;
  correlativas_pendientes: string[]; // Lista de nombres
  consejo_personalizado: string | null;
}
interface PlanExamenRecomendado {
  plan_recomendado: MateriaExamenRecomendada[];
  consejos_adicionales: string[];
}

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
    setPlanRecomendado(null);
    setPlanExamenes(null);
  }

  const handleGetPlanCursada = async () => {
    if (!token) return;
    setIsLoadingPlan(true);
    clearAllResults();
    try {
      const response = await axios.get<PlanCursadaRecomendado>(
        "/api/sbc/recomendacion/plan-cursada-optimo",
        { headers: { Authorization: `Bearer ${token}` }}
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
    clearAllResults();
    try {
      const response = await axios.get<PlanExamenRecomendado>(
        "/api/sbc/recomendacion/finales-prioritarios",
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setPlanExamenes(response.data);
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
      <div className="w-full max-w-3xl p-8 bg-gray-800 rounded-lg shadow-lg">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold">Bienvenido, {user.full_name || user.email}</h1>
            <p className="text-gray-400">Este es tu panel de control del SBC.</p>
          </div>
          <Button variant="outline" onClick={handleLogout} className="bg-gray-700 text-white">Cerrar Sesión</Button>
        </div>

        {/* Contenido */}
        <div className="space-y-6">
          {/* Alertas */}
          {isLoadingAlerts && (
            <div className="p-4 bg-gray-700 rounded-lg text-center text-gray-400">
              <Loader2Icon className="h-5 w-5 animate-spin inline-block" /> <span className="ml-2">Buscando alertas...</span>
            </div>
          )}
          {!isLoadingAlerts && alertas.length > 0 && (
            <div className="p-4 bg-yellow-900/50 text-yellow-200 rounded-lg space-y-3 mb-6 border border-yellow-700 animate-in fade-in-0">
              <div className="flex items-center gap-2">
                <TriangleAlertIcon className="h-5 w-5 text-yellow-300 flex-shrink-0" />
                <h3 className="text-lg font-semibold text-yellow-200">Alertas Proactivas</h3>
              </div>
              <ul className="list-disc pl-6 space-y-1">
                {alertas.map((alerta, index) => (
                  <li key={index} className="text-sm">
                    <strong>{alerta.tipo === TipoAlerta.CUELLO_DE_BOTELLA ? "Cuello de Botella:" : "Riesgo de Regularidad:"}</strong> {alerta.mensaje}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Recomendaciones */}
          <div className="p-4 bg-gray-700 rounded-lg">
            <h3 className="text-lg font-semibold mb-3">Recomendaciones (Mi Perfil Real)</h3>
            <p className="text-sm text-gray-400 mb-4">Genera un plan óptimo basado en tu perfil guardado.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button onClick={handleGetPlanCursada} disabled={isAnyLoading} className="w-full bg-blue-600 hover:bg-blue-700">
                {isLoadingPlan ? <><Loader2Icon className="mr-2 h-4 w-4 animate-spin" /> Generando...</> : "1. Sugerir Plan de Cursada"}
              </Button>
              <Button onClick={handleGetPlanExamenes} disabled={isAnyLoading} className="w-full bg-indigo-600 hover:bg-indigo-700">
                {isLoadingExamenes ? <><Loader2Icon className="mr-2 h-4 w-4 animate-spin" /> Priorizando...</> : "2. Prioritizar Mis Finales"}
              </Button>
            </div>
          </div>

          {/* Reactivo y Específico */}
          <div className="p-4 bg-gray-700 rounded-lg">
            <h3 className="text-lg font-semibold mb-3">Consejo General (Reactivo)</h3>
            <p className="text-sm text-gray-400 mb-4">Obtén un consejo basado en las materias que **ya seleccionaste** en tu perfil.</p>
            <div className="grid grid-cols-2 gap-4">
              <Button onClick={() => handleGetGeneralAdvice('cursada')} disabled={isAnyLoading} className="w-full">Evaluar mi Cursada Actual</Button>
              <Button onClick={() => handleGetGeneralAdvice('examen')} disabled={isAnyLoading} className="w-full bg-green-600 hover:bg-green-700">Evaluar mis Finales</Button>
            </div>
          </div>

          <div className="p-4 bg-gray-700 rounded-lg">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-semibold">Consejo Específico por Materia</h3>
              <Link href="/perfil"><Button variant="link" className="text-blue-400 p-0 h-auto">Editar mi Perfil</Button></Link>
            </div>
            <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
              {materiasPerfil.length > 0 ? (
                materiasPerfil.map(materia => (
                  <div key={materia.id} className="flex justify-between items-center p-3 bg-gray-900/50 rounded">
                    <span className="font-medium">{materia.label} ({materia.estado})</span>
                    <div className="flex gap-2 flex-shrink-0">
                      <Button size="sm" onClick={() => handleSelectMateria(materia, 'cursada')} disabled={isAnyLoading || materia.estado !== 'Cursando'}>Cursada</Button>
                      <Button size="sm" variant="outline" onClick={() => handleSelectMateria(materia, 'examen')} disabled={isAnyLoading || materia.estado !== 'Regular'}>Examen</Button>
                    </div>
                  </div>
                ))
              ) : ( <p className="text-gray-400 text-center py-4">No has añadido materias.</p> )}
            </div>
          </div>
          
          {/* Resultados */}
          {isAnyLoading && (
            <div className="flex justify-center items-center p-4 text-gray-400">
              <Loader2Icon className="mr-2 h-5 w-5 animate-spin" /> <p>Pensando...</p>
            </div>
          )}
          
          {topicos.length > 0 && materiaActiva && (
            <div className="p-4 bg-gray-900/50 text-white rounded-md space-y-3 animate-in fade-in-0">
              <h3 className="font-bold">Elegiste '{tipoDeConsejo}' para '{materiaActiva.label}'.</h3>
              <p className="text-sm text-gray-300">¿Sobre qué área específica necesitas consejo?</p>
              <div className="flex flex-wrap gap-2">
                {topicos.map(topico => (
                  <Button key={topico.uri} variant="outline" className="bg-gray-700" onClick={() => handleSelectTopico(topico)}>{topico.label}</Button>
                ))}
              </div>
            </div>
          )}
          
          {consejoGeneral && (
            <div className="p-4 bg-gray-900/50 text-yellow-300 rounded-md space-y-2 animate-in fade-in-0">
              <h3 className="font-bold">Consejo General:</h3>
              {consejoGeneral.map((c, index) => <p key={index}>{c}</p>)}
            </div>
          )}
          
          {consejoEspecifico && (
            <div className="p-4 bg-gray-900/50 text-green-300 rounded-md space-y-2 animate-in fade-in-0">
              <h3 className="font-bold">Consejo Específico:</h3>
              {consejoEspecifico.map((c, index) => <p key={index}>{c}</p>)}
            </div>
          )}

          {planRecomendado && (
            <div className="p-4 bg-gray-900/50 text-white rounded-md space-y-4 animate-in fade-in-0 border border-blue-800">
              <h3 className="font-bold text-lg text-blue-300">Plan de Cursada Recomendado</h3>
              <RenderPlan plan={planRecomendado} />
            </div>
          )}
          
          {/* --- RESULTADO EXÁMENES ACTUALIZADO --- */}
          {planExamenes && (
            <div className="p-4 bg-gray-900/50 text-white rounded-md space-y-4 animate-in fade-in-0 border border-indigo-800">
              <h3 className="font-bold text-lg text-indigo-300">Estrategia de Exámenes Recomendada</h3>
              <div className="space-y-2">
                <h4 className="font-semibold mb-2">Tus finales pendientes:</h4>
                {planExamenes.plan_recomendado.length > 0 ? (
                  <ul className="list-none pl-0 text-sm space-y-3">
                    {planExamenes.plan_recomendado.map(m => (
                      <li key={m.uri} className={`p-3 rounded border ${m.esta_habilitada ? 'border-green-800 bg-green-900/20' : 'border-red-800 bg-red-900/10'}`}>
                        
                        {/* Header de la tarjeta */}
                        <div className="flex justify-between items-start mb-2">
                            <div className="flex items-center gap-2">
                                {!m.esta_habilitada && <LockKeyhole className="w-4 h-4 text-red-400" />}
                                <strong className={`text-base ${m.esta_habilitada ? 'text-green-300' : 'text-red-300'}`}>
                                    {m.label}
                                </strong>
                            </div>
                            {m.esta_habilitada ? (
                                <span className="text-xs bg-green-900 text-green-200 px-2 py-1 rounded">Habilitada</span>
                            ) : (
                                <span className="text-xs bg-red-900 text-red-200 px-2 py-1 rounded">Bloqueada</span>
                            )}
                        </div>

                        {/* Detalles */}
                        <div className="pl-6 space-y-1">
                            {/* Correlativas Pendientes (Bloqueante) */}
                            {!m.esta_habilitada && m.correlativas_pendientes.length > 0 && (
                                <div className="text-red-300 flex items-start gap-2 mb-2">
                                    <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                                    <span>Debes aprobar antes: <b>{m.correlativas_pendientes.join(", ")}</b></span>
                                </div>
                            )}
                            
                            {/* Otros motivos de bloqueo (créditos) */}
                            {!m.esta_habilitada && m.motivo_bloqueo && m.correlativas_pendientes.length === 0 && (
                                <div className="text-red-300 flex items-start gap-2 mb-2">
                                    <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                                    <span>{m.motivo_bloqueo}</span>
                                </div>
                            )}

                            {/* Info General */}
                            <div className="text-gray-300 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                                <p>Modo: <span className="text-white">{m.modalidades.join(", ") || "Estándar"}</span></p>
                                <p>Dificultad: <span className="text-white">{m.dificultad_examen_label}</span></p>
                            </div>

                            {/* Consejo Personalizado */}
                            {m.consejo_personalizado && (
                                <div className="mt-3 p-2 bg-gray-800 rounded border border-gray-600 flex gap-2 items-start">
                                    <Lightbulb className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                                    <span className="text-gray-300 italic">{m.consejo_personalizado}</span>
                                </div>
                            )}
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : <p className="text-sm text-gray-400">No tienes finales pendientes.</p>}
              </div>
            </div>
          )}

        </div>
      </div>
    </main>
  );
}

// --- Componente Auxiliar para Renderizar el Plan ---
const RenderPlan = ({ plan }: { plan: PlanCursadaRecomendado | null }) => {
  if (!plan) return null;
  return (
    <>
      <div className="space-y-2">
        <h4 className="font-semibold">Materias Sugeridas:</h4>
        {plan.plan_recomendado.length > 0 ? (
          <ul className="list-disc pl-5 text-sm space-y-1">
            {plan.plan_recomendado.map(m => (
              <li key={m.uri}>
                <strong>{m.label}</strong> (Score: {m.score.toFixed(2)}) {m.creditos_otorgados > 0 && `- 🏅 ${m.creditos_otorgados} créditos`}
              </li>
            ))}
          </ul>
        ) : <p className="text-sm text-gray-400">No se encontraron materias.</p>}
      </div>
      <div className="space-y-2">
        <h4 className="font-semibold">Análisis:</h4>
        <div className="p-3 bg-gray-800/50 text-yellow-300 rounded-md space-y-2">
          {plan.consejos_adicionales.map((c, index) => <p key={index} className="text-sm">{c}</p>)}
        </div>
      </div>
    </>
  );
}