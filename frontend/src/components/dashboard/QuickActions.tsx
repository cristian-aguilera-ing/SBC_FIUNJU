import React from 'react';
import { Button } from "@/components/ui/button";
import { Loader2Icon, BrainCircuit, Target as TargetIcon } from "lucide-react";

interface QuickActionsProps {
  handleGetPlanCursada: () => void;
  handleGetPlanExamenes: () => void;
  isLoadingPlan: boolean;
  isLoadingExamenes: boolean;
  isAnyLoading: boolean;
}

const QuickActions = ({
  handleGetPlanCursada,
  handleGetPlanExamenes,
  isLoadingPlan,
  isLoadingExamenes,
  isAnyLoading
}: QuickActionsProps) => {
  return (
    <div className="space-y-6">
        <div className="p-4 bg-gray-700 rounded-lg border border-gray-600 shadow-lg">
            <h3 className="text-sm font-bold text-gray-300 mb-3 uppercase tracking-wider">Generador de Planes</h3>
            <div className="space-y-3">
            <Button onClick={handleGetPlanCursada} disabled={isAnyLoading} className="w-full bg-blue-600 hover:bg-blue-700 h-auto py-3 flex flex-col items-center">
                {isLoadingPlan ? <Loader2Icon className="h-5 w-5 animate-spin mb-1" /> : <BrainCircuit className="h-5 w-5 mb-1" />}
                <span className="font-bold">Plan de Cursada</span>
                <span className="text-[10px] font-normal opacity-80">Según tu Arquetipo</span>
            </Button>
            <Button onClick={handleGetPlanExamenes} disabled={isAnyLoading} className="w-full bg-indigo-600 hover:bg-indigo-700 h-auto py-3 flex flex-col items-center">
                {isLoadingExamenes ? <Loader2Icon className="h-5 w-5 animate-spin mb-1" /> : <TargetIcon className="h-5 w-5 mb-1" />}
                <span className="font-bold">Estrategia Finales</span>
                <span className="text-[10px] font-normal opacity-80">Prioridad Inteligente</span>
            </Button>
            </div>
        </div>
    </div>
  );
};

export default QuickActions;
