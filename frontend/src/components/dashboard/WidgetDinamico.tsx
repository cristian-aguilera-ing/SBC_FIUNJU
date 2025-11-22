import React from 'react';
import { ArquetipoInfo } from '@/types';
import {
  BatteryLow as BatteryLowIcon,
  Clock as ClockIcon,
  Bus as BusIcon,
  TrendingUp as TrendingUpIcon,
  WifiOff as WifiOffIcon,
  Rocket as RocketIcon,
  Target as TargetIcon
} from 'lucide-react';

const WidgetDinamico = ({ arquetipo }: { arquetipo: ArquetipoInfo }) => {
    const color = arquetipo.color;

    switch (color) {
        case "red": // Superviviente
            return (
                <div className="border-l-4 border-red-500 bg-red-900/20 p-4 rounded mb-4">
                    <h4 className="text-red-400 font-bold mb-2 flex items-center gap-2"><BatteryLowIcon className="w-5 h-5"/> Modo Ahorro Energía</h4>
                    <p className="text-xs text-gray-300">Tu lista de tareas está simplificada al máximo. Solo lo esencial.</p>
                </div>
            );
        case "orange": // Malabarista
            return (
                <div className="border-l-4 border-orange-500 bg-orange-900/20 p-4 rounded mb-4">
                    <h4 className="text-orange-400 font-bold mb-2 flex items-center gap-2"><ClockIcon className="w-5 h-5"/> Horario Familiar Bloqueado</h4>
                    <p className="text-xs text-gray-300">Recuerda: De 18hs a 21hs es tiempo familiar. No intentes estudiar ahí.</p>
                </div>
            );
        case "yellow": // Guerrero
             return (
                <div className="border-l-4 border-yellow-500 bg-yellow-900/20 p-4 rounded mb-4">
                    <h4 className="text-yellow-400 font-bold mb-2 flex items-center gap-2"><BusIcon className="w-5 h-5"/> Calculadora "Tiempo de Viaje"</h4>
                    <p className="text-xs text-gray-300">Has ganado +5hs de estudio esta semana aprovechando el viaje en bus.</p>
                </div>
            );
        case "green": // Equilibrado
             return (
                <div className="border-l-4 border-green-500 bg-green-900/20 p-4 rounded mb-4">
                    <h4 className="text-green-400 font-bold mb-2 flex items-center gap-2"><TrendingUpIcon className="w-5 h-5"/> Barra de Progreso "Promedio General"</h4>
                    <div className="w-full bg-gray-700 rounded-full h-2.5 mb-1">
                        <div className="bg-green-500 h-2.5 rounded-full" style={{ width: '70%' }}></div>
                    </div>
                    <p className="text-xs text-gray-300">Mantienes un ritmo excelente. ¡Sigue así!</p>
                </div>
            );
        case "blue": // Ermitaño
             return (
                <div className="border-l-4 border-blue-500 bg-blue-900/20 p-4 rounded mb-4">
                    <h4 className="text-blue-400 font-bold mb-2 flex items-center gap-2"><WifiOffIcon className="w-5 h-5"/> Mapa de Calor de Productividad</h4>
                    <p className="text-xs text-gray-300">Tu mayor concentración es de 23:00 a 03:00. Aprovecha el silencio nocturno.</p>
                </div>
            );
        case "violet": // Heredero
             return (
                <div className="border-l-4 border-violet-500 bg-violet-900/20 p-4 rounded mb-4">
                    <h4 className="text-violet-400 font-bold mb-2 flex items-center gap-2"><RocketIcon className="w-5 h-5"/> Planificador de Carrera Acelerada</h4>
                    <p className="text-xs text-gray-300">Estás adelantando materias del próximo año. ¡Excelente ritmo!</p>
                </div>
            );
        case "brown": // Padre/Madre
             return (
                <div className="border-l-4 border-amber-700 bg-amber-900/20 p-4 rounded mb-4">
                    <h4 className="text-amber-500 font-bold mb-2 flex items-center gap-2"><TargetIcon className="w-5 h-5"/> Bloques de "Micro-Objetivos"</h4>
                    <ul className="text-xs text-gray-300 list-disc pl-4">
                        <li>Leer 10 págs (15 min)</li>
                        <li>Resumir unidad 1 (20 min)</li>
                    </ul>
                </div>
            );
        default:
            return null;
    }
}

export default WidgetDinamico;
