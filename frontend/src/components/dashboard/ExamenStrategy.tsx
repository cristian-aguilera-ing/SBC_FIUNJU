import React from 'react';
import { PlanExamenRecomendado } from '@/types';
import { CheckCircle, AlertTriangle, BookOpen, Clock, Trophy, Target, ArrowRight, Info, X, Lightbulb, AlertCircle } from 'lucide-react';
import WidgetDinamico from './WidgetDinamico';

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
            <p className="text-xs md:text-sm text-white leading-relaxed font-medium tracking-wide">
              {line.replace(/[✔✓]/g, '').trim()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

const ExamenStrategy = ({ plan, isLoading }: { plan: PlanExamenRecomendado | null, isLoading: boolean }) => {
  if (isLoading) return null;
  if (!plan) return null;

  // Extraemos la recomendación técnica (texto) que viene en consejos_adicionales[0]
  const recommendationText = plan.consejos_adicionales[0] || "";
  // Extraemos el consejo clave que viene en consejos_adicionales[1]
  const keyAdvice = plan.consejos_adicionales[1] || "";

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* HEADER PERFIL */}
      <div className="bg-gray-800/30 rounded-2xl p-5 shadow-2xl border border-white/5 relative overflow-hidden">
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
            {plan.arquetipo.diagnostico || "Diagnóstico no disponible."}
          </div>
        </div>
      </div>

      {/* TARJETA DE CONSEJO CLAVE (Compacta y Separada) */}
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
            {plan.arquetipo.consejo_clave || (keyAdvice || "").split('Consejo:')[0]}
          </div>
        </div>
      </div>
      {/* PANEL DE ESTRATEGIA */}
      <div className="bg-white/[0.02] p-6 md:p-8 rounded-2xl shadow-lg border border-white/5">
        <h3 className="font-bold text-lg text-indigo-300 mb-4 flex items-center gap-2">
          <Target className="w-5 h-5" /> Estrategia de Finales
        </h3>

        {/* Aquí usamos el nuevo componente estético para la recomendación */}
        <RecommendationCard text={recommendationText} color={plan.arquetipo.color} />

        <div className="space-y-4">
          {plan.plan_recomendado.length > 0 ? (
            <ul className="list-none pl-0 text-sm space-y-3">
              {plan.plan_recomendado.map(m => {
                // Lógica de colores dinámica
                let borderColor = 'border-red-800/50';
                let bgColor = 'bg-gradient-to-br from-white/5 to-red-900/10';
                let textColor = 'text-red-300';
                let badgeBg = 'bg-red-900';
                let badgeText = 'text-red-400';
                let badgeBorder = 'border-red-800';

                if (m.esta_habilitada) {
                  if (m.dificultad_examen_valor === 2) {
                    // Normal -> Verde (Plan A)
                    borderColor = 'border-green-800/50';
                    bgColor = 'bg-gradient-to-br from-white/5 to-green-900/10';
                    textColor = 'text-green-300';
                    badgeBg = 'bg-green-900';
                    badgeText = 'text-green-400';
                    badgeBorder = 'border-green-800';
                  } else if (m.dificultad_examen_valor === 3) {
                    // Dificil -> Amarillo (Plan B - Advertencia)
                    borderColor = 'border-yellow-600/50';
                    bgColor = 'bg-gradient-to-br from-white/5 to-yellow-900/10';
                    textColor = 'text-yellow-300';
                    badgeBg = 'bg-yellow-900/40';
                    badgeText = 'text-yellow-400';
                    badgeBorder = 'border-yellow-700';
                  } else if (m.dificultad_examen_valor >= 4) {
                    // Muy Dificil -> Rojo (Plan C - Peligro)
                    borderColor = 'border-red-800/50';
                    bgColor = 'bg-gradient-to-br from-white/5 to-red-900/10';
                    textColor = 'text-red-300';
                    badgeBg = 'bg-red-900';
                    badgeText = 'text-red-400';
                    badgeBorder = 'border-red-800';
                  }
                }

                return (
                  <li key={m.uri} className={`relative overflow-hidden p-4 rounded-lg border transition-all ${borderColor} ${bgColor} ${!m.esta_habilitada ? 'opacity-80' : ''}`}>

                    <div className="flex justify-between items-start mb-3 relative z-10">
                      <div className="flex items-center gap-2">
                        {!m.esta_habilitada && <LockKeyhole className="w-4 h-4 text-red-400" />}
                        <strong className={`text-lg ${textColor}`}>
                          {m.label}
                        </strong>
                      </div>
                      {m.esta_habilitada ? (
                        m.dificultad_examen_valor === 3 ? (
                          <span className={`text-[10px] font-bold uppercase tracking-wider ${badgeBg} ${badgeText} px-2 py-1 rounded border ${badgeBorder}`}>Precaución</span>
                        ) : m.dificultad_examen_valor >= 4 ? (
                          <span className={`text-[10px] font-bold uppercase tracking-wider ${badgeBg} ${badgeText} px-2 py-1 rounded border ${badgeBorder}`}>Peligro</span>
                        ) : (
                          <span className={`text-[10px] font-bold uppercase tracking-wider ${badgeBg} ${badgeText} px-2 py-1 rounded border ${badgeBorder}`}>Habilitada</span>
                        )
                      ) : (
                        <span className={`text-[10px] font-bold uppercase tracking-wider ${badgeBg} ${badgeText} px-2 py-1 rounded border ${badgeBorder}`}>Bloqueada</span>
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
                          <span className="text-gray-200">{m.dificultad_examen_label}</span>
                        </div>
                      </div>

                      {m.consejo_personalizado && (
                        <div className="text-sm text-gray-300 italic border-l-2 border-yellow-600 pl-3 py-1">
                          "{m.consejo_personalizado}"
                        </div>
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : <p className="text-sm text-gray-400 text-center italic">¡Estás al día! No tienes finales pendientes.</p>}
        </div>
      </div>
    </div >
  );
};

export default ExamenStrategy;
