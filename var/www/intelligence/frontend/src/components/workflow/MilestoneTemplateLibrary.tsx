// components/workflow/MilestoneTemplateLibrary.tsx
// Libreria Template Milestone Riutilizzabili - IntelligenceHUB
// IMPLEMENTAZIONE COMPLETA - NO MOCK DATA

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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  ExpandMore as ExpandMoreIcon,
  Schedule as ScheduleIcon,
  Assignment as AssignmentIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

import { apiClient } from '../../services/api';

const MilestoneTemplateLibrary: React.FC = () => {
  const [templates, setTemplates] = useState<MilestoneTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Form states
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<MilestoneTemplate | null>(null);
  const [formData, setFormData] = useState<MilestoneTemplateCreateData>({
    nome: '',
    descrizione: '',
    durata_stimata_giorni: undefined,
    categoria: 'iniziale',
  });

  // Task management states
  const [selectedTemplate, setSelectedTemplate] = useState<MilestoneTemplate | null>(null);
  const [templateTasks, setTemplateTasks] = useState<TaskTemplate[]>([]);
  const [showTaskDialog, setShowTaskDialog] = useState(false);

  useEffect(() => {
    console.log("=== MilestoneTemplateLibrary MOUNTED ===");
    loadTemplates();
  }, []);

  // ===== TEMPLATE MANAGEMENT =====

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

  const handleCreateTemplate = async () => {
    if (!formData.nome.trim()) {
      setError('Nome template obbligatorio');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post('/admin/milestone-templates/', formData);
      if (response.success) {
        setSuccess('Milestone template creato con successo');
        setShowCreateForm(false);
        resetForm();
        loadTemplates();
      } else {
        setError(response.error || 'Errore creazione template');
      }
    } catch (error) {
      console.error('Errore creazione template:', error);
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
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

  const loadTemplateTasks = async (template: MilestoneTemplate) => {
    setLoading(true);
    setError(null);
    try {
      const response = await milestoneTemplateApi.getMilestoneTemplateTasks(template.id);
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

  const handleRecalculateSLA = async (templateId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await milestoneTemplateApi.recalculateMilestoneSLA(templateId);
      if (response.success && response.data) {
        setSuccess(`SLA ricalcolato: ${response.data.calculated_sla_giorni} giorni`);
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

  // ===== UTILITY FUNCTIONS =====

  const resetForm = () => {
    setFormData({
      nome: '',
      descrizione: '',
      durata_stimata_giorni: undefined,
      categoria: 'iniziale',
    });
    setEditingTemplate(null);
  };

  const getCategoryColor = (categoria: string) => {
    const colors: Record<string, 'primary' | 'secondary' | 'success' | 'warning' | 'error'> = {
      'iniziale': 'primary',
      'analisi': 'secondary',
      'sviluppo': 'warning',
      'finale': 'success',
      'standard': 'primary'
    };
    return colors[categoria] || 'primary';
  };

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Libreria Milestone Templates
        </Typography>
        <Box>
          <Button
            startIcon={<RefreshIcon />}
            onClick={loadTemplates}
            disabled={loading}
            sx={{ mr: 2 }}
          >
            Aggiorna
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              clearMessages();
              setShowCreateForm(true);
            }}
          >
            Nuovo Template
          </Button>
        </Box>
      </Box>

      {/* Messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Loading */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Templates Grid */}
      <Grid container spacing={3}>
        {templates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="h2">
                    {template.nome}
                  </Typography>
                  <Chip
                    label={template.categoria}
                    color={getCategoryColor(template.categoria)}
                    size="small"
                  />
                </Box>

                {template.descrizione && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {template.descrizione}
                  </Typography>
                )}

                {/* Statistics */}
                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <ScheduleIcon fontSize="small" color="primary" />
                    <Typography variant="body2">
                      {template.durata_stimata_giorni || 'N/A'} giorni
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <AssignmentIcon fontSize="small" color="secondary" />
                    <Typography variant="body2">
                      {template.task_count} task
                    </Typography>
                  </Box>
                </Box>

                {/* SLA Info */}
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    <strong>SLA:</strong> {template.sla_giorni} giorni
                    <br />
                    <em>(Calcolato automaticamente dai task)</em>
                  </Typography>
                </Alert>

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
          {editingTemplate ? 'Modifica Template' : 'Nuovo Template Milestone'}
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
              onChange={(e) => setFormData(prev => ({ 
                ...prev, 
                durata_stimata_giorni: e.target.value ? parseInt(e.target.value) : undefined 
              }))}
              margin="normal"
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>Categoria</InputLabel>
              <Select
                value={formData.categoria}
                onChange={(e) => setFormData(prev => ({ ...prev, categoria: e.target.value }))}
                label="Categoria"
              >
                <MenuItem value="iniziale">Iniziale</MenuItem>
                <MenuItem value="analisi">Analisi</MenuItem>
                <MenuItem value="sviluppo">Sviluppo</MenuItem>
                <MenuItem value="finale">Finale</MenuItem>
                <MenuItem value="standard">Standard</MenuItem>
              </Select>
            </FormControl>

            <Alert severity="info" sx={{ mt: 2 }}>
              L'SLA della milestone sarà calcolato automaticamente dalla somma degli SLA dei task assegnati.
            </Alert>
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
            onClick={handleCreateTemplate}
            variant="contained"
            disabled={loading || !formData.nome.trim()}
          >
            {loading ? <CircularProgress size={20} /> : (editingTemplate ? 'Aggiorna' : 'Crea')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Task Management Dialog */}
      <Dialog
        open={showTaskDialog}
        onClose={() => {
          setShowTaskDialog(false);
          setSelectedTemplate(null);
          setTemplateTasks([]);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Task di: {selectedTemplate?.nome}
          {selectedTemplate && (
            <Typography variant="body2" color="text.secondary">
              SLA Totale: {selectedTemplate.sla_giorni} giorni
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          {templateTasks.length > 0 ? (
            <List>
              {templateTasks.map((task) => (
                <ListItem key={task.id} divider>
                  <ListItemText
                    primary={task.nome}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          {task.descrizione}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          <Chip
                            label={`${task.sla_hours}h`}
                            size="small"
                            color="primary"
                          />
                          <Chip
                            label={task.priorita}
                            size="small"
                            color="secondary"
                          />
                          {task.is_required && (
                            <Chip
                              label="Obbligatorio"
                              size="small"
                              color="error"
                            />
                          )}
                        </Box>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Typography variant="body2" color="text.secondary">
                      Ordine: {task.ordine}
                    </Typography>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          ) : (
            <Alert severity="info">
              Nessun task assegnato a questo template milestone.
              <br />
              Usa la gestione task per aggiungere task esistenti.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowTaskDialog(false);
            setSelectedTemplate(null);
            setTemplateTasks([]);
          }}>
            Chiudi
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MilestoneTemplateLibrary;
