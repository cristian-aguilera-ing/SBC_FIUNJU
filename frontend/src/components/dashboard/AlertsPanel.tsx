import React from 'react';
import { Alerta } from '@/types';
import { TriangleAlert, Info, Loader2, ShieldCheck } from 'lucide-react';

interface AlertsPanelProps {
  alertas: Alerta[];
  isLoading: boolean;
}

const AlertsPanel: React.FC<AlertsPanelProps> = ({ alertas, isLoading }) => {

  // 1. ESTADO DE CARGA
  if (isLoading) {
    return (
      <div className="backdrop-blur-md bg-white/5 rounded-2xl border border-white/10 p-4 text-center mb-6">
        <div className="flex items-center justify-center gap-2 text-slate-400 text-xs uppercase tracking-wider animate-pulse">
          <Loader2 className="h-4 w-4 animate-spin" />
          Analizando riesgos...
        </div>
      </div>
    );
  }

  // 2. SIN ALERTAS (ESTADO SEGURO)
  // Nota: Aunque el archivo original oculta el componente si no hay alertas,
  // la interfaz "Copia" tiene un diseño específico para el estado "Sin Riesgos".
  // Se mantiene este bloque UI para preservar la estética solicitada.
  if (alertas.length === 0) {
    return (
      <div className="backdrop-blur-md bg-emerald-500/5 border border-emerald-500/20 rounded-2xl p-4 mb-6 animate-in fade-in duration-500">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 rounded-full">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
          </div>
          <div>
            <h3 className="font-display font-bold text-emerald-100/80 text-sm tracking-wide">
              Sin Riesgos Críticos
            </h3>
            <p className="text-xs text-emerald-200/50 font-light">
              Tu plan actual no presenta cuellos de botella graves detectados.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // 3. CON ALERTAS: Agrupar por tipo
  const opportunities = alertas.filter(a => a.tipo === "oportunidad_academica");
  const risks = alertas.filter(a => a.tipo !== "oportunidad_academica");

  return (
    <div className="space-y-4 mb-6 animate-in fade-in slide-in-from-top-4 duration-500">

      {/* OPORTUNIDADES (Blue/Cyan) */}
      {opportunities.length > 0 && (
        <div className="backdrop-blur-xl bg-cyan-500/10 border border-cyan-500/50 rounded-2xl p-5 shadow-[0_0_20px_rgba(6,182,212,0.15)]">
          <div className="flex items-center gap-3 mb-4 pb-3 border-b border-cyan-500/20">
            <div className="p-2 bg-cyan-500/20 rounded-lg">
              <ShieldCheck className="h-5 w-5 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
            </div>
            <h3 className="font-display font-bold text-cyan-100 tracking-wide uppercase text-sm">
              Oportunidades Académicas
            </h3>
          </div>
          <ul className="space-y-3">
            {opportunities.map((alerta, index) => (
              <li key={index} className="flex gap-3 items-start bg-cyan-950/30 p-3 rounded-lg border border-cyan-500/10 hover:border-cyan-500/30 transition-colors">
                <Info className="h-4 w-4 text-cyan-400/70 mt-0.5 shrink-0" />
                <span className="text-xs text-cyan-100/90 font-light leading-relaxed">
                  {alerta.mensaje}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* RIESGOS / CUELLOS DE BOTELLA (Amber) */}
      {risks.length > 0 && (
        <div className="backdrop-blur-xl bg-amber-500/10 border border-amber-500/50 rounded-2xl p-5 shadow-[0_0_20px_rgba(245,158,11,0.15)]">
          <div className="flex items-center gap-3 mb-4 pb-3 border-b border-amber-500/20">
            <div className="p-2 bg-amber-500/20 rounded-lg">
              <TriangleAlert className="h-5 w-5 text-amber-400 drop-shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
            </div>
            <h3 className="font-display font-bold text-amber-100 tracking-wide uppercase text-sm">
              Atención: Riesgos Detectados
            </h3>
          </div>

          <ul className="space-y-3">
            {risks.map((alerta, index) => (
              <li key={index} className="flex gap-3 items-start bg-amber-950/30 p-3 rounded-lg border border-amber-500/10 hover:border-amber-500/30 transition-colors">
                <Info className="h-4 w-4 text-amber-400/70 mt-0.5 shrink-0" />
                <span className="text-xs text-amber-100/90 font-light leading-relaxed">
                  {alerta.mensaje}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AlertsPanel;