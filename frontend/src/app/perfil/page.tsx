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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"; 
import { Label } from "@/components/ui/label"; 
import { toast } from "sonner"; 
import Link from "next/link";
import { Input } from "@/components/ui/input";
// --- CORRECCIÓN AQUÍ: Se añadió 'Award' a los imports ---
import { Trash2, ChevronDown, ChevronUp, CheckSquare, Square, BookOpenCheck, Award } from "lucide-react";

// --- Tipos de Datos ---
enum CondicionLaboral {
  NO_TRABAJA = "no_trabaja",
  MEDIO_TIEMPO = "medio_tiempo",
  TIEMPO_COMPLETO = "tiempo_completo",
}
enum HorasEstudio {
  POCAS = "pocas",
  NORMAL = "normal",
  MUCHAS = "muchas",
}
enum ColegioSecundario {
  TECNICA_INFORMATICA = "tecnica_informatica",
  TECNICA_OTRA = "tecnica_otra",
  BACHILLER = "bachiller",
}
enum MetodoEstudio {
  SOLO = "solo",
  GRUPO = "grupo",
  MIXTO = "mixto",
}

interface MateriaOntology { 
    uri: string; 
    label: string; 
    año: number | null; 
    creditos: number; // Nuevo campo para créditos
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
  horas_estudio: HorasEstudio | null;
  colegio_secundario: ColegioSecundario | null;
  metodo_estudio_preferido: MetodoEstudio | null;
  vive_solo: boolean | null;
  tiene_hijos: boolean | null;
  es_del_interior: boolean | null;
}
// --- Fin Tipos ---

export default function PerfilPage() {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const [allMaterias, setAllMaterias] = useState<MateriaOntology[]>([]);
  const [userMaterias, setUserMaterias] = useState<MateriaPerfil[]>([]); 
  
  // Estado para el acordeón
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});

  const [selectedCursarURI, setSelectedCursarURI] = useState("");
  const [selectedRendirURI, setSelectedRendirURI] = useState("");
  
  const [perfilData, setPerfilData] = useState<UserPerfil>({
    full_name: "",
    condicion_laboral: CondicionLaboral.NO_TRABAJA,
    horas_estudio: HorasEstudio.NORMAL,
    colegio_secundario: ColegioSecundario.BACHILLER,
    metodo_estudio_preferido: MetodoEstudio.SOLO,
    vive_solo: false,
    tiene_hijos: false,
    es_del_interior: false,
  });

  // Carga inicial de datos
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
      
      setPerfilData({
        full_name: userResponse.data.full_name || "",
        condicion_laboral: userResponse.data.condicion_laboral || CondicionLaboral.NO_TRABAJA,
        horas_estudio: userResponse.data.horas_estudio || HorasEstudio.NORMAL,
        colegio_secundario: userResponse.data.colegio_secundario || ColegioSecundario.BACHILLER,
        metodo_estudio_preferido: userResponse.data.metodo_estudio_preferido || MetodoEstudio.SOLO,
        vive_solo: userResponse.data.vive_solo || false,
        tiene_hijos: userResponse.data.tiene_hijos || false,
        es_del_interior: userResponse.data.es_del_interior || false,
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
  
  const handlePerfilChange = (field: keyof UserPerfil, value: string | boolean) => {
    setPerfilData(prev => ({ ...prev, [field]: value }));
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
      
      // Actualización optimista
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
  
  // --- Lógica del Acordeón ---
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
  
  // --- AGRUPACIÓN DE MATERIAS ---
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
  
  const materiasDisponibles = allMaterias.filter(
    om => !userMaterias.some(um => um.materia_uri === om.uri)
  );

  // --- CÁLCULO DE CRÉDITOS ---
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

  // --- Componente Auxiliar de Renderizado de Grupo ---
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
            {/* Header */}
            <div 
                className={`
                    flex items-center justify-between p-4 cursor-pointer transition-colors select-none
                    ${isOpen ? 'bg-gray-800' : 'bg-gray-800/50 hover:bg-gray-800'}
                `}
                onClick={() => toggleSection(sectionKey)}
            >
                <div className="flex items-center gap-4 w-full">
                    <div className={`font-bold text-lg ${headerColorClass} flex-shrink-0`}>{title}</div>
                    
                    {/* Visualizador de Créditos en Header (Solo para Optativas) */}
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
                    
                    {showCreditsHeader && (
                        <div>{isOpen ? <ChevronUp className="h-5 w-5 text-gray-500"/> : <ChevronDown className="h-5 w-5 text-gray-500"/>}</div>
                    )}
                    {!showCreditsHeader && (
                        isOpen ? <ChevronUp className="h-5 w-5 text-gray-500"/> : <ChevronDown className="h-5 w-5 text-gray-500"/>
                    )}

                </div>
            </div>

            {/* Body */}
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

        {/* --- 1. Formulario de Perfil Personal --- */}
        <form onSubmit={handleSavePerfil} className="mb-8 p-6 bg-gray-700 rounded-lg space-y-6 border border-gray-600">
          <h2 className="text-2xl font-semibold text-blue-300 border-b border-gray-600 pb-2">1. Datos Personales</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
                <div>
                    <Label htmlFor="fullName" className="text-gray-300 mb-2 block">Nombre Completo</Label>
                    <Input
                    id="fullName"
                    type="text"
                    value={perfilData.full_name || ""}
                    onChange={(e) => handlePerfilChange("full_name", e.target.value)}
                    className="bg-gray-900 border-gray-600 text-white"
                    />
                </div>
                <div>
                    <Label className="text-gray-300 mb-2 block">¿De qué colegio vienes?</Label>
                    <RadioGroup
                    value={perfilData.colegio_secundario || undefined}
                    onValueChange={(value) => handlePerfilChange("colegio_secundario", value)}
                    className="space-y-2"
                    >
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={ColegioSecundario.BACHILLER} id="c1" />
                        <Label htmlFor="c1">Bachiller</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={ColegioSecundario.TECNICA_INFORMATICA} id="c2" />
                        <Label htmlFor="c2">Técnica (Informática)</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={ColegioSecundario.TECNICA_OTRA} id="c3" />
                        <Label htmlFor="c3">Técnica (Otra)</Label>
                    </div>
                    </RadioGroup>
                </div>
                <div>
                    <Label className="text-gray-300 mb-2 block">Situación Laboral</Label>
                    <RadioGroup
                    value={perfilData.condicion_laboral || undefined}
                    onValueChange={(value) => handlePerfilChange("condicion_laboral", value)}
                    className="space-y-2"
                    >
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={CondicionLaboral.NO_TRABAJA} id="r1" />
                        <Label htmlFor="r1">No trabajo</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={CondicionLaboral.MEDIO_TIEMPO} id="r2" />
                        <Label htmlFor="r2">Medio tiempo (~4hs)</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={CondicionLaboral.TIEMPO_COMPLETO} id="r3" />
                        <Label htmlFor="r3">Tiempo completo (~8hs)</Label>
                    </div>
                    </RadioGroup>
                </div>
            </div>

            <div className="space-y-6">
                <div>
                    <Label className="text-gray-300 mb-2 block">Horas de estudio semanal</Label>
                    <RadioGroup
                    value={perfilData.horas_estudio || undefined}
                    onValueChange={(value) => handlePerfilChange("horas_estudio", value)}
                    className="space-y-2"
                    >
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={HorasEstudio.POCAS} id="h1" />
                        <Label htmlFor="h1">Pocas (-10 hs)</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={HorasEstudio.NORMAL} id="h2" />
                        <Label htmlFor="h2">Normal (10-20 hs)</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={HorasEstudio.MUCHAS} id="h3" />
                        <Label htmlFor="h3">Muchas (+20 hs)</Label>
                    </div>
                    </RadioGroup>
                </div>
                <div>
                    <Label className="text-gray-300 mb-2 block">Método de estudio preferido</Label>
                    <RadioGroup
                    value={perfilData.metodo_estudio_preferido || undefined}
                    onValueChange={(value) => handlePerfilChange("metodo_estudio_preferido", value)}
                    className="space-y-2"
                    >
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={MetodoEstudio.SOLO} id="m1" />
                        <Label htmlFor="m1">Solo</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={MetodoEstudio.GRUPO} id="m2" />
                        <Label htmlFor="m2">En Grupo</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value={MetodoEstudio.MIXTO} id="m3" />
                        <Label htmlFor="m3">Mixto</Label>
                    </div>
                    </RadioGroup>
                </div>
            </div>
          </div>
          <Button type="submit" className="w-full bg-green-600 hover:bg-green-700 mt-4 font-semibold py-6 text-lg">
            Guardar Datos Personales
          </Button>
        </form>

        {/* --- 2. Historial Académico (Materias Aprobadas) --- */}
        <div className="mb-8 p-6 bg-gray-900/80 rounded-lg border border-gray-700 shadow-md">
            <h2 className="text-2xl font-semibold mb-2 text-blue-300 border-b border-gray-700 pb-2">2. Historial Académico (Materias Aprobadas)</h2>
            <p className="text-sm text-gray-400 mb-6 mt-2">
                Marca las materias que ya aprobaste. Esto habilita las correlativas para cursar.
            </p>

            <div className="space-y-4">
                {/* 2.1 - Años Regulares */}
                {sortedYears.map(year => (
                    renderSubjectGroup(`${year}° Año`, materiasPorAnio[year], year.toString(), "text-gray-200", false)
                ))}
                
                {/* 2.2 - Requisitos de Idioma */}
                {renderSubjectGroup("Requisitos de Idioma (Inglés)", materiasIngles, "ingles", "text-cyan-400", false)}
                
                {/* 2.3 - Materias Optativas (CON CRÉDITOS) */}
                {renderSubjectGroup("Materias Optativas (Créditos)", materiasOptativas, "optativas", "text-yellow-400", true)}
            </div>
        </div>

        {/* --- 3. Materias para Cursar --- */}
        <div className="mb-8 p-6 bg-gray-700 rounded-lg border border-gray-600">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-white">
             <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm border border-blue-400">3</span>
             ¿Qué estás cursando ahora?
          </h2>
          <div className="flex gap-4 mb-4 pl-0 md:pl-10">
            <Select value={selectedCursarURI} onValueChange={setSelectedCursarURI}>
              <SelectTrigger className="w-full bg-gray-900 border-gray-600 text-white">
                <SelectValue placeholder="Selecciona materia..." />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 text-white border-gray-600">
                {materiasDisponibles.map(materia => (
                  <SelectItem key={materia.uri} value={materia.uri} className="focus:bg-gray-700">
                    {materia.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={() => handleAddMateria(selectedCursarURI, "Cursando")} className="bg-blue-600 hover:bg-blue-700">
              Añadir
            </Button>
          </div>
          <div className="space-y-2 pl-0 md:pl-10">
            {materiasCursando.length > 0 ? (
              materiasCursando.map(materia => (
                <div key={materia.id} className="flex justify-between items-center p-3 bg-gray-900/50 rounded border border-gray-600">
                  <span className="font-medium">{materia.label}</span>
                  <Button variant="ghost" size="icon" className="text-red-400 hover:bg-red-900/30 hover:text-red-300" onClick={() => handleDeleteMateria(materia.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))
            ) : ( <p className="text-gray-400 text-sm italic">No has añadido materias para cursar.</p> )}
          </div>
        </div>

        {/* --- 4. Materias para Rendir --- */}
        <div className="p-6 bg-gray-700 rounded-lg border border-gray-600">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-white">
             <span className="bg-indigo-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm border border-indigo-400">4</span>
             ¿Qué finales debes? (Regulares)
          </h2>
          <div className="flex gap-4 mb-4 pl-0 md:pl-10">
            <Select value={selectedRendirURI} onValueChange={setSelectedRendirURI}>
              <SelectTrigger className="w-full bg-gray-900 border-gray-600 text-white">
                <SelectValue placeholder="Selecciona materia..." />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 text-white border-gray-600">
                {materiasDisponibles.map(materia => (
                  <SelectItem key={materia.uri} value={materia.uri} className="focus:bg-gray-700">
                    {materia.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={() => handleAddMateria(selectedRendirURI, "Regular")} className="bg-indigo-600 hover:bg-indigo-700">
              Añadir
            </Button>
          </div>
          <div className="space-y-2 pl-0 md:pl-10">
            {materiasRegulares.length > 0 ? (
              materiasRegulares.map(materia => (
                <div key={materia.id} className="flex justify-between items-center p-3 bg-gray-900/50 rounded border border-gray-600">
                  <span className="font-medium">{materia.label}</span>
                  <Button variant="ghost" size="icon" className="text-red-400 hover:bg-red-900/30 hover:text-red-300" onClick={() => handleDeleteMateria(materia.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))
            ) : ( <p className="text-gray-400 text-sm italic">No has añadido materias para rendir.</p> )}
          </div>
        </div>
        
      </div>
    </main>
  );
}