"use client";

import { useState, useEffect, FormEvent } from "react";
import axios, { AxiosError } from "axios";
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
import { Trash2, ChevronDown, ChevronUp, CheckSquare, Square, BookOpenCheck, Award } from "lucide-react";

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

  // Nuevos Campos
  equipamiento_informatico: EquipamientoInformatico | null;
  residencia_capital: boolean | null; // Usado para UI, inversamente mapeado a es_del_interior
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
        axios.get<UserMateria[]>("/api/sbc/users/me/materias", { headers: { Authorization: `Bearer ${token}` }}),
        axios.get<MateriaOntology[]>("/api/sbc/ontologia/materias", { headers: { Authorization: `Bearer ${token}` }}),
        axios.get<UserPerfil>("/api/sbc/users/me", { headers: { Authorization: `Bearer ${token}` }}) 
      ]);
      
      // Ajuste para residencia_capital vs es_del_interior
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

        // Sincronización bidireccional entre residencia_capital y es_del_interior
        if (field === "residencia_capital") {
            updated.es_del_interior = !value;
        }
        if (field === "es_del_interior") {
            updated.residencia_capital = !value;
        }

        return updated;
    });
  };

  const handleSavePerfil = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      await axios.put("/api/sbc/users/me/perfil", perfilData, { headers: { Authorization: `Bearer ${token}` }});
      toast.success("¡Perfil Personal Guardado!");
    } catch (error) {
      toast.error("Error", { description: "No se pudo guardar tu perfil personal." });
    }
  };

  const handleAddMateria = async (materiaURI: string, estado: "Cursando" | "Regular" | "Aprobada") => {
    if (!token || !materiaURI) return;
    
    let requestBody: {
      materia_uri: string;
      estado: string;
      fecha_regularidad?: string;
    } = {
      materia_uri: materiaURI,
      estado: estado
    };

    if (estado === "Regular") {
      requestBody.fecha_regularidad = new Date().toISOString();
    }

    try {
      const response = await axios.post<UserMateria>(
        "/api/sbc/users/me/materias",
        requestBody,
        { headers: { Authorization: `Bearer ${token}` }}
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
        } else {
          return [...prev, enrichedNewMateria];
        }
      });
      
      if (estado === "Cursando") setSelectedCursarURI(""); 
      if (estado === "Regular") setSelectedRendirURI("");
      
      return true;

    } catch (error) {
      toast.error("Error", { description: "No se pudo añadir la materia." });
      return false;
    }
  };
  
  const handleDeleteMateria = async (userMateriaId: number) => {
    if (!token) return;
    try {
      await axios.delete(
        `/api/sbc/users/me/materias/${userMateriaId}`,
        { headers: { Authorization: `Bearer ${token}` }}
      );
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
      if (!isAlreadyPassed) {
        return handleAddMateria(subject.uri, "Aprobada");
      }
      return Promise.resolve(true);
    });
    await Promise.all(promises);
    toast.success("Se actualizaron las materias del grupo.");
  };

  const handleDeselectAllGroup = async (subjects: MateriaOntology[]) => {
    const promises = subjects.map(subject => {
      const existing = userMaterias.find(um => um.materia_uri === subject.uri && um.estado === "Aprobada");
      if (existing) {
        return handleDeleteMateria(existing.id);
      }
      return Promise.resolve(true);
    });
    await Promise.all(promises);
    toast.success("Se quitaron las materias del grupo.");
  };
  
  const englishURIs = [
    "http://fi.unju.edu.ar/ontologia/informatica#NivSufIng",
    "http://fi.unju.edu.ar/ontologia/informatica#NivAptIng"
  ];

  const materiasPorAnio: Record<number, MateriaOntology[]> = {};
  const materiasIngles: MateriaOntology[] = [];
  const materiasOptativas: MateriaOntology[] = [];

  allMaterias.forEach(m => {
    if (englishURIs.includes(m.uri)) {
        materiasIngles.push(m);
    } else if (m.año && m.año > 0) {
        if (!materiasPorAnio[m.año]) materiasPorAnio[m.año] = [];
        materiasPorAnio[m.año].push(m);
    } else {
        materiasOptativas.push(m);
    }
  });

  const sortedYears = Object.keys(materiasPorAnio).map(Number).sort((a, b) => a - b);
  const materiasCursando = userMaterias.filter(m => m.estado === "Cursando");
  const materiasRegulares = userMaterias.filter(m => m.estado === "Regular");

  // Lógica de filtrado para materias disponibles (Cursando Ahora)
  const aprobadasURIs = userMaterias.filter(um => um.estado === "Aprobada").map(um => um.materia_uri);
  const materiasDisponibles = allMaterias.filter(om => {
    // 1. No cursada ni aprobada ni regular
    const yaInscripto = userMaterias.some(um => um.materia_uri === om.uri);
    if (yaInscripto) return false;

    // 2. Verificar correlativas
    if (om.requisitos && om.requisitos.length > 0) {
        const tieneCorrelativas = om.requisitos.every(req => aprobadasURIs.includes(req));
        if (!tieneCorrelativas) return false;
    }

    return true;
  });

  const CREDITOS_NECESARIOS = 270;
  const creditosActuales = userMaterias
    .filter(um => um.estado === "Aprobada")
    .reduce((acc, um) => {
        const materiaOnto = allMaterias.find(m => m.uri === um.materia_uri);
        return acc + (materiaOnto?.creditos || 0);
    }, 0);

  const porcentajeCreditos = Math.min(100, (creditosActuales / CREDITOS_NECESARIOS) * 100);
  const colorCreditos = creditosActuales >= CREDITOS_NECESARIOS ? "text-green-400" : "text-yellow-400";
  const barraColor = creditosActuales >= CREDITOS_NECESARIOS ? "bg-green-500" : "bg-yellow-500";

  const renderSubjectGroup = (title: string, subjects: MateriaOntology[], sectionKey: string, headerColorClass: string, showCreditsHeader = false) => {
    if (subjects.length === 0) return null;
    const isOpen = openSections[sectionKey];
    const passedCount = subjects.filter(s => 
        userMaterias.some(um => um.materia_uri === s.uri && um.estado === "Aprobada")
    ).length;
    const totalCount = subjects.length;
    const isComplete = passedCount === totalCount && totalCount > 0;

    return (
        <div key={sectionKey} className="border border-gray-700 rounded-lg overflow-hidden mb-3">
            <div 
                className={`
                    flex items-center justify-between p-4 cursor-pointer transition-colors select-none
                    ${isOpen ? 'bg-gray-800' : 'bg-gray-800/50 hover:bg-gray-800'}
                `}
                onClick={() => toggleSection(sectionKey)}
            >
                <div className="flex items-center gap-4 w-full">
                    <div className={`font-bold text-lg ${headerColorClass} flex-shrink-0`}>{title}</div>
                    
                    {showCreditsHeader && (
                         <div className="flex-grow mx-4 flex flex-col gap-1">
                            <div className="flex justify-between text-xs uppercase font-bold tracking-widest">
                                <span className="text-gray-400">Progreso Créditos</span>
                                <span className={colorCreditos}>{creditosActuales} / {CREDITOS_NECESARIOS}</span>
                            </div>
                            <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                                <div 
                                    className={`h-full ${barraColor} transition-all duration-500 ease-out`} 
                                    style={{ width: `${porcentajeCreditos}%` }}
                                />
                            </div>
                        </div>
                    )}

                    {!showCreditsHeader && (
                        <div className={`
                            text-xs px-2 py-0.5 rounded-full border font-mono ml-auto
                            ${isComplete 
                                ? 'bg-green-900/30 border-green-800 text-green-400' 
                                : 'bg-gray-900 border-gray-700 text-gray-400'}
                        `}>
                            {passedCount} / {totalCount} Aprobadas
                        </div>
                    )}
                    
                    <div>{isOpen ? <ChevronUp className="h-5 w-5 text-gray-500"/> : <ChevronDown className="h-5 w-5 text-gray-500"/>}</div>
                </div>
            </div>

            {isOpen && (
                <div className="p-4 bg-gray-800/30 border-t border-gray-700 animate-in fade-in zoom-in-95 duration-200">
                    <div className="flex gap-3 mb-4 pb-3 border-b border-gray-700/50">
                        <Button 
                            size="sm" 
                            variant="secondary" 
                            className="text-xs h-8 bg-blue-900/30 hover:bg-blue-900/50 text-blue-200 border border-blue-800/50"
                            onClick={() => handleSelectAllGroup(subjects)}
                            disabled={isComplete}
                        >
                            <CheckSquare className="mr-2 h-3.5 w-3.5" /> Marcar todo
                        </Button>
                        <Button 
                            size="sm" 
                            variant="ghost" 
                            className="text-xs h-8 text-gray-400 hover:text-red-400 hover:bg-red-900/10"
                            onClick={() => handleDeselectAllGroup(subjects)}
                            disabled={passedCount === 0}
                        >
                            <Square className="mr-2 h-3.5 w-3.5" /> Desmarcar todo
                        </Button>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {subjects.map(subject => {
                            const userMateria = userMaterias.find(um => um.materia_uri === subject.uri);
                            const isPassed = userMateria?.estado === "Aprobada";
                            const isOtherState = userMateria && !isPassed;

                            return (
                                <div 
                                    key={subject.uri}
                                    onClick={() => {
                                        if (isPassed) handleDeleteMateria(userMateria!.id);
                                        else handleAddMateria(subject.uri, "Aprobada");
                                    }}
                                    className={`
                                        flex items-center p-2.5 rounded border cursor-pointer transition-all group select-none relative
                                        ${isPassed 
                                            ? 'bg-green-900/20 border-green-800/50 hover:bg-green-900/30' 
                                            : 'bg-gray-900/40 border-gray-700 hover:border-gray-500 hover:bg-gray-800'}
                                    `}
                                >
                                    <div className={`
                                        h-5 w-5 rounded flex items-center justify-center mr-3 border transition-colors
                                        ${isPassed ? 'bg-green-600 border-green-600' : 'border-gray-600 group-hover:border-gray-400 bg-gray-800'}
                                    `}>
                                        {isPassed && <BookOpenCheck className="h-3.5 w-3.5 text-white" />}
                                    </div>
                                    <div className="flex flex-col">
                                        <span className={`text-sm ${isPassed ? 'text-green-100 font-medium' : 'text-gray-400 group-hover:text-gray-200'}`}>
                                            {subject.label}
                                        </span>
                                        {subject.creditos > 0 && (
                                            <span className="text-[10px] text-blue-400 flex items-center gap-1">
                                                <Award className="h-3 w-3" /> Otorga {subject.creditos} créditos
                                            </span>
                                        )}
                                    </div>
                                    {isOtherState && (
                                        <span className="ml-auto text-[10px] font-bold text-yellow-500 bg-yellow-900/20 px-1.5 py-0.5 rounded uppercase border border-yellow-900/50">
                                            {userMateria.estado}
                                        </span>
                                    )}
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
    return <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">Cargando perfil...</main>
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-8 md:p-24 bg-gray-900 text-white">
      <div className="w-full max-w-4xl p-8 bg-gray-800 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold mb-6">Mi Perfil Académico</h1>
        <div className="mb-8">
          <Link href="/dashboard">
            <Button variant="outline" className="bg-gray-700 text-white hover:bg-gray-600">
              ← Volver al Panel de Consejos
            </Button>
          </Link>
        </div>

        <form onSubmit={handleSavePerfil} className="mb-8 p-6 bg-gray-700 rounded-lg space-y-8 border border-gray-600">
          <h2 className="text-2xl font-semibold text-blue-300 border-b border-gray-600 pb-2">1. Datos Personales & Entorno</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
             {/* COL 1 */}
             <div className="space-y-6">
                <div>
                    <Label htmlFor="fullName" className="text-gray-300 mb-2 block">Nombre Completo</Label>
                    <Input id="fullName" type="text" value={perfilData.full_name || ""} onChange={(e) => handlePerfilChange("full_name", e.target.value)} className="bg-gray-900 border-gray-600 text-white" />
                </div>

                <div>
                    <Label className="text-gray-300 mb-2 block">Condición Laboral</Label>
                    <Select value={perfilData.condicion_laboral || undefined} onValueChange={(v) => handlePerfilChange("condicion_laboral", v)}>
                        <SelectTrigger className="bg-gray-900 border-gray-600"><SelectValue placeholder="Selecciona" /></SelectTrigger>
                        <SelectContent className="bg-gray-800 border-gray-700">
                            <SelectItem value={CondicionLaboral.NO_TRABAJA}>No trabajo</SelectItem>
                            <SelectItem value={CondicionLaboral.MEDIO_TIEMPO}>Medio Tiempo</SelectItem>
                            <SelectItem value={CondicionLaboral.TIEMPO_COMPLETO}>Tiempo Completo</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="p-4 bg-gray-800/50 rounded border border-gray-600 space-y-4">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wide">Hogar y Familia</h3>
                    <div className="flex items-center justify-between">
                        <Label className="text-gray-200">¿Vives solo?</Label>
                        <Switch checked={perfilData.vive_solo || false} onCheckedChange={(c) => handlePerfilChange("vive_solo", c)} />
                    </div>
                    <div className="flex items-center justify-between">
                        <Label className="text-gray-200">¿Tienes hijos?</Label>
                        <Switch checked={perfilData.tiene_hijos || false} onCheckedChange={(c) => handlePerfilChange("tiene_hijos", c)} />
                    </div>
                    <div className="flex items-center justify-between">
                        <Label className="text-gray-200">¿Vives en Capital?</Label>
                        <Switch checked={perfilData.residencia_capital || false} onCheckedChange={(c) => handlePerfilChange("residencia_capital", c)} />
                    </div>
                </div>
             </div>

             {/* COL 2 */}
             <div className="space-y-6">
                <div>
                    <Label className="text-gray-300 mb-2 block">Equipamiento Informático</Label>
                    <Select value={perfilData.equipamiento_informatico || undefined} onValueChange={(v) => handlePerfilChange("equipamiento_informatico", v)}>
                        <SelectTrigger className="bg-gray-900 border-gray-600"><SelectValue placeholder="Selecciona" /></SelectTrigger>
                        <SelectContent className="bg-gray-800 border-gray-700">
                            <SelectItem value={EquipamientoInformatico.PC_PROPIA}>PC Propia</SelectItem>
                            <SelectItem value={EquipamientoInformatico.PC_COMPARTIDA}>PC Compartida</SelectItem>
                            <SelectItem value={EquipamientoInformatico.SIN_PC}>Sin PC</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
             </div>
          </div>

          <Button type="submit" className="w-full bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-500 hover:to-teal-500 mt-4 font-bold py-6 text-lg shadow-lg">
            Guardar Mi Perfil
          </Button>
        </form>

        {/* --- 2. Historial Académico --- */}
        <div className="mb-8 p-6 bg-gray-900/80 rounded-lg border border-gray-700 shadow-md">
            <h2 className="text-2xl font-semibold mb-2 text-blue-300 border-b border-gray-700 pb-2">2. Historial Académico</h2>
            <p className="text-sm text-gray-400 mb-6 mt-2">
                Marca las materias que ya aprobaste.
            </p>
            <div className="space-y-4">
                {sortedYears.map(year => (
                    renderSubjectGroup(`${year}° Año`, materiasPorAnio[year], year.toString(), "text-gray-200", false)
                ))}
                {renderSubjectGroup("Requisitos de Idioma (Inglés)", materiasIngles, "ingles", "text-cyan-400", false)}
                {renderSubjectGroup("Materias Optativas (Créditos)", materiasOptativas, "optativas", "text-yellow-400", true)}
            </div>
        </div>

        {/* --- 3 y 4 (Cursando y Finales) --- */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
             {/* 3. Materias para Cursar */}
            <div className="p-6 bg-gray-700 rounded-lg border border-gray-600">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-white">
                <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm border border-blue-400">3</span>
                Cursando Ahora
            </h2>
            <div className="flex gap-2 mb-4">
                <Select value={selectedCursarURI} onValueChange={setSelectedCursarURI}>
                <SelectTrigger className="w-full bg-gray-900 border-gray-600 text-white"><SelectValue placeholder="Elegir materia" /></SelectTrigger>
                <SelectContent className="bg-gray-800 text-white border-gray-600">
                    {materiasDisponibles.map(materia => (<SelectItem key={materia.uri} value={materia.uri}>{materia.label}</SelectItem>))}
                </SelectContent>
                </Select>
                <Button onClick={() => handleAddMateria(selectedCursarURI, "Cursando")} className="bg-blue-600">Añadir</Button>
            </div>
            <div className="space-y-2">
                {materiasCursando.map(m => (
                    <div key={m.id} className="flex justify-between items-center p-2 bg-gray-900/50 rounded border border-gray-600 text-sm">
                    <span>{m.label}</span>
                    <Trash2 className="h-4 w-4 text-red-400 cursor-pointer" onClick={() => handleDeleteMateria(m.id)} />
                    </div>
                ))}
            </div>
            </div>

            {/* 4. Materias para Rendir */}
            <div className="p-6 bg-gray-700 rounded-lg border border-gray-600">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-white">
                <span className="bg-indigo-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm border border-indigo-400">4</span>
                Finales Pendientes
            </h2>
            <div className="flex gap-2 mb-4">
                <Select value={selectedRendirURI} onValueChange={setSelectedRendirURI}>
                <SelectTrigger className="w-full bg-gray-900 border-gray-600 text-white"><SelectValue placeholder="Elegir materia" /></SelectTrigger>
                <SelectContent className="bg-gray-800 text-white border-gray-600">
                    {materiasDisponibles.map(materia => (<SelectItem key={materia.uri} value={materia.uri}>{materia.label}</SelectItem>))}
                </SelectContent>
                </Select>
                <Button onClick={() => handleAddMateria(selectedRendirURI, "Regular")} className="bg-indigo-600">Añadir</Button>
            </div>
            <div className="space-y-2">
                {materiasRegulares.map(m => (
                    <div key={m.id} className="flex justify-between items-center p-2 bg-gray-900/50 rounded border border-gray-600 text-sm">
                    <span>{m.label}</span>
                    <Trash2 className="h-4 w-4 text-red-400 cursor-pointer" onClick={() => handleDeleteMateria(m.id)} />
                    </div>
                ))}
            </div>
            </div>
        </div>
        
      </div>
    </main>
  );
}
