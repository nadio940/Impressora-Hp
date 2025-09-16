import { useQuery, useMutation, useQueryClient } from 'react-query';
import { alertsService } from '../services/alertsService';
import { Alert, AlertRule, AlertFilters } from '../types/alert';

export const useAlerts = (filters?: AlertFilters) => {
  const query = useQuery(
    ['alerts', filters],
    () => alertsService.getAlerts(filters),
    {
      refetchInterval: 30000, // Atualizar a cada 30 segundos
      keepPreviousData: true,
    }
  );

  // Contar alertas não lidos
  const unreadAlertsCount = query.data?.results?.filter(
    (alert: Alert) => alert.status === 'new'
  ).length || 0;

  return {
    ...query,
    unreadAlertsCount,
  };
};

export const useAlert = (id: number) => {
  return useQuery(
    ['alert', id],
    () => alertsService.getAlert(id),
    {
      enabled: !!id,
    }
  );
};

export const useAlertRules = () => {
  return useQuery(
    'alert-rules',
    alertsService.getAlertRules,
    {
      refetchInterval: 60000, // Atualizar a cada minuto
    }
  );
};

export const useCreateAlertRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation(alertsService.createAlertRule, {
    onSuccess: () => {
      queryClient.invalidateQueries('alert-rules');
    },
  });
};

export const useUpdateAlertRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation(alertsService.updateAlertRule, {
    onSuccess: () => {
      queryClient.invalidateQueries('alert-rules');
    },
  });
};

export const useDeleteAlertRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation(alertsService.deleteAlertRule, {
    onSuccess: () => {
      queryClient.invalidateQueries('alert-rules');
    },
  });
};

export const useAcknowledgeAlert = () => {
  const queryClient = useQueryClient();
  
  return useMutation(alertsService.acknowledgeAlert, {
    onSuccess: () => {
      queryClient.invalidateQueries('alerts');
    },
  });
};

export const useResolveAlert = () => {
  const queryClient = useQueryClient();
  
  return useMutation(alertsService.resolveAlert, {
    onSuccess: () => {
      queryClient.invalidateQueries('alerts');
    },
  });
};

export const useBulkAcknowledgeAlerts = () => {
  const queryClient = useQueryClient();
  
  return useMutation(alertsService.bulkAcknowledgeAlerts, {
    onSuccess: () => {
      queryClient.invalidateQueries('alerts');
    },
  });
};

export const useToggleAlertRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation(alertsService.toggleAlertRule, {
    onSuccess: () => {
      queryClient.invalidateQueries('alert-rules');
    },
  });
};

export const useTestAlertRule = () => {
  return useMutation(alertsService.testAlertRule);
};

export const useAlertStatistics = () => {
  return useQuery(
    'alert-statistics',
    alertsService.getStatistics,
    {
      refetchInterval: 60000, // Atualizar a cada minuto
    }
  );
};
