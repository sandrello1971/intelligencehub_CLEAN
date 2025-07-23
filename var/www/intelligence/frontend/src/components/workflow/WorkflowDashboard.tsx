// components/workflow/WorkflowDashboard.tsx
// Dashboard overview per sistema Workflow - IntelligenceHUB

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button
} from '@mui/material';
import {
  Timeline,
  Settings,
  CheckCircle,
  Warning,
  Error,
  Refresh,
  TrendingUp,
  Assignment,
  Speed
} from '@mui/icons-material';
import { workflowApi, WorkflowTemplate } from '../../services/workflowApi';

interface WorkflowDashboardProps {
  workflows: WorkflowTemplate[];
  onReload: () => void;
}

interface WorkflowStats {
  configuration_stats: {
    active_workflows: number;
    total_milestones: number;
    total_task_templates: number;
    active_articoli: number;
    active_kits: number;
    workflows_with_milestones: number;
    milestones_with_tasks: number;
    configuration_completeness: number;
  };
  usage_stats: {
    workflows_in_use: number;
    most_used_milestone: string | null;
    avg_workflow_completion_days: number;
  };
  recommendations: string[];
}

const WorkflowDashboard: React.FC<WorkflowDashboardProps> = ({ workflows, onReload }) => {
  const [stats, setStats] = useState<WorkflowStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, [workflows]);

  const loadStats = async () => {
    setLoading(true);
    try {
      const response = await workflowApi.getWorkflowStatistics();
      if (response.success && response.data) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('Errore caricamento statistiche:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (completeness: number) => {
    if (completeness >= 80) return 'success';
    if (completeness >= 60) return 'warning';
    return 'error';
  };

  const getStatusIcon = (completeness: number) => {
    if (completeness >= 80) return <CheckCircle color="success" />;
    if (completeness >= 60) return <Warning color="warning" />;
    return <Error color="error" />;
  };

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Caricamento statistiche...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header con azioni */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          Dashboard Workflow System
        </Typography>
        <IconButton onClick={onReload} sx={{ backgroundColor: '#f5f5f5' }}>
          <Refresh />
        </IconButton>
      </Box>

      <Grid container spacing={3}>
        {/* Statistiche Principali */}
        <Grid item xs={12} md={3}>
          <Card sx={{ backgroundColor: '#e3f2fd', borderRadius: 3 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Timeline sx={{ fontSize: 40, color: '#1976d2', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#1976d2' }}>
                {workflows.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Workflow Templates
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ backgroundColor: '#e8f5e8', borderRadius: 3 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assignment sx={{ fontSize: 40, color: '#2e7d32', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#2e7d32' }}>
                {stats?.configuration_stats.total_milestones || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Milestone Totali
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ backgroundColor: '#fff3e0', borderRadius: 3 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Settings sx={{ fontSize: 40, color: '#f57c00', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#f57c00' }}>
                {stats?.configuration_stats.total_task_templates || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Task Templates
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ backgroundColor: '#fce4ec', borderRadius: 3 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Speed sx={{ fontSize: 40, color: '#c2185b', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#c2185b' }}>
                {stats?.configuration_stats.configuration_completeness || 0}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Completezza Config
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Status Configurazione */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardHeader
              title="Stato Configurazione"
              avatar={
                stats ? getStatusIcon(stats.configuration_stats.configuration_completeness) : <Settings />
              }
            />
            <CardContent>
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Completezza Sistema</Typography>
                  <Typography variant="body2">
                    {stats?.configuration_stats.configuration_completeness || 0}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={stats?.configuration_stats.configuration_completeness || 0}
                  color={stats ? getStatusColor(stats.configuration_stats.configuration_completeness) : 'primary'}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {stats?.configuration_stats.workflows_with_milestones || 0}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Workflow con Milestone
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {stats?.configuration_stats.milestones_with_tasks || 0}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Milestone con Task
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Raccomandazioni */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardHeader
              title="Raccomandazioni Sistema"
              avatar={<TrendingUp color="primary" />}
            />
            <CardContent>
              {stats?.recommendations && stats.recommendations.length > 0 ? (
                <List>
                  {stats.recommendations.map((recommendation, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Chip 
                          label={index + 1} 
                          size="small" 
                          color="primary" 
                          sx={{ minWidth: 24, height: 24 }}
                        />
                      </ListItemIcon>
                      <ListItemText 
                        primary={recommendation}
                        primaryTypographyProps={{ fontSize: '0.9rem' }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <CheckCircle color="success" sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="body1" color="success.main">
                    Sistema configurato correttamente!
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Nessuna raccomandazione al momento
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3 }}>
            <CardHeader title="Azioni Rapide" />
            <CardContent>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<Timeline />}
                  size="small"
                  onClick={() => {/* Navigate to workflow templates */}}
                >
                  Gestisci Workflow
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Settings />}
                  size="small"
                  onClick={() => {/* Open configuration wizard */}}
                >
                  Configuration Wizard
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Assignment />}
                  size="small"
                  onClick={() => {/* View documentation */}}
                >
                  Documentazione
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default WorkflowDashboard;
