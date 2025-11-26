import React from 'react';
import { PlanCursadaRecomendado } from '@/types';
import WidgetDinamico from './WidgetDinamico';
import { BookOpen, CheckCircle, XCircle, Info, Check } from "lucide-react";

// Componente para renderizar la tarjeta de recomendación estética (Estrategia Específica)
const RecommendationCard = ({ text, color }: { text: string, color: string }) => {
    const lines = text.split('\n').filter(line => line.trim() !== '');

    return (
        <div className="bg-gradient-to-r from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6 mb-6 shadow-lg relative overflow-hidden group">
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
                        <p className="text-lg md:text-xl text-white leading-relaxed font-medium tracking-wide">
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
                            <div key={m.uri} className="relative group overflow-hidden flex items-center justify-between p-4 bg-gradient-to-r from-gray-800 to-gray-800/50 rounded-lg border border-green-900/30 hover:border-green-500/50 transition-all shadow-md">
                                {/* Borde izquierdo coloreado */}
                                <div className="absolute left-0 top-0 bottom-0 w-1 bg-green-500"></div>

                                <div className="pl-2">
                                    <strong className="text-green-100 block text-base tracking-tight">{m.label}</strong>
                                    <span className="text-xs text-gray-400 font-mono mt-1 inline-block bg-gray-900/50 px-2 py-0.5 rounded">
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
                            <div key={m.uri} className="flex items-center justify-between p-2 bg-gray-900 rounded border border-gray-800 text-gray-500 text-xs">
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
            <div className="bg-gray-800 rounded-2xl p-5 shadow-2xl border border-gray-700 relative overflow-hidden">
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
                        <div className="bg-gray-900/50 p-1.5 rounded-xl border border-white/5 backdrop-blur-sm scale-90 origin-right">
                            <WidgetDinamico arquetipo={plan.arquetipo} />
                        </div>
                    </div>
                </div>
            </div>

            {/* TARJETA DE DIAGNÓSTICO (Auto-height) */}
            <div className="relative rounded-2xl p-1 bg-gradient-to-br from-gray-800 to-gray-900 shadow-xl">
                <div className="absolute inset-0 rounded-2xl opacity-20" style={{ border: `1px solid ${plan.arquetipo.color}`, boxShadow: `0 0 20px ${plan.arquetipo.color}20` }} />

                <div className="bg-gray-900/90 backdrop-blur-xl rounded-xl p-6 md:p-8 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1" style={{ backgroundColor: plan.arquetipo.color }} />

                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2 uppercase tracking-wide">
                        <CheckCircle className="w-5 h-5" style={{ color: plan.arquetipo.color }} />
                        Diagnóstico
                    </h3>

                    <div className="text-gray-300 text-base md:text-lg leading-relaxed space-y-2">
                        {plan.arquetipo.consejos[0].split('Consejo:')[0].split('\n').map((line, i) => {
                            const isBullet = line.trim().startsWith('*');
                            if (!line.trim()) return null;
                            return (
                                <p key={i} className={`
                                ${isBullet ? "ml-6 pl-4 border-l-2 border-gray-700 italic text-gray-400" : ""}
                                ${i === 0 ? "font-medium text-white mb-2" : ""}
                            `}>
                                    {line.replace('*', '').trim()}
                                </p>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* TARJETA DE CONSEJO (Separada y Llamativa) */}
            {plan.arquetipo.consejos[0].includes('Consejo:') && (
                <div className="relative overflow-hidden rounded-xl p-6 border border-white/10 shadow-2xl group">
                    {/* Fondo Animado Sutil */}
                    <div className="absolute inset-0 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900" />
                    <div className="absolute inset-0 opacity-10 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] mix-blend-overlay" />

                    {/* Glow Effect based on Archetype Color */}
                    <div className="absolute -left-20 -bottom-20 w-64 h-64 rounded-full blur-[80px] opacity-20" style={{ backgroundColor: plan.arquetipo.color }} />

                    <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center gap-6">
                        <div className="p-3 rounded-full bg-white/5 border border-white/10 shadow-inner shrink-0">
                            <Info className="w-8 h-8" style={{ color: plan.arquetipo.color }} />
                        </div>

                        <div>
                            <h4 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Consejo Clave</h4>
                            <p className="text-xl md:text-2xl font-display font-medium text-white leading-tight drop-shadow-sm">
                                {plan.arquetipo.consejos[0].split('Consejo:')[1].trim()}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* PANEL DE PLANIFICACIÓN */}
            <div className="bg-gray-800 p-6 md:p-8 rounded-2xl shadow-lg border border-gray-700">
                <div className="flex items-center justify-between mb-8 border-b border-gray-700 pb-4">
                    <h3 className="font-bold text-2xl text-white flex items-center gap-3">
                        <BookOpen className="w-6 h-6 text-blue-400" /> Plan de Cursada
                    </h3>
                </div>

                {/* Aquí usamos el nuevo componente estético para la recomendación */}
                <RecommendationCard text={recommendationText} color={plan.arquetipo.color} />

                <RenderPlan plan={plan} />
            </div>
        </div>
    );
};

export default PlanResults;