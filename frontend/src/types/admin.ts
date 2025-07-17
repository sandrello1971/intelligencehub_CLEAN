// types/admin.ts
// Definizioni TypeScript per sistema amministrazione IntelligenceHUB

export interface TipoCommessa {
  id: string;
  nome: string;
  codice: string;
  descrizione?: string;
  sla_default_hours: number;
  template_milestones?: any;
  is_active: boolean;
  created_at: string;
}

export interface TipoCommessaCreate {
  nome: string;
  codice: string;
  descrizione?: string;
  sla_default_hours: number;
  is_active?: boolean;
}

export interface TipoCommessaUpdate {
  nome?: string;
  codice?: string;
  descrizione?: string;
  sla_default_hours?: number;
  is_active?: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export enum LoadingState {
  IDLE = 'idle',
  LOADING = 'loading',
  SUCCESS = 'success',
  ERROR = 'error'
}
