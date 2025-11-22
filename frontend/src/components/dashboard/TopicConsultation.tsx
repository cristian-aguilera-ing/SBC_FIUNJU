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
        <div className="border border-gray-700 rounded bg-gray-800 overflow-hidden mb-2">
            <button
                onClick={toggle}
                className="w-full flex items-center justify-between p-3 hover:bg-gray-700 transition-colors"
            >
                <span className="font-semibold text-sm text-gray-200">{materia.label}</span>
                {expanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
            </button>

            {expanded && (
                <div className="p-3 bg-gray-900/50 border-t border-gray-700">
                    {loadingTopicos ? (
                        <p className="text-xs text-gray-500 italic">Cargando temas...</p>
                    ) : (
                        <div className="space-y-4">
                            {/* Sección Cursada */}
                            <div>
                                <h5 className="text-xs font-bold text-green-400 uppercase mb-2 flex items-center gap-1">
                                    <BookOpen className="w-3 h-3"/> Durante la Cursada
                                </h5>
                                {topicosCursada.length > 0 ? (
                                    topicosCursada.map(t => (
                                        <TopicItem key={t.uri} topico={t} materiaUri={materia.materia_uri} tipo="cursada" token={token} />
                                    ))
                                ) : <p className="text-xs text-gray-600 ml-4">No hay consejos específicos.</p>}
                            </div>

                            {/* Sección Examen */}
                            <div>
                                <h5 className="text-xs font-bold text-purple-400 uppercase mb-2 flex items-center gap-1">
                                    <GraduationCap className="w-3 h-3"/> Para el Final
                                </h5>
                                {topicosExamen.length > 0 ? (
                                    topicosExamen.map(t => (
                                        <TopicItem key={t.uri} topico={t} materiaUri={materia.materia_uri} tipo="examen" token={token} />
                                    ))
                                ) : <p className="text-xs text-gray-600 ml-4">No hay consejos específicos.</p>}
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
        <div className="p-4 bg-gray-700 rounded-lg border border-gray-600">
            <h3 className="text-sm font-bold text-gray-300 mb-3 uppercase tracking-wider">Consulta por Tópicos</h3>
            <p className="text-xs text-gray-400 mb-3">Selecciona una de tus materias actuales para ver consejos específicos.</p>

            {materiasCursando.length > 0 ? (
                <div className="space-y-2">
                    {materiasCursando.map(m => (
                        <MateriaExpandable key={m.id} materia={m} token={token} />
                    ))}
                </div>
            ) : (
                <p className="text-sm text-yellow-500 italic bg-yellow-900/20 p-2 rounded border border-yellow-900">
                    No tienes materias marcadas como "Cursando". Ve a tu perfil para agregarlas.
                </p>
            )}
        </div>
    );
};

export default TopicConsultation;
