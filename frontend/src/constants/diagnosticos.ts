// Diagnósticos hardcoded para cada perfil de estudiante
// Estos se usan como fallback si el backend no proporciona diagnósticos

export const DIAGNOSTICOS_POR_PERFIL: Record<string, string> = {
    "Perfil Crítico": `Tu perfil tiene 'muy poco tiempo para estudiar'. No se permiten errores.
* trabajas tiempo completo
* Vivis lejos
* vivis solo
* tenes hijo/s`,

    "Perfil Bajo": `Tiene un poco más de tiempo gracias al apoyo familiar y vivir cerca.
* trabajas tiempo completo
* Vivis en Capital
* No vives solo
* tenes hijo/s`,

    "Perfil Medio Bajo": `Tiene tiempo, pero viajar largas distancias más las tareas domésticas te quitan energía.
* trabajas medio tiempo
* Vivis en el Interior
* Vivis solo
* No tenes hijo/s`,

    "Perfil Equilibrado": `Es el balance perfecto. Puede asumir carga, pero no extrema.
* trabajas medio tiempo
* Vivis en Capital
* No vivis solo
* No tenes hijo/s`,

    "Perfil Medio Alto": `Tiempo completo, pero vivir solo viene con tareas domésticas y viajar limita la 'energía mental'.
* No trabajas
* Vivis en el Interior
* Vivis solo
* No tenes hijo/s`,

    "Perfil Super Alto": `Disponibilidad total. Su única restricción es su propia capacidad de concentración.
* No trabajas
* Vivis en Capital
* No vivis solo
* No tenes hijo/s`,

    "Perfil Atípico": `Tiempo libre de trabajo, pero al tener hijos perdes el 'flujo' de estudio constante.
* No trabajas
* Vivis en Capital
* No vivis solo
* Tenes hijo/s`
};

/**
 * Obtiene el diagnóstico para un perfil específico
 * @param nombrePerfil - Nombre del perfil (ej: "Perfil Equilibrado")
 * @param diagnosticoBackend - Diagnóstico que viene del backend (opcional)
 * @returns El diagnóstico del perfil o un mensaje por defecto
 */
export function obtenerDiagnostico(nombrePerfil: string, diagnosticoBackend?: string): string {
    // Si el backend proporciona un diagnóstico válido, usarlo
    if (diagnosticoBackend && diagnosticoBackend.trim() !== "" && diagnosticoBackend !== "Diagnóstico no disponible.") {
        return diagnosticoBackend;
    }

    // Buscar en los diagnósticos hardcoded
    const diagnostico = DIAGNOSTICOS_POR_PERFIL[nombrePerfil];

    if (diagnostico) {
        return diagnostico;
    }

    // Fallback final
    return "Diagnóstico no disponible.";
}
