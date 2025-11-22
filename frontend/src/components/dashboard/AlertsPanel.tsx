import React from 'react';
import { Alerta } from '@/types';
import { Loader2Icon, TriangleAlertIcon } from "lucide-react";

interface AlertsPanelProps {
  alertas: Alerta[];
  isLoading: boolean;
}

const AlertsPanel = ({ alertas, isLoading }: AlertsPanelProps) => {
  return (
    <>
      {isLoading && (
        <div className="p-4 bg-gray-700 rounded-lg text-center text-gray-400 text-xs">
          <Loader2Icon className="h-4 w-4 animate-spin inline-block" /> Buscando alertas...
        </div>
      )}
      {!isLoading && alertas.length > 0 && (
        <div className="p-4 bg-yellow-900/50 text-yellow-200 rounded-lg space-y-3 border border-yellow-700 animate-in fade-in-0">
          <div className="flex items-center gap-2">
            <TriangleAlertIcon className="h-5 w-5 text-yellow-300 flex-shrink-0" />
            <h3 className="text-sm font-bold uppercase tracking-wider">Atención</h3>
          </div>
          <ul className="list-disc pl-4 space-y-1">
            {alertas.map((alerta, index) => (
              <li key={index} className="text-xs">
                {alerta.mensaje}
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
};

export default AlertsPanel;
