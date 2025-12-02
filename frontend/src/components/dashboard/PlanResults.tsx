import React from 'react';
import { PlanCursadaRecomendado } from '@/types';
import WidgetDinamico from './WidgetDinamico';
import { CheckCircle, AlertTriangle, BookOpen, Clock, Trophy, Target, ArrowRight, Info, X, Lightbulb, XCircle } from 'lucide-react';
import { obtenerDiagnostico } from '@/constants/diagnosticos';

// Componente para renderizar la tarjeta de recomendación estética (Estrategia Específica)
const RecommendationCard = ({ text, color }: { text: string, color: string }) => {
    const lines = text.split('\n').filter(line => line.trim() !== '');

    return (
        <div className="bg-gradient-to-r from-white/5 to-white/10 border border-white/10 rounded-xl p-6 mb-6 shadow-lg relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full" style={{ backgroundColor: color }} />
            <div className="absolute -right-10 -top-10 w-32 h-32 bg-white/5 rounded-full blur-3xl group-hover:bg-white/10 transition-all" />

            <h5 className="text-sm font-bold text-gray-400 uppercase mb-4 flex items-center gap-2 tracking-wider">
                <Info className="w-4 h-4" style={{ color }} /> Estrategia Recomendada
            </h5>
            <div className="space-y-3 relative z-10">
                {lines.map((line, idx) => (
                    <div key={idx} className="flex items-start gap-4">
                        <div
                            className="mt-1.5 w-2 h-2 rounded-full flex-shrink-0 shadow-[0_0_10px_currentColor]"
                            style={{ backgroundColor: color, color: color }}
                        />
                        <p className="text-xs md:text-sm text-white leading-relaxed font-medium tracking-wide">
                            {line.replace(/[✔✓]/g, '').trim()}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
};

const RenderPlan = ({ plan }: { plan: PlanCursadaRecomendado | null }) => {
    if (!plan) return null;
    return (
        <div className="space-y-4">
            {/* SECCIÓN RECOMENDADA */}
            {plan.plan_recomendado.length > 0 ? (
                <div className="space-y-2">
                    <h4 className="text-sm font-bold text-green-400 uppercase flex items-center gap-2 mb-3">
                        <CheckCircle className="w-4 h-4" /> Materias a Cursar
                    </h4>
                    <div className="grid gap-3">
                        {plan.plan_recomendado.map(m => (
                            <div key={m.uri} className="relative group overflow-hidden flex items-center justify-between p-4 bg-gradient-to-r from-white/5 to-white/10 rounded-lg border border-green-900/30 hover:border-green-500/50 transition-all shadow-md">
                                {/* Borde izquierdo coloreado */}
                                <div className="absolute left-0 top-0 bottom-0 w-1 bg-green-500"></div>

                                <div className="pl-2">
                                    <strong className="text-green-100 block text-base tracking-tight">{m.label}</strong>
                                    <span className="text-xs text-gray-400 font-mono mt-1 inline-block bg-black/20 px-2 py-0.5 rounded">
                                        Nivel Dificultad: {m.dificultad}
                                    </span>
                                </div>

                                {m.creditos_otorgados > 0 && (
                                    <div className="flex flex-col items-end">
                                        <span className="text-[10px] font-bold text-green-400 bg-green-900/20 px-2 py-1 rounded border border-green-800">
                                            +{m.creditos_otorgados} Créditos
                                        </span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="p-4 rounded border border-dashed border-gray-700 text-center text-gray-500 text-sm bg-gray-800/30">
                    <p>Ninguna de las materias que seleccionaste cumple con los criterios estrictos de tu perfil actual.</p>
                </div>
            )}

            {/* SECCIÓN OMITIDAS */}
            {plan.materias_omitidas.length > 0 && (
                <div className="mt-8 pt-6 border-t border-gray-700/50 space-y-3">
                    <h4 className="text-xs font-bold text-red-400 uppercase flex items-center gap-2">
                        <XCircle className="w-3 h-3" /> Sugerimos postergar (Sobrecarga)
                    </h4>
                    <div className="grid gap-2 opacity-60 hover:opacity-100 transition-opacity">
                        {plan.materias_omitidas.map(m => (
                            <div key={m.uri} className="flex items-center justify-between p-2 bg-black/20 rounded border border-white/5 text-gray-500 text-xs">
                                <span className="pl-2">{m.label}</span>
                                <span className="font-mono bg-gray-800 px-1.5 py-0.5 rounded">Dif: {m.dificultad}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

const PlanResults = ({ plan, isLoading }: { plan: PlanCursadaRecomendado | null, isLoading: boolean }) => {
    if (isLoading) return null;
    if (!plan) return null;

    // Extraemos la recomendación técnica (texto) que viene en consejos_adicionales[0]
    const recommendationText = plan.consejos_adicionales[0] || "";

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* HEADER PERFIL */}
            <div className="bg-white/[0.02] rounded-2xl p-5 shadow-2xl border border-white/5 relative overflow-hidden">
                {/* Fondo con gradiente sutil basado en el color del arquetipo */}
                <div
                    className="absolute top-0 right-0 w-96 h-96 opacity-10 rounded-full blur-[100px] -mr-20 -mt-20 pointer-events-none"
                    style={{ backgroundColor: plan.arquetipo.color }}
                />

                <div className="relative z-10">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                        <div>
                            <div className="flex items-center gap-3 mb-1">
                                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Tu Arquetipo Detectado</span>
                            </div>
                            <h2 className="text-2xl md:text-3xl font-display font-bold text-white flex items-center gap-3 drop-shadow-md">
                                <span style={{ color: plan.arquetipo.color }}>{plan.arquetipo.nombre}</span>
                            </h2>
                        </div>
                        {/* Widget Dinámico (Iconos) */}
                        <div className="bg-black/20 p-1.5 rounded-xl border border-white/5 backdrop-blur-sm scale-90 origin-right">
                            <WidgetDinamico arquetipo={plan.arquetipo} />
                        </div>
                    </div>
                </div>
            </div>

            {/* TARJETA DE DIAGNÓSTICO (Compacta) */}
            <div className="relative rounded-xl p-0.5 bg-gradient-to-br from-white/5 to-white/10 shadow-lg mt-4">
                <div className="absolute inset-0 rounded-xl opacity-20" style={{ border: `1px solid ${plan.arquetipo.color}`, boxShadow: `0 0 15px ${plan.arquetipo.color}15` }} />

                <div className="bg-slate-900/40 backdrop-blur-xl rounded-xl p-4 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-0.5" style={{ backgroundColor: plan.arquetipo.color }} />

                    <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2 uppercase tracking-wide">
                        <CheckCircle className="w-4 h-4" style={{ color: plan.arquetipo.color }} />
                        Diagnóstico
                    </h3>

                    <div className="text-gray-300 text-xs md:text-sm leading-relaxed whitespace-pre-wrap">
                        {obtenerDiagnostico(plan.arquetipo.nombre, plan.arquetipo.diagnostico)}
                    </div>
                </div>
            </div>

            {/* TARJETA DE CONSEJO CLAVE (Compacta y Separada) */}
            <div className="relative rounded-xl p-0.5 bg-gradient-to-br from-white/5 to-white/10 shadow-lg mt-3">
                <div className="absolute inset-0 rounded-xl opacity-20" style={{ border: `1px solid ${plan.arquetipo.color}`, boxShadow: `0 0 15px ${plan.arquetipo.color}15` }} />

                <div className="bg-slate-900/40 backdrop-blur-xl rounded-xl p-4 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-0.5" style={{ backgroundColor: plan.arquetipo.color }} />

                    <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2 uppercase tracking-wide">
                        <Lightbulb className="w-4 h-4" style={{ color: plan.arquetipo.color }} />
                        Consejo Clave
                    </h3>

                    <div className="text-gray-300 text-xs md:text-sm leading-relaxed whitespace-pre-wrap">
                        {plan.arquetipo.consejo_clave || plan.arquetipo.consejos[0].split('Consejo:')[0]}
                    </div>
                </div>
            </div>




            {/* PANEL DE PLANIFICACIÓN */}
            <div className="bg-white/[0.02] p-6 md:p-8 rounded-2xl shadow-lg border border-white/5">
                <div className="flex items-center justify-between mb-8 border-b border-gray-700 pb-4">
                    <h3 className="font-bold text-2xl text-white flex items-center gap-3">
                        <BookOpen className="w-6 h-6 text-blue-400" /> Plan de Cursada
                    </h3>
                </div>

                {/* Aquí usamos el nuevo componente estético para la recomendación */}
                <RecommendationCard text={recommendationText} color={plan.arquetipo.color} />

                <RenderPlan plan={plan} />
            </div>
        </div >
    );
};

export default PlanResults;