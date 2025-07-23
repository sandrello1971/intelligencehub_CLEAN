// services/milestoneTemplateApi.ts
// API Client per Milestone Templates - IntelligenceHUB

import { BaseApiClient, ApiResponse } from './baseApi';

export interface MilestoneTemplate {
  id: number;
  nome: string;
  descrizione?: string;
  durata_stimata_giorni?: number;
  categoria: string;
  sla_giorni: number; // Calcolato automaticamente dai task
  created_at: string;
  task_count: number;
  usage_count: number;
}

export interface TaskTemplate {
  id: string;
  nome: string;
  descrizione?: string;
  ordine: number;
  sla_hours: number;
  priorita: string;
  is_required: boolean;
}

export interface MilestoneTemplateCreateData {
  nome: string;
  descrizione?: string;
  durata_stimata_giorni?: number;
  categoria: string;
}

export interface TaskAssignmentData {
  ordine: number;
  is_required: boolean;
}

class MilestoneTemplateApiClient extends BaseApiClient {
  
  // ===== MILESTONE TEMPLATES CRUD =====
  
  async createMilestoneTemplate(data: MilestoneTemplateCreateData): Promise<ApiResponse<MilestoneTemplate>> {
    return this.request('/api/v1/admin/milestone-templates/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listMilestoneTemplates(): Promise<ApiResponse<MilestoneTemplate[]>> {
    return this.request('/api/v1/admin/milestone-templates/');
  }

  async deleteMilestoneTemplate(templateId: number): Promise<ApiResponse<{ message: string }>> {
    return this.request(`/api/v1/admin/milestone-templates/${templateId}`, {
      method: 'DELETE',
    });
  }

  // ===== TASK MANAGEMENT =====
  
  async getMilestoneTemplateTasks(templateId: number): Promise<ApiResponse<{
    tasks: TaskTemplate[];
    milestone_sla_giorni: number;
    total_sla_hours: number;
  }>> {
    return this.request(`/api/v1/admin/milestone-templates/${templateId}/tasks`);
  }

  async assignTaskToMilestone(
    templateId: number, 
    taskId: string, 
    data: TaskAssignmentData
  ): Promise<ApiResponse<{ message: string; milestone_sla_giorni: number }>> {
    return this.request(`/api/v1/admin/milestone-templates/${templateId}/tasks/${taskId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async removeTaskFromMilestone(
    templateId: number, 
    taskId: string
  ): Promise<ApiResponse<{ message: string; milestone_sla_giorni: number }>> {
    return this.request(`/api/v1/admin/milestone-templates/${templateId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  // ===== UTILITY =====
  
  async recalculateMilestoneSLA(templateId: number): Promise<ApiResponse<{
    milestone_template_id: number;
    calculated_sla_giorni: number;
    message: string;
  }>> {
    return this.request(`/api/v1/admin/milestone-templates/${templateId}/recalculate-sla`, {
      method: 'PUT',
    });
  }
}

export const milestoneTemplateApi = new MilestoneTemplateApiClient();
export default milestoneTemplateApi;
