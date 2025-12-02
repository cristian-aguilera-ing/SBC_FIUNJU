import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { MateriaPerfil, TopicoOntology, ConsejoResponse } from "@/types";
import { ChevronRight, ChevronDown, BookOpen, GraduationCap, MessageSquare } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

interface TopicConsultationProps {
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
                endpoint, body, { headers: { Authorization: `Bearer ${token}` } }
            );
            setConsejo(response.data.consejos);
        } catch (error) {
            toast.error("Error al obtener consejo");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mb-3">
            <button
                onClick={handleAsk}
                disabled={loading}
                className="group w-full flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 hover:border-blue-400/60 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20 disabled:opacity-50"
            >
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center group-hover:bg-blue-500/30 transition-colors">
                    <MessageSquare className="w-4 h-4 text-blue-400" />
                </div>
                <div className="flex-1 text-left">
                    <p className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">
                        {topico.label}
                    </p>
                    {topico.descripcion && (
                        <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">
                            {topico.descripcion}
                        </p>
                    )}
                </div>
                {loading && (
                    <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                )}
            </button>
            {consejo && (
                <div className="mt-2 ml-2 p-4 bg-gradient-to-br from-blue-900/40 to-indigo-900/40 border border-blue-500/50 rounded-xl animate-in slide-in-from-top-2 duration-300 backdrop-blur-sm">
                    <div className="space-y-2">
                        {consejo.map((c, i) => (
                            <div key={i} className="flex items-start gap-2 text-sm text-blue-100">
                                <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-blue-400 mt-2" />
                                <p className="flex-1">{c}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

// Subcomponente para una materia expandible
const MateriaExpandable = ({ materia, token }: { materia: MateriaPerfil, token: string | null }) => {
    const [expanded, setExpanded] = useState(false);
    const [topicosCursada, setTopicosCursada] = useState<TopicoOntology[]>([]);
    const [topicosExamen, setTopicosExamen] = useState<TopicoOntology[]>([]);
    const [loadingTopicos, setLoadingTopicos] = useState(false);
    const [loaded, setLoaded] = useState(false);

    const toggle = async () => {
        if (!expanded && !loaded && token) {
            setLoadingTopicos(true);
            try {
                const [resCursada, resExamen] = await Promise.all([
                    axios.get<TopicoOntology[]>(`/api/sbc/ontologia/materias/topicos`, {
                        headers: { Authorization: `Bearer ${token}` },
                        params: { materia_uri: materia.materia_uri, tipo: 'cursada' }
                    }),
                    axios.get<TopicoOntology[]>(`/api/sbc/ontologia/materias/topicos`, {
                        headers: { Authorization: `Bearer ${token}` },
                        params: { materia_uri: materia.materia_uri, tipo: 'examen' }
                    })
                ]);
                setTopicosCursada(resCursada.data);
                setTopicosExamen(resExamen.data);
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
                <span className="font-semibold text-base text-gray-100 group-hover:text-white transition-colors">{materia.label}</span>
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
                                ) : <p className="text-xs text-gray-500 ml-2">No hay consejos específicos.</p>}
                            </div>

                            {/* Sección Examen */}
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
                                ) : <p className="text-xs text-gray-500 ml-2">No hay consejos específicos.</p>}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

const TopicConsultation = ({ materiasPerfil, token }: TopicConsultationProps) => {
    // Filtrar materias "Cursando" (asumimos que estado "Cursando" o similar es lo que buscamos)
    // En UserMateria el estado por defecto es "Cursando".
    const materiasCursando = materiasPerfil.filter(m => m.estado === "Cursando" || m.estado === "Regular");

    return (
        <div className="p-6 bg-gradient-to-br from-gray-800/40 to-gray-900/40 rounded-2xl border border-white/10 backdrop-blur-sm shadow-2xl">
            <div className="mb-5">
                <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                        <MessageSquare className="w-5 h-5 text-blue-400" />
                    </div>
                    Explorar Tópicos
                </h3>
                <p className="text-sm text-gray-400">Selecciona una materia para ver consejos específicos sobre cada tema.</p>
            </div>

            {materiasCursando.length > 0 ? (
                <div className="space-y-3">
                    {materiasCursando.map(m => (
                        <MateriaExpandable key={m.id} materia={m} token={token} />
                    ))}
                </div>
            ) : (
                <div className="p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30">
                    <p className="text-sm text-yellow-300 flex items-center gap-2">
                        <span className="text-xl">⚠️</span>
                        No tienes materias marcadas como "Cursando". Ve a tu perfil para agregarlas.
                    </p>
                </div>
            )}
        </div>
    );
};

export default TopicConsultation;
