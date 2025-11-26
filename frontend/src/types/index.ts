export interface MateriaOntology {
  uri: string;
  label: string;
}

export interface UserMateria {
  id: number;
  materia_uri: string;
  estado: string;
}

export interface MateriaPerfil extends UserMateria {
  label: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  materias_cursadas: UserMateria[];
}

export interface ConsejoResponse {
  consejos: string[];
}

export interface TopicoOntology {
  uri: string;
  label: string;
}

export enum TipoAlerta {
  RIESGO_REGULARIDAD = "riesgo_regularidad",
  CUELLO_DE_BOTELLA = "cuello_de_botella",
  SOBRECARGA = "sobrecarga",
}

export interface Alerta {
  tipo: TipoAlerta;
  mensaje: string;
  materia_uri: string | null;
  materia_label: string | null;
}

export interface MateriaRecomendada {
  uri: string;
  label: string;
  score: number;
  año: number;
  dificultad: number;
  desbloquea_count: number;
  creditos_otorgados: number;
}

export interface ArquetipoInfo {
  nombre: string;
  color: string;
  consejos: string[];
}

export interface PlanCursadaRecomendado {
  plan_recomendado: MateriaRecomendada[];
  materias_omitidas: MateriaRecomendada[];
  arquetipo: ArquetipoInfo;
  consejos_adicionales: string[];
}

export interface MateriaExamenRecomendada {
  uri: string;
  label: string;
  dificultad_examen_label: string;
  dificultad_examen_valor: number;
  modalidades: string[];
  esta_habilitada: boolean;
  motivo_bloqueo: string | null;
  correlativas_pendientes: string[];
  consejo_personalizado: string | null;
}

export interface PlanExamenRecomendado {
  plan_recomendado: MateriaExamenRecomendada[];
  consejos_adicionales: string[];
  arquetipo: ArquetipoInfo;
}
