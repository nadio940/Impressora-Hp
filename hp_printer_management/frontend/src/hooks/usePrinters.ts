import { useQuery, useMutation, useQueryClient } from 'react-query';
import { printersService } from '../services/printersService';
import { Printer, PrinterFilters } from '../types/printer';

export const usePrinters = (filters?: PrinterFilters) => {
  return useQuery(
    ['printers', filters],
    () => printersService.getPrinters(filters),
    {
      refetchInterval: 30000, // Atualizar a cada 30 segundos
      keepPreviousData: true,
    }
  );
};

export const usePrinter = (id: number) => {
  return useQuery(
    ['printer', id],
    () => printersService.getPrinter(id),
    {
      enabled: !!id,
      refetchInterval: 10000, // Atualizar a cada 10 segundos para detalhes
    }
  );
};

export const useCreatePrinter = () => {
  const queryClient = useQueryClient();
  
  return useMutation(printersService.createPrinter, {
    onSuccess: () => {
      queryClient.invalidateQueries('printers');
    },
  });
};

export const useUpdatePrinter = () => {
  const queryClient = useQueryClient();
  
  return useMutation(printersService.updatePrinter, {
    onSuccess: (data) => {
      queryClient.invalidateQueries('printers');
      queryClient.invalidateQueries(['printer', data.id]);
    },
  });
};

export const useDeletePrinter = () => {
  const queryClient = useQueryClient();
  
  return useMutation(printersService.deletePrinter, {
    onSuccess: () => {
      queryClient.invalidateQueries('printers');
    },
  });
};

export const useTestPrinterConnection = () => {
  return useMutation(printersService.testConnection);
};

export const useDiscoverPrinters = () => {
  return useMutation(printersService.discoverPrinters);
};

export const useRefreshSupplies = () => {
  const queryClient = useQueryClient();
  
  return useMutation(printersService.refreshSupplies, {
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries(['printer', variables.id]);
      queryClient.invalidateQueries('printers');
    },
  });
};

export const usePrinterStatistics = () => {
  return useQuery(
    'printer-statistics',
    printersService.getStatistics,
    {
      refetchInterval: 60000, // Atualizar a cada minuto
    }
  );
};
