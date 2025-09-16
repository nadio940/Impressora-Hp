import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
} from '@mui/material';
import {
  Print as PrintIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { usePrinters } from '../hooks/usePrinters';
import { useAlerts } from '../hooks/useAlerts';
import { useDashboard } from '../hooks/useDashboard';
import LoadingSpinner from '../components/LoadingSpinner';
import StatCard from '../components/StatCard';

const Dashboard: React.FC = () => {
  const { data: printersData, isLoading: printersLoading } = usePrinters();
  const { data: alertsData, isLoading: alertsLoading } = useAlerts();
  const { data: dashboardData, isLoading: dashboardLoading } = useDashboard();

  if (printersLoading || alertsLoading || dashboardLoading) {
    return <LoadingSpinner />;
  }

  const printers = printersData?.results || [];
  const alerts = alertsData?.results || [];
  const stats = dashboardData?.statistics || {};

  // Dados para gráficos
  const consumptionData = dashboardData?.consumption_trend || [];
  const printerStatusData = [
    { name: 'Ativas', value: stats.active_printers || 0, color: '#4caf50' },
    { name: 'Offline', value: stats.offline_printers || 0, color: '#f44336' },
    { name: 'Manutenção', value: stats.maintenance_printers || 0, color: '#ff9800' },
  ];

  const recentAlerts = alerts.slice(0, 5);
  const activePrinters = printers.filter(p => p.status === 'active').slice(0, 5);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total de Impressoras"
            value={stats.total_printers || 0}
            icon={<PrintIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Impressoras Ativas"
            value={stats.active_printers || 0}
            icon={<CheckCircleIcon />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Alertas Ativos"
            value={stats.active_alerts || 0}
            icon={<WarningIcon />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Trabalhos Hoje"
            value={stats.jobs_today || 0}
            icon={<PrintIcon />}
            color="info"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Gráfico de Consumo */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Tendência de Consumo (7 dias)
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={consumptionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="pages" 
                      stroke="#8884d8" 
                      strokeWidth={2}
                      name="Páginas Impressas"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="toner_consumed" 
                      stroke="#82ca9d" 
                      strokeWidth={2}
                      name="Toner Consumido (%)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Status das Impressoras */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Status das Impressoras
              </Typography>
              <Box sx={{ height: 250 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={printerStatusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {printerStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
              <Box sx={{ mt: 2 }}>
                {printerStatusData.map((item, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        backgroundColor: item.color,
                        borderRadius: '50%',
                        mr: 1,
                      }}
                    />
                    <Typography variant="body2">
                      {item.name}: {item.value}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Alertas Recentes */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Alertas Recentes
                </Typography>
                <Button size="small" href="/alerts">
                  Ver Todos
                </Button>
              </Box>
              <List>
                {recentAlerts.length > 0 ? (
                  recentAlerts.map((alert) => (
                    <ListItem key={alert.id} divider>
                      <ListItemIcon>
                        {alert.severity === 'critical' ? (
                          <ErrorIcon color="error" />
                        ) : (
                          <WarningIcon color="warning" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={alert.title}
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="caption">
                              {alert.printer_name}
                            </Typography>
                            <Chip 
                              label={alert.severity} 
                              size="small" 
                              color={alert.severity === 'critical' ? 'error' : 'warning'}
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                  ))
                ) : (
                  <ListItem>
                    <ListItemText
                      primary="Nenhum alerta recente"
                      secondary="Todas as impressoras estão funcionando normalmente"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Impressoras Ativas */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Impressoras Ativas
                </Typography>
                <Button size="small" href="/printers">
                  Ver Todas
                </Button>
              </Box>
              <List>
                {activePrinters.length > 0 ? (
                  activePrinters.map((printer) => (
                    <ListItem key={printer.id} divider>
                      <ListItemIcon>
                        <CheckCircleIcon color="success" />
                      </ListItemIcon>
                      <ListItemText
                        primary={printer.name}
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="caption">
                              {printer.location || printer.ip_address}
                            </Typography>
                            <Chip 
                              label={`Toner: ${printer.toner_levels?.toner_black || 0}%`} 
                              size="small" 
                              color="primary"
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                  ))
                ) : (
                  <ListItem>
                    <ListItemText
                      primary="Nenhuma impressora ativa"
                      secondary="Verifique as conexões de rede"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
