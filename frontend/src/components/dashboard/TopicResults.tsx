import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { MateriaPerfil, TopicoOntology, ConsejoResponse } from "@/types";
import { ChevronRight, ChevronDown, BookOpen, GraduationCap, MessageSquare } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

interface TopicResultsProps {
  materiasPerfil: MateriaPerfil[];
  token: string | null;
}

// Subcomponente para mostrar un tópico y pedir consejo
const TopicItem = ({
    topico,
    materiaUri,
    tipo,
    token
}: {
    topico: TopicoOntology,
    materiaUri: string,
    tipo: 'cursada' | 'examen',
    token: string | null
}) => {
    const [consejo, setConsejo] = useState<string[] | null>(null);
    const [loading, setLoading] = useState(false);

    const handleAsk = async () => {
        if (!token) return;
        setLoading(true);
        try {
            const endpoint = tipo === 'cursada'
                ? '/api/sbc/consejos/cursada/especifico'
                : '/api/sbc/consejos/examen/especifico';

            const body = {
                materia_uris_request: [materiaUri],
                topico_uri: topico.uri
            };

            const response = await axios.post<ConsejoResponse>(
                endpoint, body, { headers: { Authorization: `Bearer ${token}` }}
            );
            setConsejo(response.data.consejos);
        } catch (error) {
            toast.error("Error al obtener consejo");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="ml-4 mb-2">
            <Button
                variant="ghost"
                size="sm"
                onClick={handleAsk}
                disabled={loading}
                className="text-gray-300 hover:text-blue-300 hover:bg-blue-900/20 text-xs flex items-center gap-2 w-full justify-start"
            >
                <MessageSquare className="w-3 h-3" />
                {topico.label}
            </Button>
            {consejo && (
                 <div className="ml-6 mt-1 p-2 bg-blue-900/30 border border-blue-800 rounded text-xs text-blue-200 animate-in fade-in-0">
                    {consejo.map((c, i) => <p key={i}>• {c}</p>)}
                 </div>
            )}
        </div>
    );
};

// Subcomponente para una materia expandible
const MateriaExpandable = ({ materia, token, tipos }: { materia: MateriaPerfil, token: string | null, tipos: ('cursada' | 'examen')[] }) => {
    const [expanded, setExpanded] = useState(false);
    const [topicosCursada, setTopicosCursada] = useState<TopicoOntology[]>([]);
    const [topicosExamen, setTopicosExamen] = useState<TopicoOntology[]>([]);
    const [loadingTopicos, setLoadingTopicos] = useState(false);
    const [loaded, setLoaded] = useState(false);

    const toggle = async () => {
        if (!expanded && !loaded && token) {
            setLoadingTopicos(true);
            try {
                const promises = [];
                if (tipos.includes('cursada')) {
                    promises.push(axios.get<TopicoOntology[]>(`/api/sbc/ontologia/materias/topicos`, {
                        headers: { Authorization: `Bearer ${token}` },
                        params: { materia_uri: materia.materia_uri, tipo: 'cursada' }
                    }).then(res => setTopicosCursada(res.data)));
                }
                if (tipos.includes('examen')) {
                    promises.push(axios.get<TopicoOntology[]>(`/api/sbc/ontologia/materias/topicos`, {
                        headers: { Authorization: `Bearer ${token}` },
                        params: { materia_uri: materia.materia_uri, tipo: 'examen' }
                    }).then(res => setTopicosExamen(res.data)));
                }
                await Promise.all(promises);
                setLoaded(true);
            } catch (err) {
                toast.error("Error cargando tópicos");
            } finally {
                setLoadingTopicos(false);
            }
        }
        setExpanded(!expanded);
    };

    return (
        <div className="border border-gray-700 rounded bg-gray-800/80 overflow-hidden mb-3">
            <button
                onClick={toggle}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-700 transition-colors"
            >
                <div className="flex flex-col items-start">
                    <span className="font-semibold text-sm text-gray-200">{materia.label}</span>
                    <span className="text-[10px] text-gray-400 uppercase tracking-wider">
                        {tipos.includes('cursada') && tipos.includes('examen') ? "Cursada y Final" : tipos.includes('cursada') ? "Cursando" : "Final"}
                    </span>
                </div>
                {expanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
            </button>

            {expanded && (
                <div className="p-3 bg-gray-900/30 border-t border-gray-700 animate-in slide-in-from-top-2">
                    {loadingTopicos ? (
                        <p className="text-xs text-gray-500 italic">Cargando temas...</p>
                    ) : (
                        <div className="space-y-4">
                            {/* Sección Cursada */}
                            {tipos.includes('cursada') && (
                                <div>
                                    <h5 className="text-xs font-bold text-green-400 uppercase mb-2 flex items-center gap-1 border-b border-gray-700/50 pb-1">
                                        <BookOpen className="w-3 h-3"/> Durante la Cursada
                                    </h5>
                                    {topicosCursada.length > 0 ? (
                                        topicosCursada.map(t => (
                                            <TopicItem key={t.uri} topico={t} materiaUri={materia.materia_uri} tipo="cursada" token={token} />
                                        ))
                                    ) : <p className="text-xs text-gray-500 ml-4 italic">Sin tópicos específicos.</p>}
                                </div>
                            )}

                            {/* Sección Examen */}
                            {tipos.includes('examen') && (
                                <div>
                                    <h5 className="text-xs font-bold text-purple-400 uppercase mb-2 flex items-center gap-1 border-b border-gray-700/50 pb-1">
                                        <GraduationCap className="w-3 h-3"/> Para el Final
                                    </h5>
                                    {topicosExamen.length > 0 ? (
                                        topicosExamen.map(t => (
                                            <TopicItem key={t.uri} topico={t} materiaUri={materia.materia_uri} tipo="examen" token={token} />
                                        ))
                                    ) : <p className="text-xs text-gray-500 ml-4 italic">Sin tópicos específicos.</p>}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

const TopicResults = ({ materiasPerfil, token }: TopicResultsProps) => {
    // Filtrar materias
    const materiasCursando = materiasPerfil.filter(m => m.estado === "Cursando");
    // PreparandoFinal = Seleccionado para rendir AHORA
    // Regular = Habilitado para rendir (pero quizás no seleccionado ahora? El usuario dijo "materias que esta seleccionado en 'Finales para rendir ahora'")
    // Así que usamos estado 'PreparandoFinal'.
    const materiasRindiendo = materiasPerfil.filter(m => m.estado === "PreparandoFinal");

    // Combinamos para mostrar en la lista. Algunas podrían estar en ambos estados? (Raro en el modelo actual, estado es string único).
    // Si el estado es único, una materia es Cursando O Regular O PreparandoFinal.

    if (materiasCursando.length === 0 && materiasRindiendo.length === 0) {
        return (
            <div className="p-8 text-center text-gray-400 border border-dashed border-gray-700 rounded-lg">
                <p>No tienes materias seleccionadas en "Cursando Ahora" ni en "Finales para Rendir Ahora".</p>
                <p className="text-xs mt-2">Ve a tu perfil para seleccionarlas.</p>
            </div>
        );
    }

    return (
        <div className="bg-gray-800 p-5 rounded-lg shadow-lg border border-gray-700 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h3 className="font-bold text-lg text-blue-300 mb-4 flex items-center gap-2">
                <MessageSquare className="w-5 h-5"/> Consulta por Tópicos
            </h3>
            <p className="text-sm text-gray-400 mb-6">
                Explora consejos específicos sobre los temas de tus materias actuales.
            </p>

            <div className="space-y-2">
                {materiasCursando.map(m => (
                    <MateriaExpandable key={`cur-${m.id}`} materia={m} token={token} tipos={['cursada']} />
                ))}

                {materiasRindiendo.map(m => (
                    <MateriaExpandable key={`fin-${m.id}`} materia={m} token={token} tipos={['examen']} />
                ))}
            </div>
        </div>
    );
};

export default TopicResults;
