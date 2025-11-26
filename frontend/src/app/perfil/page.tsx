"use client";

import { useState, useEffect, FormEvent } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import {
  Trash2, ChevronDown, ChevronUp, CheckSquare, Square,
  BookOpenCheck, Award, BookCheck, CalendarCheck, AlertTriangle,
  User as UserIcon, Briefcase, Home as HomeIcon, Laptop,
  Loader2Icon, ArrowLeft
} from "lucide-react";
import { Rajdhani, Orbitron } from 'next/font/google';
import { NetworkAnimation } from '@/components/auth/NetworkAnimation';
import { motion } from 'framer-motion';

// Fuentes
const rajdhani = Rajdhani({ subsets: ['latin'], weight: ['300', '400', '500', '600', '700'], variable: '--font-rajdhani' });
const orbitron = Orbitron({ subsets: ['latin'], weight: ['400', '500', '600', '700'], variable: '--font-orbitron' });

// --- Tipos de Datos ---
enum CondicionLaboral {
  NO_TRABAJA = "no_trabaja",
  MEDIO_TIEMPO = "medio_tiempo",
  TIEMPO_COMPLETO = "tiempo_completo",
}

enum EquipamientoInformatico {
  PC_PROPIA = "pc_propia",
  PC_COMPARTIDA = "pc_compartida",
  SIN_PC = "sin_pc",
}

interface MateriaOntology {
  uri: string;
  label: string;
  año: number | null;
  creditos: number;
  creditos_requeridos: number;
  requisitos: string[];
}
interface UserMateria {
  id: number;
  materia_uri: string;
  estado: string;
  user_id: number;
  fecha_regularidad: string | null;
}
interface MateriaPerfil extends UserMateria { label: string; }

interface UserPerfil {
  full_name: string | null;
  condicion_laboral: CondicionLaboral | null;
  vive_solo: boolean | null;
  tiene_hijos: boolean | null;
  es_del_interior: boolean | null;
  equipamiento_informatico: EquipamientoInformatico | null;
  residencia_capital: boolean | null;
}
// --- Fin Tipos ---

export default function PerfilPage() {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const [allMaterias, setAllMaterias] = useState<MateriaOntology[]>([]);
  const [userMaterias, setUserMaterias] = useState<MateriaPerfil[]>([]);

  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});

  const [selectedCursarURI, setSelectedCursarURI] = useState("");
  const [selectedRendirURI, setSelectedRendirURI] = useState("");

  const [perfilData, setPerfilData] = useState<UserPerfil>({
    full_name: "",
    condicion_laboral: CondicionLaboral.NO_TRABAJA,
    vive_solo: false,
    tiene_hijos: false,
    es_del_interior: false,
    equipamiento_informatico: EquipamientoInformatico.PC_PROPIA,
    residencia_capital: true,
  });

  useEffect(() => {
    const storedToken = localStorage.getItem("sbc_access_token");
    if (!storedToken) {
      window.location.href = "/login";
      return;
    }
    setToken(storedToken);
    fetchData(storedToken);
  }, []);

  const fetchData = async (token: string) => {
    setIsLoading(true);
    try {
      const [profileResponse, ontologyResponse, userResponse] = await Promise.all([
        axios.get<UserMateria[]>("/api/sbc/users/me/materias", { headers: { Authorization: `Bearer ${token}` } }),
        axios.get<MateriaOntology[]>("/api/sbc/ontologia/materias", { headers: { Authorization: `Bearer ${token}` } }),
        axios.get<UserPerfil>("/api/sbc/users/me", { headers: { Authorization: `Bearer ${token}` } })
      ]);

      const esInterior = userResponse.data.es_del_interior || false;

      setPerfilData({
        full_name: userResponse.data.full_name || "",
        condicion_laboral: userResponse.data.condicion_laboral || CondicionLaboral.NO_TRABAJA,
        vive_solo: userResponse.data.vive_solo || false,
        tiene_hijos: userResponse.data.tiene_hijos || false,
        es_del_interior: esInterior,
        equipamiento_informatico: userResponse.data.equipamiento_informatico || EquipamientoInformatico.PC_PROPIA,
        residencia_capital: !esInterior,
      });

      setAllMaterias(ontologyResponse.data);

      const enrichedUserMaterias = profileResponse.data.map(materia => {
        const ontologyData = ontologyResponse.data.find(om => om.uri === materia.materia_uri);
        return { ...materia, label: ontologyData?.label || "Materia Desconocida" };
      });
      setUserMaterias(enrichedUserMaterias);

    } catch (error) {
      toast.error("Error de Carga", { description: "No se pudieron cargar tus datos." });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePerfilChange = (field: keyof UserPerfil, value: any) => {
    setPerfilData(prev => {
      const updated = { ...prev, [field]: value };
      if (field === "residencia_capital") updated.es_del_interior = !value;
      if (field === "es_del_interior") updated.residencia_capital = !value;
      return updated;
    });
  };

  const handleSavePerfil = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      await axios.put("/api/sbc/users/me/perfil", perfilData, { headers: { Authorization: `Bearer ${token}` } });
      toast.success("¡Perfil Personal Guardado!");
    } catch (error) {
      toast.error("Error", { description: "No se pudo guardar tu perfil personal." });
    }
  };

  const handleAddMateria = async (materiaURI: string, estado: "Cursando" | "Regular" | "Aprobada" | "PreparandoFinal") => {
    if (!token || !materiaURI) return;
    let requestBody: { materia_uri: string; estado: string; fecha_regularidad?: string; } = {
      materia_uri: materiaURI,
      estado: estado
    };
    if (estado === "Regular" || estado === "PreparandoFinal") {
      requestBody.fecha_regularidad = new Date().toISOString();
    }
    try {
      const response = await axios.post<UserMateria>(
        "/api/sbc/users/me/materias", requestBody, { headers: { Authorization: `Bearer ${token}` } }
      );
      const newMateria = response.data;
      const ontologyData = allMaterias.find(om => om.uri === newMateria.materia_uri);
      setUserMaterias(prev => {
        const existingIndex = prev.findIndex(m => m.materia_uri === materiaURI);
        const enrichedNewMateria = { ...newMateria, label: ontologyData?.label || "Materia Desconocida" };
        if (existingIndex >= 0) {
          const updated = [...prev];
          updated[existingIndex] = enrichedNewMateria;
          return updated;
        } else { return [...prev, enrichedNewMateria]; }
      });
      if (estado === "Cursando") setSelectedCursarURI("");
      if (estado === "PreparandoFinal") setSelectedRendirURI("");
      return true;
    } catch (error) {
      toast.error("Error", { description: "No se pudo añadir la materia." });
      return false;
    }
  };

  const handleDeleteMateria = async (userMateriaId: number) => {
    if (!token) return;
    try {
      await axios.delete(`/api/sbc/users/me/materias/${userMateriaId}`, { headers: { Authorization: `Bearer ${token}` } });
      setUserMaterias(prev => prev.filter(m => m.id !== userMateriaId));
      return true;
    } catch (error) {
      toast.error("Error", { description: "No se pudo quitar la materia." });
      return false;
    }
  };

  const toggleSection = (key: string) => {
    setOpenSections(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSelectAllGroup = async (subjects: MateriaOntology[]) => {
    const promises = subjects.map(subject => {
      const isAlreadyPassed = userMaterias.some(um => um.materia_uri === subject.uri && um.estado === "Aprobada");
      if (!isAlreadyPassed) return handleAddMateria(subject.uri, "Aprobada");
      return Promise.resolve(true);
    });
    await Promise.all(promises);
    toast.success("Se actualizaron las materias del grupo.");
  };

  const handleDeselectAllGroup = async (subjects: MateriaOntology[]) => {
    const promises = subjects.map(subject => {
      const existing = userMaterias.find(um => um.materia_uri === subject.uri && (um.estado === "Aprobada" || um.estado === "Regular" || um.estado === "PreparandoFinal"));
      if (existing) return handleDeleteMateria(existing.id);
      return Promise.resolve(true);
    });
    await Promise.all(promises);
    toast.success("Se quitaron las materias del grupo.");
  };

  const handleResetHistory = async () => {
    if (!confirm("¿Estás seguro de que quieres BORRAR TODO tu historial académico? Esto incluye materias aprobadas, regulares y las que estás cursando actualmente. Esta acción no se puede deshacer.")) return;

    const promises = userMaterias.map(um => handleDeleteMateria(um.id));
    await Promise.all(promises);
    toast.success("Historial académico reiniciado correctamente.");
  };

  // --- Data Processing ---
  const englishURIs = ["http://fi.unju.edu.ar/ontologia/informatica#NivSufIng", "http://fi.unju.edu.ar/ontologia/informatica#NivAptIng"];
  const materiasPorAnio: Record<number, MateriaOntology[]> = {};
  const materiasIngles: MateriaOntology[] = [];
  const materiasOptativas: MateriaOntology[] = [];

  allMaterias.forEach(m => {
    if (englishURIs.includes(m.uri)) materiasIngles.push(m);
    else if (m.año && m.año > 0) {
      if (!materiasPorAnio[m.año]) materiasPorAnio[m.año] = [];
      materiasPorAnio[m.año].push(m);
    } else materiasOptativas.push(m);
  });

  const sortedYears = Object.keys(materiasPorAnio).map(Number).sort((a, b) => a - b);
  const materiasCursando = userMaterias.filter(m => m.estado === "Cursando");
  const materiasPreparandoFinal = userMaterias.filter(m => m.estado === "PreparandoFinal");
  const materiasRegularesDisponibles = userMaterias.filter(m => m.estado === "Regular");

  // --- Lógica de Correlatividades ---
  const aprobadasURIs = userMaterias.filter(um => um.estado === "Aprobada").map(um => um.materia_uri);
  const regularizadasURIs = userMaterias.filter(um =>
    um.estado === "Regular" || um.estado === "PreparandoFinal" || um.estado === "Aprobada"
  ).map(um => um.materia_uri);

  const CREDITOS_NECESARIOS = 270;
  const creditosActuales = userMaterias.filter(um => um.estado === "Aprobada").reduce((acc, um) => {
    const materiaOnto = allMaterias.find(m => m.uri === um.materia_uri);
    return acc + (materiaOnto?.creditos || 0);
  }, 0);

  // "Cursando Ahora" (Dropdown):
  // Condición: Requisitos deben estar REGULARIZADOS (o Aprobados)
  let materiasDisponibles = allMaterias.filter(om => {
    const yaInscripto = userMaterias.some(um => um.materia_uri === om.uri);
    if (yaInscripto) return false;

    // Check correlativas vs regularizadasURIs
    if (om.requisitos && om.requisitos.length > 0) {
      const tieneCorrelativasParaCursar = om.requisitos.every(req => regularizadasURIs.includes(req));
      if (!tieneCorrelativasParaCursar) return false;
    }

    if (om.creditos_requeridos > 0 && creditosActuales < om.creditos_requeridos) return false;
    return true;
  });

  materiasDisponibles.sort((a, b) => {
    const aEsOptativa = (a.creditos || 0) > 0;
    const bEsOptativa = (b.creditos || 0) > 0;
    if (aEsOptativa !== bEsOptativa) return aEsOptativa ? 1 : -1;
    return a.label.localeCompare(b.label);
  });

  const porcentajeCreditos = Math.min(100, (creditosActuales / CREDITOS_NECESARIOS) * 100);
  const colorCreditos = creditosActuales >= CREDITOS_NECESARIOS ? "text-emerald-400" : "text-amber-400";
  const barraColor = creditosActuales >= CREDITOS_NECESARIOS ? "bg-emerald-500" : "bg-amber-500";

  const renderSubjectGroup = (title: string, subjects: MateriaOntology[], sectionKey: string, headerColorClass: string, showCreditsHeader = false) => {
    if (subjects.length === 0) return null;
    const isOpen = openSections[sectionKey];
    const passedCount = subjects.filter(s => userMaterias.some(um => um.materia_uri === s.uri && um.estado === "Aprobada")).length;
    const totalCount = subjects.length;
    const isComplete = passedCount === totalCount && totalCount > 0;

    return (
      <div key={sectionKey} className="border border-white/10 rounded-xl overflow-hidden mb-3 backdrop-blur-sm bg-white/[0.02]">
        <div className={`flex items-center justify-between p-4 cursor-pointer transition-all select-none ${isOpen ? 'bg-white/10' : 'hover:bg-white/5'}`} onClick={() => toggleSection(sectionKey)}>
          <div className="flex items-center gap-4 w-full">
            <div className={`font-display font-bold text-lg ${headerColorClass} flex-shrink-0 tracking-wide`}>{title}</div>
            {showCreditsHeader && (
              <div className="flex-grow mx-4 flex flex-col gap-1">
                <div className="flex justify-between text-[10px] uppercase font-bold tracking-widest">
                  <span className="text-slate-400">Progreso Créditos</span>
                  <span className={colorCreditos}>{creditosActuales} / {CREDITOS_NECESARIOS}</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className={`h-full ${barraColor} transition-all duration-500 ease-out shadow-[0_0_10px_currentColor]`} style={{ width: `${porcentajeCreditos}%` }} />
                </div>
              </div>
            )}
            {!showCreditsHeader && (
              <div className={`text-[10px] px-2 py-0.5 rounded-full border font-mono ml-auto tracking-wider ${isComplete ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-slate-800/50 border-white/10 text-slate-400'}`}>
                {passedCount} / {totalCount} Aprobadas
              </div>
            )}
            <div>{isOpen ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}</div>
          </div>
        </div>
        {isOpen && (
          <div className="p-4 bg-black/20 border-t border-white/5 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex gap-3 mb-4 pb-3 border-b border-white/5">
              <Button size="sm" variant="ghost" className="text-xs h-8 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/20" onClick={() => handleSelectAllGroup(subjects)} disabled={isComplete}><CheckSquare className="mr-2 h-3.5 w-3.5" /> Marcar todo</Button>
              <Button size="sm" variant="ghost" className="text-xs h-8 text-slate-400 hover:text-red-400 hover:bg-red-500/10" onClick={() => handleDeselectAllGroup(subjects)} disabled={passedCount === 0}><Square className="mr-2 h-3.5 w-3.5" /> Desmarcar todo</Button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {subjects.map(subject => {
                const userMateria = userMaterias.find(um => um.materia_uri === subject.uri);
                const isPassed = userMateria?.estado === "Aprobada";
                const isRegular = userMateria?.estado === "Regular" || userMateria?.estado === "PreparandoFinal";
                const isCursando = userMateria?.estado === "Cursando";

                // --- VALIDACIÓN DE BOTONES ---
                const cumpleCreditos = !(subject.creditos_requeridos > 0 && creditosActuales < subject.creditos_requeridos);
                const cumpleReqRegular = subject.requisitos.every(req => regularizadasURIs.includes(req));
                const habilitadoParaRegular = cumpleCreditos && cumpleReqRegular;
                const cumpleReqAprobada = subject.requisitos.every(req => aprobadasURIs.includes(req));
                const habilitadoParaAprobar = cumpleCreditos && cumpleReqAprobada;

                return (
                  <div key={subject.uri} className={`flex items-center p-3 rounded-lg border transition-all group select-none relative justify-between ${isPassed ? 'bg-emerald-500/10 border-emerald-500/30' : isRegular ? 'bg-cyan-500/10 border-cyan-500/30' : isCursando ? 'bg-blue-500/10 border-blue-500/30' : (!habilitadoParaRegular && !habilitadoParaAprobar) ? 'bg-slate-900/40 border-white/5 opacity-50' : 'bg-white/5 border-white/10 hover:border-white/20 hover:bg-white/10'}`}>
                    <div className="flex flex-col">
                      <span className={`text-sm tracking-wide ${isPassed ? 'text-emerald-200 font-medium' : isRegular ? 'text-cyan-200 font-medium' : isCursando ? 'text-blue-200 font-medium' : 'text-slate-400'}`}>{subject.label}</span>
                      <div className="flex gap-2 mt-0.5">
                        {subject.creditos > 0 && <span className="text-[10px] text-cyan-400/80 flex items-center gap-1"><Award className="h-3 w-3" /> {subject.creditos} cred.</span>}
                        {!cumpleCreditos && <span className="text-[10px] text-amber-500/80 flex items-center gap-1" title={`Requiere ${subject.creditos_requeridos} créditos`}><AlertTriangle className="h-3 w-3" /> Req. {subject.creditos_requeridos} cred.</span>}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {isCursando && (
                        <span className="text-[10px] font-bold bg-blue-600 text-white px-2 py-0.5 rounded animate-pulse">
                          CURSANDO
                        </span>
                      )}
                      <div className="flex items-center gap-1">
                        <button type="button" onClick={() => { if (isRegular) handleDeleteMateria(userMateria!.id); else handleAddMateria(subject.uri, "Regular"); }} disabled={!habilitadoParaRegular && !isRegular} className={`w-7 h-7 rounded flex items-center justify-center border text-[10px] font-bold transition-all ${isRegular ? 'bg-cyan-600 border-cyan-500 text-white shadow-[0_0_10px_rgba(6,182,212,0.5)]' : (!habilitadoParaRegular) ? 'border-white/5 text-slate-600 cursor-not-allowed' : 'border-white/10 text-slate-500 hover:border-cyan-500/50 hover:text-cyan-400 bg-black/20'}`} title={!habilitadoParaRegular ? "No cumples requisitos de cursada" : "Regularizar Materia"}>R</button>
                        <button type="button" onClick={() => { if (isPassed) handleDeleteMateria(userMateria!.id); else handleAddMateria(subject.uri, "Aprobada"); }} disabled={!habilitadoParaAprobar && !isPassed} className={`w-7 h-7 rounded flex items-center justify-center border text-[10px] font-bold transition-all ${isPassed ? 'bg-emerald-600 border-emerald-500 text-white shadow-[0_0_10px_rgba(16,185,129,0.5)]' : (!habilitadoParaAprobar) ? 'border-white/5 text-slate-600 cursor-not-allowed' : 'border-white/10 text-slate-500 hover:border-emerald-500/50 hover:text-emerald-400 bg-black/20'}`} title={!habilitadoParaAprobar ? "No cumples requisitos de final" : "Aprobar Final"}>A</button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className={`relative w-full h-screen overflow-hidden bg-slate-950 flex items-center justify-center ${rajdhani.variable} ${orbitron.variable} font-sans`}>
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-black to-slate-900" />
        <NetworkAnimation />
        <div className="relative z-30 flex flex-col items-center gap-4 backdrop-blur-md p-10 rounded-2xl border border-cyan-500/20 bg-slate-900/40 shadow-[0_0_50px_rgba(6,182,212,0.1)]">
          <Loader2Icon className="h-12 w-12 text-cyan-400 animate-spin drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
          <p className="text-cyan-100 font-display tracking-[0.3em] uppercase text-sm animate-pulse mt-2">Cargando Perfil...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative min-h-screen w-full bg-slate-950 ${rajdhani.variable} ${orbitron.variable} font-sans selection:bg-cyan-500/30`}>

      {/* --- CAPA 0: FONDO FIJO --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-slate-950" />
        <div className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] bg-purple-900/20 rounded-full blur-[120px] opacity-60" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[60vw] h-[60vw] bg-cyan-900/20 rounded-full blur-[120px] opacity-60" />
      </div>

      {/* --- CAPA 1: ANIMACIÓN --- */}
      <div className="fixed inset-0 z-10 pointer-events-none">
        <NetworkAnimation />
      </div>

      {/* --- CAPA 2: CONTENIDO PRINCIPAL --- */}
      <div className="relative z-30 min-h-screen overflow-y-auto overflow-x-hidden bg-transparent">
        <div className="container mx-auto px-4 py-6 md:py-10 lg:px-8 max-w-[1200px]">

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="w-full"
          >
            {/* TARJETA GLASS CONTAINER */}
            <div className="relative backdrop-blur-xl bg-slate-900/40 border border-white/10 rounded-3xl shadow-[0_8px_32px_0_rgba(0,0,0,0.5)] min-h-[85vh] overflow-hidden">

              {/* Gradiente Sutil Overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />

              {/* Borde Brillante Superior */}
              <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent opacity-50" />

              <div className="p-6 md:p-10">

                {/* HEADER */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-6 border-b border-white/10 pb-6">
                  <div className="flex items-center gap-5">
                    <div className="p-3 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-2xl border border-white/10 shadow-[0_0_15px_rgba(6,182,212,0.2)] hidden md:block">
                      <UserIcon className="text-cyan-300 w-8 h-8 drop-shadow-md" />
                    </div>
                    <div>
                      <h1 className="text-3xl md:text-4xl font-display font-bold text-white tracking-wider uppercase drop-shadow-lg">
                        Mi Perfil Académico
                      </h1>
                      <p className="text-slate-300 mt-1 font-light text-sm md:text-base tracking-wide">
                        Gestiona tus datos y progreso para optimizar las recomendaciones.
                      </p>
                    </div>
                  </div>

                  <Link href="/dashboard">
                    <Button variant="ghost" className="h-11 bg-white/5 text-slate-300 border border-white/10 hover:bg-cyan-500/20 hover:text-white hover:border-cyan-400/50 transition-all duration-300 backdrop-blur-sm">
                      <ArrowLeft className="mr-2 h-4 w-4" /> Volver al Panel
                    </Button>
                  </Link>
                </div>

                <form onSubmit={handleSavePerfil} className="mb-10 space-y-8">
                  {/* SECCIÓN 1: DATOS PERSONALES */}
                  <div>
                    <h2 className="text-xl font-display font-bold text-cyan-300 border-b border-white/10 pb-3 mb-6 flex items-center gap-2">
                      <span className="bg-cyan-500/20 text-cyan-300 rounded px-2 py-0.5 text-sm border border-cyan-500/30">01</span>
                      Datos Personales & Entorno
                    </h2>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      {/* Tarjeta 1 */}
                      <div className="bg-white/[0.03] rounded-2xl border border-white/10 p-6 flex flex-col h-full hover:bg-white/[0.05] transition-colors">
                        <div className="flex items-center gap-2 mb-5 text-cyan-400 font-bold uppercase text-xs tracking-widest border-b border-white/5 pb-3">
                          <UserIcon className="w-4 h-4" /> Identidad
                        </div>
                        <div className="space-y-5 flex-grow">
                          <div>
                            <Label htmlFor="fullName" className="text-slate-400 mb-2 block text-xs uppercase tracking-wider">Nombre Completo</Label>
                            <Input id="fullName" type="text" value={perfilData.full_name || ""} onChange={(e) => handlePerfilChange("full_name", e.target.value)} className="bg-black/40 border-white/10 text-white h-10 text-sm focus:border-cyan-500/50 focus:ring-cyan-500/20" placeholder="Tu nombre" />
                          </div>
                          <div>
                            <Label className="text-slate-400 mb-2 block text-xs uppercase tracking-wider">Condición Laboral</Label>
                            <Select value={perfilData.condicion_laboral || undefined} onValueChange={(v) => handlePerfilChange("condicion_laboral", v)}>
                              <SelectTrigger className="bg-black/40 border-white/10 h-10 text-sm text-white"><SelectValue placeholder="Selecciona" /></SelectTrigger>
                              <SelectContent className="bg-slate-900 border-white/10 text-white">
                                <SelectItem value={CondicionLaboral.NO_TRABAJA}>No trabajo</SelectItem>
                                <SelectItem value={CondicionLaboral.MEDIO_TIEMPO}>Medio Tiempo</SelectItem>
                                <SelectItem value={CondicionLaboral.TIEMPO_COMPLETO}>Tiempo Completo</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      </div>

                      {/* Tarjeta 2 */}
                      <div className="bg-white/[0.03] rounded-2xl border border-white/10 p-6 flex flex-col h-full hover:bg-white/[0.05] transition-colors">
                        <div className="flex items-center gap-2 mb-5 text-emerald-400 font-bold uppercase text-xs tracking-widest border-b border-white/5 pb-3">
                          <Laptop className="w-4 h-4" /> Recursos
                        </div>
                        <div className="space-y-5 flex-grow">
                          <div>
                            <Label className="text-slate-400 mb-2 block text-xs uppercase tracking-wider">PC / Notebook</Label>
                            <Select value={perfilData.equipamiento_informatico || undefined} onValueChange={(v) => handlePerfilChange("equipamiento_informatico", v)}>
                              <SelectTrigger className="bg-black/40 border-white/10 h-10 text-sm text-white"><SelectValue placeholder="Selecciona" /></SelectTrigger>
                              <SelectContent className="bg-slate-900 border-white/10 text-white">
                                <SelectItem value={EquipamientoInformatico.PC_PROPIA}>PC Propia</SelectItem>
                                <SelectItem value={EquipamientoInformatico.PC_COMPARTIDA}>PC Compartida</SelectItem>
                                <SelectItem value={EquipamientoInformatico.SIN_PC}>Sin PC</SelectItem>
                              </SelectContent>
                            </Select>
                            <p className="text-[10px] text-slate-500 mt-3 italic leading-relaxed border-l-2 border-emerald-500/30 pl-2">
                              Tu equipamiento influye en la recomendación de materias prácticas.
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Tarjeta 3 */}
                      <div className="bg-white/[0.03] rounded-2xl border border-white/10 p-6 flex flex-col h-full hover:bg-white/[0.05] transition-colors">
                        <div className="flex items-center gap-2 mb-5 text-purple-400 font-bold uppercase text-xs tracking-widest border-b border-white/5 pb-3">
                          <HomeIcon className="w-4 h-4" /> Contexto
                        </div>
                        <div className="space-y-4 flex-grow">
                          <div className="flex items-center justify-between bg-black/20 p-3 rounded-xl border border-white/5">
                            <Label className="text-slate-300 text-xs cursor-pointer uppercase tracking-wider" htmlFor="switch-solo">¿Vives solo?</Label>
                            <Switch id="switch-solo" checked={perfilData.vive_solo || false} onCheckedChange={(c) => handlePerfilChange("vive_solo", c)} className="data-[state=checked]:bg-purple-500" />
                          </div>
                          <div className="flex items-center justify-between bg-black/20 p-3 rounded-xl border border-white/5">
                            <Label className="text-slate-300 text-xs cursor-pointer uppercase tracking-wider" htmlFor="switch-hijos">¿Tienes hijos?</Label>
                            <Switch id="switch-hijos" checked={perfilData.tiene_hijos || false} onCheckedChange={(c) => handlePerfilChange("tiene_hijos", c)} className="data-[state=checked]:bg-purple-500" />
                          </div>
                          <div className="flex items-center justify-between bg-black/20 p-3 rounded-xl border border-white/5">
                            <Label className="text-slate-300 text-xs cursor-pointer uppercase tracking-wider" htmlFor="switch-capital">¿Vives en Capital?</Label>
                            <Switch id="switch-capital" checked={perfilData.residencia_capital || false} onCheckedChange={(c) => handlePerfilChange("residencia_capital", c)} className="data-[state=checked]:bg-purple-500" />
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-end mt-6">
                      <Button type="submit" className="bg-cyan-600 hover:bg-cyan-500 text-white font-bold px-8 shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_25px_rgba(6,182,212,0.5)] transition-all duration-300 rounded-xl h-11 uppercase tracking-wider text-xs">
                        Guardar Cambios
                      </Button>
                    </div>
                  </div>
                </form>

                {/* SECCIÓN 2: HISTORIAL ACADÉMICO */}
                <div className="mb-10 p-6 md:p-8 bg-white/[0.02] rounded-3xl border border-white/10 shadow-inner">
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-white/10 pb-3 mb-2 gap-4">
                    <h2 className="text-xl font-display font-bold text-cyan-300 flex items-center gap-2">
                      <span className="bg-cyan-500/20 text-cyan-300 rounded px-2 py-0.5 text-sm border border-cyan-500/30">02</span>
                      Historial Académico
                    </h2>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleResetHistory}
                      className="text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 border border-red-500/20"
                    >
                      <Trash2 className="w-3 h-3 mr-2" /> Reiniciar Historial
                    </Button>
                  </div>
                  <p className="text-sm text-slate-400 mb-6 mt-2 font-light">
                    Marca <span className="text-cyan-400 font-bold">R</span> para regularizadas y <span className="text-emerald-400 font-bold">A</span> para aprobadas.
                  </p>
                  <div className="space-y-4">
                    {sortedYears.map(year => (
                      renderSubjectGroup(`${year}° Año`, materiasPorAnio[year], year.toString(), "text-slate-200", false)
                    ))}
                    {renderSubjectGroup("Requisitos de Idioma (Inglés)", materiasIngles, "ingles", "text-cyan-400", false)}
                    {renderSubjectGroup("Materias Optativas (Créditos)", materiasOptativas, "optativas", "text-amber-400", true)}
                  </div>
                </div>

                {/* SECCIÓN 3 y 4 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                  {/* 3. Materias para Cursar */}
                  <div className="p-6 bg-white/[0.03] rounded-2xl border border-white/10 hover:bg-white/[0.05] transition-colors">
                    <h2 className="text-lg font-display font-bold mb-5 flex items-center gap-3 text-white">
                      <span className="bg-blue-500/20 text-blue-300 rounded-lg w-8 h-8 flex items-center justify-center text-sm border border-blue-500/30">03</span>
                      Cursando Ahora
                    </h2>
                    <div className="flex gap-2 mb-4">
                      <Select value={selectedCursarURI} onValueChange={setSelectedCursarURI}>
                        <SelectTrigger className="w-full bg-black/40 border-white/10 text-white h-10"><SelectValue placeholder="Elegir materia" /></SelectTrigger>
                        <SelectContent className="bg-slate-900 text-white border-white/10">
                          {materiasDisponibles.map(materia => (<SelectItem key={materia.uri} value={materia.uri}>{materia.label}</SelectItem>))}
                        </SelectContent>
                      </Select>
                      <Button onClick={() => handleAddMateria(selectedCursarURI, "Cursando")} className="bg-blue-600 hover:bg-blue-500 text-white border border-blue-400/30">Añadir</Button>
                    </div>
                    <div className="space-y-2">
                      {materiasCursando.map(m => (
                        <div key={m.id} className="flex justify-between items-center p-3 bg-blue-500/10 rounded-lg border border-blue-500/20 text-sm">
                          <span className="font-medium text-blue-200">{m.label}</span>
                          <Trash2 className="h-4 w-4 text-red-400 cursor-pointer hover:text-red-300 transition-colors" onClick={() => handleDeleteMateria(m.id)} />
                        </div>
                      ))}
                      {materiasCursando.length === 0 && <p className="text-xs text-slate-500 italic border-l-2 border-white/10 pl-3 py-1">No has seleccionado materias para cursar.</p>}
                    </div>
                  </div>

                  {/* 4. Finales para rendir ahora */}
                  <div className="p-6 bg-white/[0.03] rounded-2xl border border-white/10 hover:bg-white/[0.05] transition-colors">
                    <h2 className="text-lg font-display font-bold mb-2 flex items-center gap-3 text-white">
                      <span className="bg-purple-500/20 text-purple-300 rounded-lg w-8 h-8 flex items-center justify-center text-sm border border-purple-500/30">04</span>
                      Finales para rendir
                    </h2>
                    <p className="text-xs text-slate-400 mb-4 ml-11">
                      Elige de tus materias regulares cuáles rendirás en este turno.
                    </p>
                    <div className="flex gap-2 mb-4">
                      <Select value={selectedRendirURI} onValueChange={setSelectedRendirURI}>
                        <SelectTrigger className="w-full bg-black/40 border-white/10 text-white h-10"><SelectValue placeholder="Elegir de mis Regulares" /></SelectTrigger>
                        <SelectContent className="bg-slate-900 text-white border-white/10">
                          {materiasRegularesDisponibles.map(m => (<SelectItem key={m.materia_uri} value={m.materia_uri}>{m.label}</SelectItem>))}
                        </SelectContent>
                      </Select>
                      <Button onClick={() => handleAddMateria(selectedRendirURI, "PreparandoFinal")} className="bg-purple-600 hover:bg-purple-500 text-white border border-purple-400/30">Añadir</Button>
                    </div>
                    <div className="space-y-2">
                      {materiasPreparandoFinal.map(m => (
                        <div key={m.id} className="flex justify-between items-center p-3 bg-purple-500/10 rounded-lg border border-purple-500/20 text-sm">
                          <span className="text-purple-200 font-medium">{m.label}</span>
                          <Trash2 className="h-4 w-4 text-red-400 cursor-pointer hover:text-red-300 transition-colors" onClick={() => handleAddMateria(m.materia_uri, "Regular")} />
                        </div>
                      ))}
                      {materiasPreparandoFinal.length === 0 && <p className="text-xs text-slate-500 italic border-l-2 border-white/10 pl-3 py-1">No has seleccionado finales para rendir.</p>}
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
