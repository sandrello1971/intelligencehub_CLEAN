// services/admin/tipiCommesseService.ts
// Service per gestione Tipi Commesse - IntelligenceHUB

import { apiClient, ApiResponse } from '../api';
import { 
  TipoCommessa, 
  TipoCommessaCreate, 
  TipoCommessaUpdate,
  PaginatedResponse 
} from '../../types/admin';

class TipiCommesseService {
  private readonly basePath = '/admin/tipi-commesse';

  async getAll(): Promise<ApiResponse<TipoCommessa[]>> {
    return apiClient.get<TipoCommessa[]>(this.basePath);
  }

  async getById(id: string): Promise<ApiResponse<TipoCommessa>> {
    return apiClient.get<TipoCommessa>(`${this.basePath}/${id}`);
  }

  async create(data: TipoCommessaCreate): Promise<ApiResponse<TipoCommessa>> {
    return apiClient.post<TipoCommessa>(this.basePath, data);
  }

  async update(id: string, data: TipoCommessaUpdate): Promise<ApiResponse<TipoCommessa>> {
    return apiClient.put<TipoCommessa>(`${this.basePath}/${id}`, data);
  }

  async delete(id: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`${this.basePath}/${id}`);
  }

  async toggleActive(id: string, isActive: boolean): Promise<ApiResponse<TipoCommessa>> {
    return apiClient.patch<TipoCommessa>(`${this.basePath}/${id}/toggle-active`, {
      is_active: isActive
    });
  }
}

const tipiCommesseService = new TipiCommesseService();
export default tipiCommesseService;
