import apiClient, { formatApiResponse, handleApiError } from './api';
import { Printer, PrinterFilters, PrinterCreateData, PrinterUpdateData } from '../types/printer';

interface PrintersResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Printer[];
}

interface ConnectionTestData {
  id: number;
}

interface ConnectionTestResponse {
  connected: boolean;
  message: string;
  last_seen?: string;
}

interface DiscoveryData {
  ip_range: string;
  timeout?: number;
  snmp_community?: string;
}

interface DiscoveryResponse {
  discovered_printers: any[];
  count: number;
}

interface PrinterStatistics {
  total_printers: number;
  active_printers: number;
  offline_printers: number;
  maintenance_printers: number;
  laser_printers: number;
  inkjet_printers: number;
  multifunction_printers: number;
}

export const printersService = {
  // Listar impressoras
  getPrinters: async (filters?: PrinterFilters): Promise<PrintersResponse> => {
    try {
      const params = new URLSearchParams();
      
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            params.append(key, value.toString());
          }
        });
      }
      
      const response = await apiClient.get('/printers/', { params });
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Obter impressora por ID
  getPrinter: async (id: number): Promise<Printer> => {
    try {
      const response = await apiClient.get(`/printers/${id}/`);
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Criar impressora
  createPrinter: async (data: PrinterCreateData): Promise<Printer> => {
    try {
      const response = await apiClient.post('/printers/', data);
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Atualizar impressora
  updatePrinter: async ({ id, ...data }: PrinterUpdateData & { id: number }): Promise<Printer> => {
    try {
      const response = await apiClient.patch(`/printers/${id}/`, data);
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Deletar impressora
  deletePrinter: async (id: number): Promise<void> => {
    try {
      await apiClient.delete(`/printers/${id}/`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Testar conexão
  testConnection: async ({ id }: ConnectionTestData): Promise<ConnectionTestResponse> => {
    try {
      const response = await apiClient.post(`/printers/${id}/test_connection/`);
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Atualizar status
  updateStatus: async (id: number, status: string, notes?: string): Promise<void> => {
    try {
      await apiClient.post(`/printers/${id}/update_status/`, {
        status,
        notes,
      });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Obter suprimentos
  getSupplies: async (id: number): Promise<any[]> => {
    try {
      const response = await apiClient.get(`/printers/${id}/supplies/`);
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Atualizar suprimentos
  refreshSupplies: async ({ id }: { id: number }): Promise<void> => {
    try {
      await apiClient.post(`/printers/${id}/refresh_supplies/`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Descobrir impressoras
  discoverPrinters: async (data: DiscoveryData): Promise<DiscoveryResponse> => {
    try {
      const response = await apiClient.post('/printers/discover/', data);
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Obter estatísticas
  getStatistics: async (): Promise<PrinterStatistics> => {
    try {
      const response = await apiClient.get('/printers/statistics/');
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
