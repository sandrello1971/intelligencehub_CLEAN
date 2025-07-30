
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
  
  // Form states
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<any | null>(null);
  const [formData, setFormData] = useState({
    nome: '',
    descrizione: '',
    durata_stimata_giorni: undefined as number | undefined,
    categoria: 'standard',
  });

  // Task management states
  const [selectedTemplate, setSelectedTemplate] = useState<any | null>(null);
  const [templateTasks, setTemplateTasks] = useState<any[]>([]);
  const [showTaskDialog, setShowTaskDialog] = useState(false);
  const [availableTasks, setAvailableTasks] = useState<any[]>([]);
  const [showAddTaskDialog, setShowAddTaskDialog] = useState(false);
  const [selectedTaskToAdd, setSelectedTaskToAdd] = useState<any | null>(null);

  // Task Order Manager states
  const [showTaskManager, setShowTaskManager] = useState(false);
  const [selectedMilestoneForTasks, setSelectedMilestoneForTasks] = useState<any>(null);

  useEffect(() => {
    loadTemplates();
    loadAvailableTasks();
  }, []);

  // Clear messages after time
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const loadTemplates = async () => {
    console.log("=== CALLING loadTemplates ===");
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

  const resetForm = () => {
    setFormData({ nome: '', descrizione: '', durata_stimata_giorni: undefined, categoria: 'standard' });
    setEditingTemplate(null);
  };

  const handleCreateOrUpdateTemplate = async () => {
    if (!formData.nome.trim()) {
      setError('Nome template obbligatorio');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      let response;
      
      if (editingTemplate) {
        // UPDATE
        response = await apiClient.put(`/admin/milestone-templates/${editingTemplate.id}`, formData);
      } else {
        // CREATE
        response = await apiClient.post('/admin/milestone-templates/', formData);
      }
      
      if (response.success) {
        setSuccess(editingTemplate ? 'Template aggiornato con successo' : 'Template creato con successo');
        setShowCreateForm(false);
        resetForm();
        loadTemplates();
      } else {
        setError(response.error || 'Errore salvataggio template');
      }
    } catch (error) {
      console.error('Errore salvataggio template:', error);
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  const handleEditTemplate = (template: any) => {
    setEditingTemplate(template);
    setFormData({
      nome: template.nome,
      descrizione: template.descrizione || '',
      durata_stimata_giorni: template.durata_stimata_giorni,
      categoria: template.categoria || 'standard',
    });
    setShowCreateForm(true);
  };

  const handleDeleteTemplate = async (templateId: number) => {
    if (!confirm('Sei sicuro di voler eliminare questo template?')) return;

    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.delete('/admin/milestone-templates/' + templateId);
      if (response.success) {
        setSuccess('Template eliminato con successo');
        loadTemplates();
      } else {
        setError(response.error || 'Errore eliminazione template');
      }
    } catch (error) {
      console.error('Errore eliminazione template:', error);
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  // ===== TASK MANAGEMENT =====

  const loadTemplateTasks = async (template: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/admin/milestone-templates/${template.id}/tasks`);
      if (response.success && response.data) {
        setTemplateTasks(response.data.tasks);
        setSelectedTemplate({
          ...template,
          sla_giorni: response.data.milestone_sla_giorni
        });
        setShowTaskDialog(true);
      } else {
        setError('Errore caricamento task');
      }
    } catch (error) {
      console.error('Errore caricamento task:', error);
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableTasks = async () => {
    try {
      const response = await apiClient.get('/tasks-global/');
      if (response.success && response.data) {
        setAvailableTasks(response.data);
      }
    } catch (error) {
      console.error('Errore caricamento task disponibili:', error);
    }
  };

  const handleAddTaskToMilestone = async () => {
    if (!selectedTemplate || !selectedTaskToAdd) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post(
        `/admin/milestone-templates/${selectedTemplate.id}/tasks/${selectedTaskToAdd.id}`,
        { ordine: templateTasks.length + 1 }
      );
      
      if (response.success) {
        setSuccess('Task associato con successo');
        setShowAddTaskDialog(false);
        setSelectedTaskToAdd(null);
        // Ricarica i task della milestone
        await loadTemplateTasks(selectedTemplate);
      } else {
        setError('Errore associazione task');
      }
    } catch (error) {
      console.error('Errore associazione task:', error);
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveTaskFromMilestone = async (taskId: number) => {
    if (!selectedTemplate) return;
    
    if (!confirm('Sei sicuro di voler rimuovere questo task dalla milestone?')) return;

    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.delete(
        `/admin/milestone-templates/${selectedTemplate.id}/tasks/${taskId}`
      );
      
      if (response.success) {
        setSuccess('Task rimosso con successo');
        // Ricarica i task della milestone
        await loadTemplateTasks(selectedTemplate);
      } else {
        setError('Errore rimozione task');
      }
    } catch (error) {
      console.error('Errore rimozione task:', error);
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  // ===== TASK ORDER MANAGER =====
  
  const handleOpenTaskManager = (template: any) => {
    setSelectedMilestoneForTasks(template);
    setShowTaskManager(true);
  };

  const handleCloseTaskManager = () => {
    setShowTaskManager(false);
    setSelectedMilestoneForTasks(null);
  };

  const handleRecalculateSLA = async (templateId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post(`/admin/milestone-templates/${templateId}/recalculate-sla`);
      if (response.success) {
        setSuccess('SLA ricalcolato con successo');
        loadTemplates();
      } else {
        setError('Errore ricalcolo SLA');
      }
    } catch (error) {
      console.error('Errore ricalcolo SLA:', error);
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ m: 0 }}>
          📋 Milestone Templates
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setShowCreateForm(true)}
          disabled={loading}
        >
          Nuovo Template
        </Button>
      </Box>

      {/* Messages */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
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
                  <Chip
                    label={template.categoria}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                <Typography variant="caption" color="text.secondary">
                  Utilizzato in {template.usage_count} workflow
                </Typography>
              </CardContent>

              <CardActions>
                <Button
                  size="small"
                  onClick={() => loadTemplateTasks(template)}
                  disabled={loading}
                >
                  Gestisci Task
                </Button>

                <Button
                  size="small"
                  startIcon={<AssignmentIcon />}
                  onClick={() => handleOpenTaskManager(template)}
                  disabled={loading}
                  sx={{ color: 'primary.main' }}
                >
                  📋 Ordina Task
                </Button>

                <Button
                  size="small"
                  startIcon={<EditIcon />}
                  onClick={() => handleEditTemplate(template)}
                  disabled={loading}
                >
                  Modifica
                </Button>               

                <Button
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={() => handleRecalculateSLA(template.id)}
                  disabled={loading}
                >
                  Ricalcola SLA
                </Button>
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleDeleteTemplate(template.id)}
                  disabled={loading}
                >
                  <DeleteIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Empty State */}
      {!loading && templates.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Nessun template milestone trovato
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Crea il primo template per iniziare
          </Typography>
        </Box>
      )}

      {/* Create/Edit Dialog */}
      <Dialog
        open={showCreateForm}
        onClose={() => {
          setShowCreateForm(false);
          resetForm();
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {editingTemplate ? 'Modifica Template Milestone' : 'Nuovo Template Milestone'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Nome Template"
              value={formData.nome}
              onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Descrizione"
              value={formData.descrizione}
              onChange={(e) => setFormData(prev => ({ ...prev, descrizione: e.target.value }))}
              margin="normal"
              multiline
              rows={3}
            />
            <TextField
              fullWidth
              label="Durata Stimata (giorni)"
              type="number"
              value={formData.durata_stimata_giorni || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, durata_stimata_giorni: e.target.value ? parseInt(e.target.value) : undefined }))}
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Categoria</InputLabel>
              <Select
                value={formData.categoria}
                onChange={(e) => setFormData(prev => ({ ...prev, categoria: e.target.value }))}
              >
                <MenuItem value="standard">Standard</MenuItem>
                <MenuItem value="commerciale">Commerciale</MenuItem>
                <MenuItem value="tecnico">Tecnico</MenuItem>
                <MenuItem value="amministrativo">Amministrativo</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowCreateForm(false);
            resetForm();
          }}>
            Annulla
          </Button>
          <Button 
            onClick={handleCreateOrUpdateTemplate} 
            variant="contained"
            disabled={loading}
          >
            {editingTemplate ? 'Aggiorna' : 'Crea'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Task Management Dialog */}
      <Dialog
        open={showTaskDialog}
        onClose={() => setShowTaskDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Task per: {selectedTemplate?.nome}
            </Typography>
            <IconButton onClick={() => setShowTaskDialog(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => setShowAddTaskDialog(true)}
              disabled={loading}
            >
              Associa Task
            </Button>
          </Box>

          {templateTasks.length > 0 ? (
            <List>
              {templateTasks.map((task, index) => (
                <React.Fragment key={task.id}>
                  <ListItem>
                    <ListItemText
                      primary={task.nome}
                      secondary={
                        <Box>
                          <Typography variant="body2">{task.descrizione}</Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Chip label={`${task.sla_hours}h`} size="small" />
                            <Chip label={task.priorita} size="small" color="primary" />
                            {task.is_required && (
                              <Chip label="Obbligatorio" size="small" color="error" />
                            )}
                          </Box>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        color="error"
                        onClick={() => handleRemoveTaskFromMilestone(task.id)}
                        disabled={loading}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < templateTasks.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
              Nessun task associato alla milestone
            </Typography>
          )}
        </DialogContent>
      </Dialog>

      {/* Add Task Dialog */}
      <Dialog
        open={showAddTaskDialog}
        onClose={() => setShowAddTaskDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Seleziona Task da Associare</DialogTitle>
        <DialogContent>
          <List>
            {availableTasks.map((task) => (
              <ListItem
                key={task.id}
                button
                selected={selectedTaskToAdd?.id === task.id}
                onClick={() => setSelectedTaskToAdd(task)}
              >
                <ListItemText
                  primary={task.tsk_code}
                  secondary={task.tsk_description}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAddTaskDialog(false)}>
            Annulla
          </Button>
          <Button 
            onClick={handleAddTaskToMilestone}
            variant="contained"
            disabled={!selectedTaskToAdd || loading}
          >
            Associa Task
          </Button>
        </DialogActions>
      </Dialog>

      {/* Task Order Manager Dialog */}
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
