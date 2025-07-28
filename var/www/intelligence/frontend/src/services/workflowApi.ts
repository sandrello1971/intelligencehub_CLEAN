// services/workflowApi.ts
// API Service per Workflow Management - IntelligenceHUB Frontend

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface Articolo {
  id: number;
  codice: string;
  nome: string;
  descrizione: string;
  tipo_prodotto: 'semplice' | 'composito';
  prezzo_base: number | null;
  durata_mesi: number | null;
  sla_default_hours: number;
  template_milestones: any;
  attivo: boolean;
  created_at: string;
  updated_at: string;
}

export interface KitCommerciale {
  id: number;
  nome: string;
  descrizione: string;
  articolo_principale_id: number | null;
  attivo: boolean;
  created_at: string;
}

export interface WorkflowTemplate {
  id: number;
  nome: string;
  descrizione: string;
  durata_stimata_giorni: number | null;
  ordine: number;
  wkf_code: string | null;
  wkf_description: string | null;
  attivo: boolean;
  created_at: string;
}

export interface WorkflowMilestone {
  id: number;
  workflow_template_id: number;
  nome: string;
  descrizione: string;
  ordine: number;
  durata_stimata_giorni: number | null;
  sla_giorni: number | null;
  warning_giorni: number;
  escalation_giorni: number;
  tipo_milestone: string;
  auto_generate_tickets: boolean;
  created_at: string;
}

export interface TaskTemplate {
  id: number;
  milestone_id: number;
  nome: string;
  descrizione: string;
  ordine: number;
  durata_stimata_ore: number | null;
  ruolo_responsabile: string | null;
  obbligatorio: boolean;
  tipo_task: string;
  checklist_template: any[];
  created_at: string;
}

export interface CompleteWorkflow extends WorkflowTemplate {
  milestones: (WorkflowMilestone & { task_templates: TaskTemplate[] })[];
}

class WorkflowApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    // Aggiungi token se presente
    const token = localStorage.getItem('token');
    if (token) {
      (defaultHeaders as any)['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error('API Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // ===== ARTICOLI =====
  async getArticoli(attivo: boolean = true): Promise<ApiResponse<Articolo[]>> {
    return this.request<Articolo[]>(`/admin/workflow-config/articoli?attivo=${attivo}`);
  }

  async getArticolo(id: number): Promise<ApiResponse<Articolo>> {
    return this.request<Articolo>(`/admin/workflow-config/articoli/${id}`);
  }

  // ===== KIT COMMERCIALI =====
  async getKitCommerciali(attivo: boolean = true): Promise<ApiResponse<KitCommerciale[]>> {
    return this.request<KitCommerciale[]>(`/admin/workflow-config/kit-commerciali?attivo=${attivo}`);
  }

  // ===== WORKFLOW TEMPLATES =====
  async getWorkflowTemplates(attivo: boolean = true): Promise<ApiResponse<WorkflowTemplate[]>> {
    return this.request<WorkflowTemplate[]>(`/admin/workflow-config/workflow-templates?attivo=${attivo}`);
  }

  async getWorkflowTemplate(id: number): Promise<ApiResponse<CompleteWorkflow>> {
    return this.request<CompleteWorkflow>(`/admin/workflow-config/workflow-templates/${id}`);
  }

  async createWorkflowTemplate(data: Partial<WorkflowTemplate>): Promise<ApiResponse<WorkflowTemplate>> {
    return this.request<WorkflowTemplate>('/admin/workflow-config/workflow-templates', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateWorkflowTemplate(id: number, data: Partial<WorkflowTemplate>): Promise<ApiResponse<WorkflowTemplate>> {
    return this.request<WorkflowTemplate>(`/admin/workflow-config/workflow-templates/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // ===== WORKFLOW MILESTONES =====
  async createWorkflowMilestone(data: Partial<WorkflowMilestone>): Promise<ApiResponse<WorkflowMilestone>> {
    return this.request<WorkflowMilestone>('/admin/workflow-config/workflow-milestones', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ===== TASK TEMPLATES =====
  async createTaskTemplate(data: Partial<TaskTemplate>): Promise<ApiResponse<TaskTemplate>> {
    return this.request<TaskTemplate>('/admin/workflow-config/milestone-task-templates', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ===== WORKFLOW MANAGEMENT =====
  async cloneWorkflow(workflowId: number, data: {
    new_name: string;
    clone_milestones: boolean;
    clone_tasks: boolean;
  }): Promise<ApiResponse<any>> {
    return this.request(`/admin/workflow-management/workflows/${workflowId}/clone`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async validateWorkflow(workflowId: number): Promise<ApiResponse<any>> {
    return this.request(`/admin/workflow-management/workflows/${workflowId}/validate`);
  }

  async getWorkflowStatistics(): Promise<ApiResponse<any>> {
    return this.request('/admin/workflow-management/statistics/overview');
  }

  // ===== MILESTONE TEMPLATES STANDALONE =====
  async createMilestoneTemplate(data: {
    nome: string;
    descrizione: string;
    durata_stimata_giorni: number | null;
    categoria: string;
  }): Promise<ApiResponse<any>> {
    return this.request("/admin/workflow-config/milestone-templates", {
      method: "POST", 
      body: JSON.stringify(data),
    });
  }
}

export const workflowApi = new WorkflowApiClient();
export default workflowApi;
