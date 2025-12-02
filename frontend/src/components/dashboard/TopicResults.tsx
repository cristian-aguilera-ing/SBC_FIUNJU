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
    const [isExpanded, setIsExpanded] = useState(false);

    const handleAsk = async () => {
        if (!token) return;

        // Si ya está expandido, solo contraer
        if (isExpanded) {
            setIsExpanded(false);
            return;
        }

        // Si ya tenemos el consejo, solo expandir
        if (consejo) {
            setIsExpanded(true);
            return;
        }

        // Si no tenemos el consejo, pedirlo
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
                endpoint, body, { headers: { Authorization: `Bearer ${token}` } }
            );
            setConsejo(response.data.consejos);
            setIsExpanded(true);
        } catch (error) {
            toast.error("Error al obtener consejo");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mb-2">
            <button
                onClick={handleAsk}
                disabled={loading}
                className="group w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800/30 border-l-2 border-blue-500/50 hover:border-blue-400 hover:bg-gray-800/50 transition-all duration-200 disabled:opacity-50"
            >
                <MessageSquare className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
                <span className="text-sm text-gray-300 group-hover:text-white transition-colors flex-1 text-left">
                    {topico.label}
                </span>
                {loading && (
                    <div className="w-3.5 h-3.5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin flex-shrink-0" />
                )}
            </button>
            {consejo && isExpanded && (
                <div className="mt-3 ml-6 p-4 bg-gradient-to-br from-emerald-900/20 via-blue-900/20 to-purple-900/20 border-l-4 border-emerald-500/60 rounded-r-xl animate-in slide-in-from-left-2 duration-300 shadow-lg">
                    <div className="space-y-3">
                        {consejo.map((c, i) => (
                            <div key={i} className="flex items-start gap-3 text-sm leading-relaxed">
                                <span className="flex-shrink-0 w-2 h-2 rounded-full bg-emerald-400 mt-1.5 shadow-sm shadow-emerald-400/50" />
                                <p className="flex-1 text-gray-200">{c}</p>
                            </div>
                        ))}
                    </div>
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
        <div className="border border-white/10 rounded-xl bg-gradient-to-br from-gray-800/50 to-gray-900/50 overflow-hidden mb-3 backdrop-blur-sm hover:border-white/20 transition-all duration-300 shadow-lg">
            <button
                onClick={toggle}
                className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors group"
            >
                <div className="flex flex-col items-start">
                    <span className="font-semibold text-base text-gray-100 group-hover:text-white transition-colors">{materia.label}</span>
                    <span className="text-[10px] text-gray-400 uppercase tracking-wider">
                        {tipos.includes('cursada') && tipos.includes('examen') ? "Cursada y Final" : tipos.includes('cursada') ? "Cursando" : "Final"}
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    {(topicosCursada.length > 0 || topicosExamen.length > 0) && (
                        <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full">
                            {topicosCursada.length + topicosExamen.length}
                        </span>
                    )}
                    {expanded ?
                        <ChevronDown className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" /> :
                        <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
                    }
                </div>
            </button>

            {expanded && (
                <div className="p-4 bg-black/20 border-t border-white/5 animate-in slide-in-from-top-2 duration-300">
                    {loadingTopicos ? (
                        <div className="flex items-center justify-center gap-2 py-8">
                            <div className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                            <p className="text-sm text-gray-400">Cargando temas...</p>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Sección Cursada */}
                            {tipos.includes('cursada') && (
                                <div className="p-4 rounded-xl bg-gradient-to-br from-green-900/10 to-emerald-900/10 border border-green-500/20">
                                    <h5 className="text-sm font-bold text-green-400 uppercase mb-3 flex items-center gap-2">
                                        <div className="w-6 h-6 rounded-lg bg-green-500/20 flex items-center justify-center">
                                            <BookOpen className="w-4 h-4" />
                                        </div>
                                        Durante la Cursada
                                    </h5>
                                    {topicosCursada.length > 0 ? (
                                        <div className="space-y-2">
                                            {topicosCursada.map(t => (
                                                <TopicItem key={t.uri} topico={t} materiaUri={materia.materia_uri} tipo="cursada" token={token} />
                                            ))}
                                        </div>
                                    ) : <p className="text-xs text-gray-500 ml-2">Sin tópicos específicos.</p>}
                                </div>
                            )}

                            {/* Sección Examen */}
                            {tipos.includes('examen') && (
                                <div className="p-4 rounded-xl bg-gradient-to-br from-purple-900/10 to-fuchsia-900/10 border border-purple-500/20">
                                    <h5 className="text-sm font-bold text-purple-400 uppercase mb-3 flex items-center gap-2">
                                        <div className="w-6 h-6 rounded-lg bg-purple-500/20 flex items-center justify-center">
                                            <GraduationCap className="w-4 h-4" />
                                        </div>
                                        Para el Final
                                    </h5>
                                    {topicosExamen.length > 0 ? (
                                        <div className="space-y-2">
                                            {topicosExamen.map(t => (
                                                <TopicItem key={t.uri} topico={t} materiaUri={materia.materia_uri} tipo="examen" token={token} />
                                            ))}
                                        </div>
                                    ) : <p className="text-xs text-gray-500 ml-2">Sin tópicos específicos.</p>}
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
        <div className="p-6 bg-gradient-to-br from-gray-800/40 to-gray-900/40 rounded-2xl border border-white/10 backdrop-blur-sm shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-5">
                <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                        <MessageSquare className="w-5 h-5 text-blue-400" />
                    </div>
                    Explorar Tópicos
                </h3>
                <p className="text-sm text-gray-400">Explora consejos específicos sobre los temas de tus materias actuales.</p>
            </div>

            <div className="space-y-3">
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
