import React from 'react';
import { PlanExamenRecomendado } from '@/types';
import { TargetIcon, LockKeyhole, AlertCircle } from "lucide-react";

const ExamenStrategy = ({ plan, isLoading }: { plan: PlanExamenRecomendado | null, isLoading: boolean }) => {
  if (isLoading) return null;
  if (!plan) return null;

  return (
    <div className="bg-gray-800 p-5 rounded-lg shadow-lg border border-gray-700 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <h3 className="font-bold text-lg text-indigo-300 mb-4 flex items-center gap-2">
        <TargetIcon className="w-5 h-5" /> Estrategia de Finales
      </h3>

      {/* Consejos Globales de Examen */}
      {plan.consejos_adicionales.length > 0 && (
        <div className="mb-6 space-y-2">
          {plan.consejos_adicionales.map((c, i) => (
            <div key={i} className="p-3 bg-indigo-900/20 border border-indigo-800 rounded text-indigo-200 text-sm">
              {c}
            </div>
          ))}
        </div>
      )}

      <div className="space-y-4">
        {plan.plan_recomendado.length > 0 ? (
          <ul className="list-none pl-0 text-sm space-y-3">
            {plan.plan_recomendado.map(m => (
              <li key={m.uri} className={`relative overflow-hidden p-4 rounded-lg border transition-all ${m.esta_habilitada ? 'border-green-800/50 bg-gradient-to-br from-gray-800 to-green-900/10' : 'border-red-800/50 bg-gradient-to-br from-gray-800 to-red-900/10 opacity-80'}`}>

                <div className="flex justify-between items-start mb-3 relative z-10">
                  <div className="flex items-center gap-2">
                    {!m.esta_habilitada && <LockKeyhole className="w-4 h-4 text-red-400" />}
                    <strong className={`text-lg ${m.esta_habilitada ? 'text-green-300' : 'text-red-300'}`}>
                      {m.label}
                    </strong>
                  </div>
                  {m.esta_habilitada ? (
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-green-900 text-green-400 px-2 py-1 rounded border border-green-800">Habilitada</span>
                  ) : (
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-red-900 text-red-400 px-2 py-1 rounded border border-red-800">Bloqueada</span>
                  )}
                </div>

                <div className="relative z-10 pl-0 md:pl-6 space-y-3">
                  {!m.esta_habilitada && (
                    <div className="p-2 rounded bg-red-900/20 border border-red-900/50 text-red-200 text-xs flex gap-2 items-center">
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      <span>
                        {m.correlativas_pendientes.length > 0
                          ? `Falta aprobar: ${m.correlativas_pendientes.join(", ")}`
                          : m.motivo_bloqueo}
                      </span>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4 text-xs text-gray-400 bg-gray-900/30 p-2 rounded">
                    <div>
                      <span className="block font-bold text-gray-500 uppercase text-[10px]">Modalidad</span>
                      <span className="text-gray-200 capitalize">{m.modalidades.join(", ") || "Estándar"}</span>
                    </div>
                    <div>
                      <span className="block font-bold text-gray-500 uppercase text-[10px]">Dificultad</span>
                      <span className="text-gray-200">{m.dificultad_examen_label} ({m.dificultad_examen_valor}/5)</span>
                    </div>
                  </div>

                  {m.consejo_personalizado && (
                    <div className="text-sm text-gray-300 italic border-l-2 border-yellow-600 pl-3 py-1">
                      "{m.consejo_personalizado}"
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        ) : <p className="text-sm text-gray-400 text-center italic">¡Estás al día! No tienes finales pendientes.</p>}
      </div>
    </div>
  );
};

export default ExamenStrategy;
