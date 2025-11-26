import React from 'react';
import { BrainCircuit, BookOpen, GraduationCap, ArrowRight, Activity, Cpu } from 'lucide-react';
import { cn } from "@/lib/utils";

interface QuickActionsProps {
  handleGetPlanCursada: () => void;
  handleGetPlanExamenes: () => void;
  handleGetTopics: () => void;
  isLoadingPlan: boolean;
  isLoadingExamenes: boolean;
  isAnyLoading: boolean;
}

const QuickActions: React.FC<QuickActionsProps> = ({
  handleGetPlanCursada,
  handleGetPlanExamenes,
  handleGetTopics,
  isLoadingPlan,
  isLoadingExamenes,
  isAnyLoading
}) => {
  
  // Lógica mapeada a la estructura visual de la copia
  const actions = [
    {
      label: "Plan Cursada",
      desc: "Ruta óptima recomendada",
      icon: BookOpen,
      onClick: handleGetPlanCursada,
      loading: isLoadingPlan,
      color: "cyan"
    },
    {
      label: "Estrategia Finales",
      desc: "Priorización de exámenes",
      icon: GraduationCap,
      onClick: handleGetPlanExamenes,
      loading: isLoadingExamenes,
      color: "purple"
    },
    {
      label: "Explorar Tópicos",
      desc: "Grafo de conocimientos",
      icon: BrainCircuit,
      onClick: handleGetTopics,
      loading: false, // En el original también es false (no tiene estado de carga propio)
      color: "emerald"
    }
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 pb-2 mb-2 border-b border-white/10">
          <Cpu className="h-4 w-4 text-cyan-400" />
          <h3 className="font-display font-semibold text-slate-200 tracking-wide uppercase text-xs md:text-sm">
            Generadores
          </h3>
      </div>

      {/* Grid Vertical para Sidebar */}
      <div className="grid grid-cols-1 gap-3">
        {actions.map((action, idx) => {
          // Lógica de deshabilitación consistente con el original:
          // Si cualquiera está cargando, todo se deshabilita
          const isDisabled = isAnyLoading;
          
          return (
            <button
              key={idx}
              onClick={action.onClick}
              disabled={isDisabled}
              className={cn(
                "group relative w-full overflow-hidden rounded-xl border border-white/5 p-3 text-left transition-all duration-300",
                "bg-black/30 hover:bg-white/5 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed",
                action.color === 'cyan' && "hover:border-cyan-500/30 hover:shadow-[0_0_15px_rgba(6,182,212,0.1)]",
                action.color === 'purple' && "hover:border-purple-500/30 hover:shadow-[0_0_15px_rgba(168,85,247,0.1)]",
                action.color === 'emerald' && "hover:border-emerald-500/30 hover:shadow-[0_0_15px_rgba(16,185,129,0.1)]"
              )}
            >
              {/* Fondo activo sutil */}
              <div className={cn(
                 "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500",
                 action.color === 'cyan' && "bg-gradient-to-r from-cyan-500/10 to-transparent",
                 action.color === 'purple' && "bg-gradient-to-r from-purple-500/10 to-transparent",
                 action.color === 'emerald' && "bg-gradient-to-r from-emerald-500/10 to-transparent",
              )} />

              <div className="relative flex items-center justify-between gap-3">
                
                {/* Icono */}
                <div className={cn(
                  "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-black/40 transition-colors group-hover:border-transparent group-hover:text-white",
                  action.color === 'cyan' && "text-cyan-400 group-hover:bg-cyan-600",
                  action.color === 'purple' && "text-purple-400 group-hover:bg-purple-600",
                  action.color === 'emerald' && "text-emerald-400 group-hover:bg-emerald-600",
                )}>
                  <action.icon size={18} />
                </div>
                
                {/* Texto */}
                <div className="flex-1 min-w-0">
                  <h4 className="font-display font-bold text-slate-200 group-hover:text-white transition-colors text-xs uppercase tracking-wider truncate">
                    {action.label}
                  </h4>
                  <p className="text-[10px] text-slate-500 group-hover:text-slate-300 transition-colors truncate">
                    {action.desc}
                  </p>
                </div>

                {/* Flecha */}
                <ArrowRight className={cn(
                   "h-4 w-4 -translate-x-2 opacity-0 transition-all duration-300 group-hover:translate-x-0 group-hover:opacity-100 shrink-0",
                   action.color === 'cyan' && "text-cyan-400",
                   action.color === 'purple' && "text-purple-400",
                   action.color === 'emerald' && "text-emerald-400",
                )} />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default QuickActions;