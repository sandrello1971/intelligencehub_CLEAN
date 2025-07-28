// frontend/src/services/ticketApi.ts
export interface Company {
  id: number;
  name: string;
  partita_iva?: string;
  codice_fiscale?: string;
  settore?: string;
  email?: string;
  telefono?: string;
}

export interface KitCommerciale {
  id: number;
  nome: string;
  descrizione?: string;
  articolo_principale_id?: number;
  attivo: boolean;
  articoli_count: number;
  articoli_inclusi?: any[];
}

export interface CommercialTicketRequest {
  company_id: number;
  kit_commerciale_id: number;
  notes?: string;
  owner_id?: string;
}

export interface CommercialTicketResponse {
  success: boolean;
  commessa_id: string;
  commessa_code: string;
  kit_info: {
    nome: string;
    id: number;
  };
  company_info: {
    nome: string;
    id: number;
  };
  servizi_inclusi: string[];
  crm_activity_id?: number;
  message: string;
}

export interface TicketHierarchy {
  cliente: string;
  company_id: number;
  tickets_padre: any[];
  tickets_figli: any[];
  statistics: {
    total_commesse: number;
    total_tickets_padre: number;
    total_tickets_figli: number;
  };
}

class TicketApiService {
  private baseUrl = '/api/v1';

  // Cerca aziende con filtro
  async searchCompanies(query: string): Promise<{ companies: Company[] }> {
    const response = await fetch(`${this.baseUrl}/companies/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error('Errore durante la ricerca aziende');
    }
    return response.json();
  }

  // Ottieni tutti i kit commerciali attivi
  async getKitCommerciali(): Promise<{ kit_commerciali: KitCommerciale[] }> {
    const response = await fetch(`${this.baseUrl}/kit-commerciali/?attivo=true`);
    if (!response.ok) {
      throw new Error('Errore durante il caricamento dei kit commerciali');
    }
    return response.json();
  }

  // Crea ticket commerciale
  async createCommercialTicket(
    request: CommercialTicketRequest,
    token?: string
  ): Promise<CommercialTicketResponse> {
    const response = await fetch(`${this.baseUrl}/tickets/commercial/create-commessa`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Errore HTTP: ${response.status}`);
    }

    return response.json();
  }

  // Ottieni gerarchia ticket per azienda
  async getTicketHierarchy(companyId: number): Promise<TicketHierarchy> {
    const response = await fetch(`${this.baseUrl}/tickets/commercial/hierarchy/${companyId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Errore durante il caricamento della gerarchia ticket');
    }

    return response.json();
  }

  // Ottieni dettagli ticket
  async getTicketDetail(ticketId: number, token?: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/tickets/${ticketId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Errore durante il caricamento del ticket');
    }

    return response.json();
  }

  // Lista ticket con filtri
  async listTickets(filters?: {
    priority?: string;
    status?: string;
    customer_name?: string;
  }, token?: string): Promise<any[]> {
    const params = new URLSearchParams();
    if (filters?.priority) params.append('priority', filters.priority);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.customer_name) params.append('customer_name', filters.customer_name);

    const url = `${this.baseUrl}/tickets/?${params.toString()}`;
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Errore durante il caricamento dei ticket');
    }

    return response.json();
  }
}

// Singleton instance
export const ticketApi = new TicketApiService();
export default ticketApi;
