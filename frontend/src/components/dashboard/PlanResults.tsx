import React from 'react';
import { PlanCursadaRecomendado } from '@/types';
import WidgetDinamico from './WidgetDinamico';
import { Lightbulb, BookOpen } from "lucide-react";

const RenderPlan = ({ plan }: { plan: PlanCursadaRecomendado | null }) => {
  if (!plan) return null;
  return (
    <div className="space-y-4">
      {plan.plan_recomendado.length > 0 ? (
        <div className="grid gap-3">
            {plan.plan_recomendado.map(m => (
            <div key={m.uri} className="flex items-center justify-between p-3 bg-gray-900/40 rounded border border-gray-700">
                <div>
                    <strong className="text-green-300 block">{m.label}</strong>
                    <span className="text-xs text-gray-500">Score: {m.score.toFixed(2)} | Año: {m.año}</span>
                </div>
                {m.creditos_otorgados > 0 && (
                    <span className="text-xs bg-yellow-900/30 text-yellow-500 px-2 py-1 rounded border border-yellow-900/50">
                        +{m.creditos_otorgados} Créditos
                    </span>
                )}
            </div>
            ))}
        </div>
      ) : <p className="text-sm text-gray-400 italic">No hay materias recomendadas disponibles por el momento.</p>}

      {plan.materias_omitidas.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-700">
              <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Materias Postergadas (Estrategia)</h4>
              <div className="flex flex-wrap gap-2">
                  {plan.materias_omitidas.map(m => (
                      <span key={m.uri} className="text-xs text-gray-500 bg-gray-900 px-2 py-1 rounded border border-gray-800 line-through opacity-50">
                          {m.label}
                      </span>
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

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Tarjeta de Perfil Detectado */}
      <div className={`p-5 rounded-lg shadow-lg border-l-4 bg-gray-800`} style={{ borderLeftColor: plan.arquetipo.color }}>
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              Arquetipo: <span style={{ color: plan.arquetipo.color }}>{plan.arquetipo.nombre}</span>
            </h2>
            <p className="text-sm text-gray-400 mt-1">Detectado por tu perfil laboral, familiar y ubicación.</p>
          </div>
          {/* Badge de color */}
          <div className="w-8 h-8 rounded-full shadow-inner" style={{ backgroundColor: plan.arquetipo.color }}></div>
        </div>

        {/* Widget Dinámico */}
        <WidgetDinamico arquetipo={plan.arquetipo} />

        {/* Consejos Tácticos del Arquetipo */}
        <div className="space-y-2">
          {plan.consejos_adicionales.map((c, idx) => (
            <div key={idx} className="bg-gray-900/50 p-3 rounded border border-gray-700 text-sm text-gray-300 flex gap-3">
              <Lightbulb className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
              {c}
            </div>
          ))}
        </div>
      </div>

      {/* Lista de Materias */}
      <div className="bg-gray-800 p-5 rounded-lg shadow-lg border border-gray-700">
        <h3 className="font-bold text-lg text-blue-300 mb-4 flex items-center gap-2">
          <BookOpen className="w-5 h-5" /> Plan Sugerido
        </h3>
        <RenderPlan plan={plan} />
      </div>
    </div>
  );
};

export default PlanResults;
