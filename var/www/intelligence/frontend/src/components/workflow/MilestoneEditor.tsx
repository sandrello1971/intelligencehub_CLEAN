// components/workflow/MilestoneEditor.tsx
// Editor per Milestone con gestione Task Templates - IntelligenceHUB

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Save,
  Cancel,
  DragIndicator,
  ExpandMore,
  Assignment,
  Schedule,
  Person,
  CheckCircle
} from '@mui/icons-material';
import { workflowApi, WorkflowMilestone, TaskTemplate } from '../../services/workflowApi';

interface MilestoneEditorProps {
  workflowId: number;
  onMilestoneUpdate: () => void;
}

interface MilestoneFormData {
  nome: string;
  descrizione: string;
  ordine: number;
  durata_stimata_giorni: number | null;
  sla_giorni: number | null;
  warning_giorni: number;
  escalation_giorni: number;
  tipo_milestone: string;
  auto_generate_tickets: boolean;
}

interface TaskFormData {
  nome: string;
  descrizione: string;
  ordine: number;
  durata_stimata_ore: number | null;
  ruolo_responsabile: string;
  obbligatorio: boolean;
  tipo_task: string;
  checklist_template: string[];
}

const MilestoneEditor: React.FC<MilestoneEditorProps> = ({
  workflowId,
  onMilestoneUpdate
}) => {
  const [milestones, setMilestones] = useState<(WorkflowMilestone & { task_templates: TaskTemplate[] })[]>([]);
  const [loading, setLoading] = useState(false);
  const [showMilestoneForm, setShowMilestoneForm] = useState(false);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [selectedMilestone, setSelectedMilestone] = useState<WorkflowMilestone | null>(null);
  const [editingTask, setEditingTask] = useState<TaskTemplate | null>(null);
  const [milestoneFormData, setMilestoneFormData] = useState<MilestoneFormData>({
    nome: '',
    descrizione: '',
    ordine: 1,
    durata_stimata_giorni: null,
    sla_giorni: null,
    warning_giorni: 2,
    escalation_giorni: 1,
    tipo_milestone: 'standard',
    auto_generate_tickets: true
  });
  const [taskFormData, setTaskFormData] = useState<TaskFormData>({
    nome: '',
    descrizione: '',
    ordine: 1,
    durata_stimata_ore: null,
    ruolo_responsabile: '',
    obbligatorio: true,
    tipo_task: 'standard',
    checklist_template: []
  });
  const [newChecklistItem, setNewChecklistItem] = useState('');

  useEffect(() => {
    loadWorkflowDetails();
  }, [workflowId]);

  const loadWorkflowDetails = async () => {
    setLoading(true);
    try {
      const response = await workflowApi.getWorkflowTemplate(workflowId);
      if (response.success && response.data) {
        setMilestones(response.data.milestones || []);
      }
    } catch (error) {
      console.error('Errore caricamento workflow:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMilestone = async () => {
    try {
      const milestoneData = {
        ...milestoneFormData,
        workflow_template_id: workflowId
      };

      const response = await workflowApi.createWorkflowMilestone(milestoneData);
      if (response.success) {
        setShowMilestoneForm(false);
        resetMilestoneForm();
        loadWorkflowDetails();
        onMilestoneUpdate();
      }
    } catch (error) {
      console.error('Errore creazione milestone:', error);
    }
  };

  const handleCreateTask = async () => {
    if (!selectedMilestone) return;

    try {
      const taskData = {
        ...taskFormData,
        milestone_id: selectedMilestone.id
      };

      const response = await workflowApi.createTaskTemplate(taskData);
      if (response.success) {
        setShowTaskForm(false);
        resetTaskForm();
        loadWorkflowDetails();
      }
    } catch (error) {
      console.error('Errore creazione task:', error);
    }
  };

  const resetMilestoneForm = () => {
    setMilestoneFormData({
      nome: '',
      descrizione: '',
      ordine: milestones.length + 1,
      durata_stimata_giorni: null,
      sla_giorni: null,
      warning_giorni: 2,
      escalation_giorni: 1,
      tipo_milestone: 'standard',
      auto_generate_tickets: true
    });
  };

  const resetTaskForm = () => {
    setTaskFormData({
      nome: '',
      descrizione: '',
      ordine: selectedMilestone ? selectedMilestone.task_templates?.length + 1 || 1 : 1,
      durata_stimata_ore: null,
      ruolo_responsabile: '',
      obbligatorio: true,
      tipo_task: 'standard',
      checklist_template: []
    });
    setEditingTask(null);
  };

  const handleAddChecklistItem = () => {
    if (newChecklistItem.trim()) {
      setTaskFormData(prev => ({
        ...prev,
        checklist_template: [...prev.checklist_template, newChecklistItem.trim()]
      }));
      setNewChecklistItem('');
    }
  };

  const handleRemoveChecklistItem = (index: number) => {
    setTaskFormData(prev => ({
      ...prev,
      checklist_template: prev.checklist_template.filter((_, i) => i !== index)
    }));
  };

  const getTotalDuration = () => {
    return milestones.reduce((total, milestone) => {
      return total + (milestone.durata_stimata_giorni || 0);
    }, 0);
  };

  const getTotalTasks = () => {
    return milestones.reduce((total, milestone) => {
      return total + (milestone.task_templates?.length || 0);
    }, 0);
  };

  return (
    <Box>
      {/* Header con statistiche */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Configurazione Milestone e Task
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setShowMilestoneForm(true)}
            sx={{ borderRadius: 2 }}
          >
            Nuova Milestone
          </Button>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <Card sx={{ backgroundColor: '#e3f2fd', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#1976d2' }}>
                  {milestones.length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Milestone Configurate
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card sx={{ backgroundColor: '#e8f5e8', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#2e7d32' }}>
                  {getTotalTasks()}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Task Templates Totali
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card sx={{ backgroundColor: '#fff3e0', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#f57c00' }}>
                  {getTotalDuration()}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Giorni Stimati Totali
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Lista Milestone */}
      {milestones.length === 0 ? (
        <Card sx={{ textAlign: 'center', py: 6 }}>
          <CardContent>
            <Assignment sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Nessuna milestone configurata
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              Inizia aggiungendo la prima milestone al tuo workflow
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setShowMilestoneForm(true)}
            >
              Aggiungi Prima Milestone
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {milestones.map((milestone, index) => (
            <Accordion key={milestone.id} defaultExpanded={index === 0}>
              <AccordionSummary
                expandIcon={<ExpandMore />}
                sx={{ backgroundColor: '#f8f9fa' }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
                  <DragIndicator color="disabled" />
                  <Chip
                    label={`#${milestone.ordine}`}
                    size="small"
                    color="primary"
                  />
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, flexGrow: 1 }}>
                    {milestone.nome}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {milestone.durata_stimata_giorni && (
                      <Chip
                        icon={<Schedule />}
                        label={`${milestone.durata_stimata_giorni}g`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                    <Chip
                      icon={<Assignment />}
                      label={`${milestone.task_templates?.length || 0} task`}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                </Box>
              </AccordionSummary>
              
              <AccordionDetails>
                <Grid container spacing={3}>
                  {/* Dettagli Milestone */}
                  <Grid item xs={12} md={6}>
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        Dettagli Milestone
                      </Typography>
                      {milestone.descrizione && (
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                          {milestone.descrizione}
                        </Typography>
                      )}
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        <Chip label={`SLA: ${milestone.sla_giorni || 'N/A'} giorni`} size="small" />
                        <Chip label={`Warning: ${milestone.warning_giorni}g`} size="small" />
                        <Chip label={`Escalation: ${milestone.escalation_giorni}g`} size="small" />
                        <Chip 
                          label={milestone.auto_generate_tickets ? 'Auto-generate' : 'Manuale'} 
                          size="small" 
                          color={milestone.auto_generate_tickets ? 'success' : 'default'}
                        />
                      </Box>
                    </Box>
                  </Grid>

                  {/* Task Templates */}
                  <Grid item xs={12} md={6}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        Task Templates ({milestone.task_templates?.length || 0})
                      </Typography>
                      <Button
                        size="small"
                        startIcon={<Add />}
                        onClick={() => {
                          setSelectedMilestone(milestone);
                          setShowTaskForm(true);
                        }}
                      >
                        Aggiungi Task
                      </Button>
                    </Box>

                    {milestone.task_templates && milestone.task_templates.length > 0 ? (
                      <List dense>
                        {milestone.task_templates.map((task, taskIndex) => (
                          <ListItem key={task.id} sx={{ px: 0 }}>
                            <ListItemText
                              primary={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Chip
                                    label={task.ordine}
                                    size="small"
                                    sx={{ minWidth: 24, height: 20 }}
                                  />
                                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                    {task.nome}
                                  </Typography>
                                  {task.obbligatorio && (
                                    <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                                  )}
                                </Box>
                              }
                              secondary={
                                <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                                  {task.durata_stimata_ore && (
                                    <Chip
                                      label={`${task.durata_stimata_ore}h`}
                                      size="small"
                                      variant="outlined"
                                    />
                                  )}
                                  {task.ruolo_responsabile && (
                                    <Chip
                                      icon={<Person />}
                                      label={task.ruolo_responsabile}
                                      size="small"
                                      variant="outlined"
                                    />
                                  )}
                                </Box>
                              }
                            />
                            <ListItemSecondaryAction>
                              <IconButton
                                size="small"
                                onClick={() => {
                                  setSelectedMilestone(milestone);
                                  setEditingTask(task);
                                  setTaskFormData({
                                    nome: task.nome,
                                    descrizione: task.descrizione,
                                    ordine: task.ordine,
                                    durata_stimata_ore: task.durata_stimata_ore,
                                    ruolo_responsabile: task.ruolo_responsabile || '',
                                    obbligatorio: task.obbligatorio,
                                    tipo_task: task.tipo_task,
                                    checklist_template: Array.isArray(task.checklist_template) 
                                      ? task.checklist_template.map(item => typeof item === 'string' ? item : item.text || '')
                                      : []
                                  });
                                  setShowTaskForm(true);
                                }}
                              >
                                <Edit />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Alert severity="info" sx={{ mt: 1 }}>
                        Nessun task configurato per questa milestone
                      </Alert>
                    )}
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}

      {/* Dialog Creazione Milestone */}
      <Dialog
        open={showMilestoneForm}
        onClose={() => setShowMilestoneForm(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Nuova Milestone</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Nome Milestone"
                value={milestoneFormData.nome}
                onChange={(e) => setMilestoneFormData(prev => ({ ...prev, nome: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Ordine"
                type="number"
                value={milestoneFormData.ordine}
                onChange={(e) => setMilestoneFormData(prev => ({ ...prev, ordine: parseInt(e.target.value) || 1 }))}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Descrizione"
                value={milestoneFormData.descrizione}
                onChange={(e) => setMilestoneFormData(prev => ({ ...prev, descrizione: e.target.value }))}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Durata Stimata (giorni)"
                type="number"
                value={milestoneFormData.durata_stimata_giorni || ''}
                onChange={(e) => setMilestoneFormData(prev => ({ 
                  ...prev, 
                  durata_stimata_giorni: e.target.value ? parseInt(e.target.value) : null 
                }))}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="SLA (giorni)"
                type="number"
                value={milestoneFormData.sla_giorni || ''}
                onChange={(e) => setMilestoneFormData(prev => ({ 
                  ...prev, 
                  sla_giorni: e.target.value ? parseInt(e.target.value) : null 
                }))}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Tipo Milestone</InputLabel>
                <Select
                  value={milestoneFormData.tipo_milestone}
                  onChange={(e) => setMilestoneFormData(prev => ({ ...prev, tipo_milestone: e.target.value }))}
                  label="Tipo Milestone"
                >
                  <MenuItem value="standard">Standard</MenuItem>
                  <MenuItem value="critica">Critica</MenuItem>
                  <MenuItem value="opzionale">Opzionale</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={milestoneFormData.auto_generate_tickets}
                    onChange={(e) => setMilestoneFormData(prev => ({ 
                      ...prev, 
                      auto_generate_tickets: e.target.checked 
                    }))}
                  />
                }
                label="Genera ticket automaticamente"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMilestoneForm(false)}>Annulla</Button>
          <Button 
            onClick={handleCreateMilestone}
            variant="contained"
            disabled={!milestoneFormData.nome.trim()}
          >
            Crea Milestone
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog Creazione/Modifica Task */}
      <Dialog
        open={showTaskForm}
        onClose={() => setShowTaskForm(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingTask ? 'Modifica Task' : 'Nuovo Task'} - {selectedMilestone?.nome}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Nome Task"
                value={taskFormData.nome}
                onChange={(e) => setTaskFormData(prev => ({ ...prev, nome: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Ordine"
                type="number"
                value={taskFormData.ordine}
                onChange={(e) => setTaskFormData(prev => ({ ...prev, ordine: parseInt(e.target.value) || 1 }))}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Descrizione"
                value={taskFormData.descrizione}
                onChange={(e) => setTaskFormData(prev => ({ ...prev, descrizione: e.target.value }))}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Durata Stimata (ore)"
                type="number"
                value={taskFormData.durata_stimata_ore || ''}
                onChange={(e) => setTaskFormData(prev => ({ 
                  ...prev, 
                  durata_stimata_ore: e.target.value ? parseInt(e.target.value) : null 
                }))}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Ruolo Responsabile"
                value={taskFormData.ruolo_responsabile}
                onChange={(e) => setTaskFormData(prev => ({ ...prev, ruolo_responsabile: e.target.value }))}
                placeholder="es: analista, senior, commerciale"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo Task</InputLabel>
                <Select
                  value={taskFormData.tipo_task}
                  onChange={(e) => setTaskFormData(prev => ({ ...prev, tipo_task: e.target.value }))}
                  label="Tipo Task"
                >
                  <MenuItem value="standard">Standard</MenuItem>
                  <MenuItem value="review">Review</MenuItem>
                  <MenuItem value="approval">Approvazione</MenuItem>
                  <MenuItem value="documentation">Documentazione</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={taskFormData.obbligatorio}
                    onChange={(e) => setTaskFormData(prev => ({ 
                      ...prev, 
                      obbligatorio: e.target.checked 
                    }))}
                  />
                }
                label="Task obbligatorio"
              />
            </Grid>

            {/* Checklist Template */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Checklist Template
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Aggiungi elemento checklist..."
                  value={newChecklistItem}
                  onChange={(e) => setNewChecklistItem(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleAddChecklistItem();
                    }
                  }}
                />
                <Button
                  variant="outlined"
                  onClick={handleAddChecklistItem}
                  disabled={!newChecklistItem.trim()}
                >
                  Aggiungi
                </Button>
              </Box>
              
              {taskFormData.checklist_template.length > 0 && (
                <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
                  {taskFormData.checklist_template.map((item, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={item} />
                      <ListItemSecondaryAction>
                        <IconButton
                          size="small"
                          onClick={() => handleRemoveChecklistItem(index)}
                        >
                          <Delete />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowTaskForm(false);
            resetTaskForm();
          }}>
            Annulla
          </Button>
          <Button 
            onClick={handleCreateTask}
            variant="contained"
            disabled={!taskFormData.nome.trim()}
          >
            {editingTask ? 'Aggiorna Task' : 'Crea Task'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MilestoneEditor;
