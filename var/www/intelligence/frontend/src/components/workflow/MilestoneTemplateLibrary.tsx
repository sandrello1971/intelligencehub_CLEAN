// components/workflow/MilestoneTemplateLibrary.tsx
// Libreria Template Milestone Riutilizzabili - IntelligenceHUB
// IMPLEMENTAZIONE COMPLETA CON GESTIONE TASK
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Schedule as ScheduleIcon,
  Assignment as AssignmentIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { apiClient } from '../../services/api';
import MilestoneTaskManager from './MilestoneTaskManager';

const MilestoneTemplateLibrary: React.FC = () => {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Task Manager state
  const [showTaskManager, setShowTaskManager] = useState(false);
  const [selectedMilestoneForTasks, setSelectedMilestoneForTasks] = useState<any>(null);
  
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<any>(null);
  const [formData, setFormData] = useState({
    nome: '',
    descrizione: '',
    durata_stimata_giorni: null as number | null,
    categoria: 'standard',
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/admin/milestone-templates/');
      if (response.success && response.data) {
        setTemplates(response.data);
      } else {
        setError('Errore caricamento milestone templates');
      }
    } catch (error) {
      console.error('Errore caricamento templates:', error);
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  // ===== TASK MANAGER HANDLERS =====
  
  const handleOpenTaskManager = (template: any) => {
    setSelectedMilestoneForTasks(template);
    setShowTaskManager(true);
  };

  const handleCloseTaskManager = () => {
    setShowTaskManager(false);
    setSelectedMilestoneForTasks(null);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ m: 0 }}>
          📋 Milestone Templates
        </Typography>
      </Box>

      {/* Messages */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && templates.length === 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Templates Grid */}
      <Grid container spacing={3}>
        {templates.map((template) => (
          <Grid item xs={12} sm={6} md={4} key={template.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" component="h2" gutterBottom>
                  {template.nome}
                </Typography>
                
                {template.descrizione && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {template.descrizione}
                  </Typography>
                )}

                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  <Chip
                    icon={<ScheduleIcon />}
                    label={`${template.sla_giorni || 'N/A'} giorni`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    icon={<AssignmentIcon />}
                    label={`${template.task_count} task`}
                    size="small"
                    color="secondary"
                    variant="outlined"
                  />
                </Box>
              </CardContent>

              <CardActions>
                <Button
                  size="small"
                  onClick={() => handleOpenTaskManager(template)}
                  disabled={loading}
                  startIcon={<AssignmentIcon />}
                >
                  📋 Ordina Task
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Task Manager Dialog */}
      {showTaskManager && selectedMilestoneForTasks && (
        <MilestoneTaskManager
          milestoneId={selectedMilestoneForTasks.id}
          milestoneName={selectedMilestoneForTasks.nome}
          open={showTaskManager}
          onClose={handleCloseTaskManager}
          onTasksUpdated={() => {
            loadTemplates();
          }}
        />
      )}
    </Box>
  );
};

export default MilestoneTemplateLibrary;
