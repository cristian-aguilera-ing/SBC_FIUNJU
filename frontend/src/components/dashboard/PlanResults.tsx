import React from 'react';
import { PlanCursadaRecomendado } from '@/types';
import WidgetDinamico from './WidgetDinamico';
import { BookOpen, CheckCircle, XCircle, Info, Check } from "lucide-react";

// Componente para renderizar la tarjeta de recomendación estética
const RecommendationCard = ({ text, color }: { text: string, color: string }) => {
    const lines = text.split('\n').filter(line => line.trim() !== '');
    
    return (
        <div className="bg-gray-900/60 border border-gray-700 rounded-lg p-4 mb-4">
            <h5 className="text-xs font-bold text-gray-400 uppercase mb-3 flex items-center gap-2">
                <Info className="w-3 h-3" /> Estrategia Recomendada
            </h5>
            <div className="space-y-2">
                {lines.map((line, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                        <div 
                            className="mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0" 
                            style={{ backgroundColor: color }}
                        />
                        <p className="text-sm text-gray-200 leading-tight font-medium">
                            {line.replace(/[✔✓]/g, '').trim()} {/* Limpiamos los checks del texto original si existen */}
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
                <CheckCircle className="w-4 h-4"/> Materias a Cursar
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
                  <XCircle className="w-3 h-3"/> Sugerimos postergar (Sobrecarga)
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
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* HEADER PERFIL */}
      <div className="bg-gray-800 rounded-xl p-6 shadow-xl border border-gray-700 relative overflow-hidden">
        {/* Fondo con gradiente sutil basado en el color del arquetipo */}
        <div 
            className="absolute top-0 right-0 w-64 h-64 opacity-10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"
            style={{ backgroundColor: plan.arquetipo.color }}
        />

        <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Tu Arquetipo Detectado</span>
            </div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
                <span style={{ color: plan.arquetipo.color }}>{plan.arquetipo.nombre}</span>
            </h2>

            {/* Widget Dinámico (Iconos) */}
            <WidgetDinamico arquetipo={plan.arquetipo} />

            {/* Comentario Principal */}
            <div className="mt-6 text-gray-300 text-sm leading-relaxed border-l-2 pl-4 italic" style={{ borderColor: plan.arquetipo.color }}>
                "{plan.arquetipo.consejos[0]}"
            </div>
        </div>
      </div>

      {/* PANEL DE PLANIFICACIÓN */}
      <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
        <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-xl text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-400" /> Plan de Cursada
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