// components/workflow/TaskTemplateManager.tsx
// Gestione autonoma Task Templates riutilizzabili - IntelligenceHUB

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  InputAdornment,
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
  Search,
  Edit,
  Delete,
  FileCopy,
  Assignment,
  Person,
  Schedule,
  CheckCircle,
  ExpandMore,
  Save,
  Cancel
} from '@mui/icons-material';

interface TaskTemplate {
  id: number;
  nome: string;
  descrizione: string;
  durata_stimata_ore: number | null;
  ruolo_responsabile: string | null;
  obbligatorio: boolean;
  tipo_task: string;
  checklist_template: any[];
  usage_count?: number; // Numero di milestone che usano questo template
}

interface TaskTemplateFormData {
  nome: string;
  descrizione: string;
  durata_stimata_ore: number | null;
  ruolo_responsabile: string;
  obbligatorio: boolean;
  tipo_task: string;
  checklist_template: string[];
  categoria: string;
}

const TaskTemplateManager: React.FC = () => {
  const [templates, setTemplates] = useState<TaskTemplate[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<TaskTemplate[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<TaskTemplate | null>(null);
  const [formData, setFormData] = useState<TaskTemplateFormData>({
    nome: '',
    descrizione: '',
    durata_stimata_ore: null,
    ruolo_responsabile: '',
    obbligatorio: true,
    tipo_task: 'standard',
    checklist_template: [],
    categoria: ''
  });
  const [newChecklistItem, setNewChecklistItem] = useState('');

  useEffect(() => {
    loadTemplates();
  }, []);

  useEffect(() => {
    filterTemplates();
  }, [templates, searchTerm, selectedCategory]);

  const loadTemplates = async () => {
    // Placeholder - implementare quando avremo l'API per template standalone
    const mockTemplates: TaskTemplate[] = [
      {
        id: 1,
        nome: "Raccolta Documentazione Cliente",
        descrizione: "Raccogliere tutta la documentazione necessaria dal cliente",
        durata_stimata_ore: 2,
        ruolo_responsabile: "commerciale",
        obbligatorio: true,
        tipo_task: "documentation",
        checklist_template: [
          "Documento identità",
          "Visura camerale",
          "Ultimo bilancio"
        ],
        usage_count: 5
      },
      {
        id: 2,
        nome: "Analisi Preliminare",
        descrizione: "Analisi preliminare della situazione aziendale",
        durata_stimata_ore: 4,
        ruolo_responsabile: "analista",
        obbligatorio: true,
        tipo_task: "review",
        checklist_template: [
          "Verifica dati bilancio",
          "Analisi settore",
          "Identificazione criticità"
        ],
        usage_count: 3
      },
      {
        id: 3,
        nome: "Approvazione Senior",
        descrizione: "Approvazione finale da parte del senior",
        durata_stimata_ore: 1,
        ruolo_responsabile: "senior",
        obbligatorio: true,
        tipo_task: "approval",
        checklist_template: [
          "Verifica completezza",
          "Controllo qualità",
          "Approvazione finale"
        ],
        usage_count: 8
      }
    ];
    setTemplates(mockTemplates);
  };

  const filterTemplates = () => {
    let filtered = templates;

    if (searchTerm) {
      filtered = filtered.filter(template =>
        template.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        template.descrizione.toLowerCase().includes(searchTerm.toLowerCase()) ||
        template.ruolo_responsabile?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCategory) {
      filtered = filtered.filter(template => template.tipo_task === selectedCategory);
    }

    setFilteredTemplates(filtered);
  };

  const resetForm = () => {
    setFormData({
      nome: '',
      descrizione: '',
      durata_stimata_ore: null,
      ruolo_responsabile: '',
      obbligatorio: true,
      tipo_task: 'standard',
      checklist_template: [],
      categoria: ''
    });
    setEditingTemplate(null);
  };

  const handleSubmit = async () => {
    // Implementare salvataggio
    console.log('Saving template:', formData);
    setShowForm(false);
    resetForm();
    // Ricarica templates
    loadTemplates();
  };

  const handleEdit = (template: TaskTemplate) => {
    setEditingTemplate(template);
    setFormData({
      nome: template.nome,
      descrizione: template.descrizione,
      durata_stimata_ore: template.durata_stimata_ore,
      ruolo_responsabile: template.ruolo_responsabile || '',
      obbligatorio: template.obbligatorio,
      tipo_task: template.tipo_task,
      checklist_template: Array.isArray(template.checklist_template) 
        ? template.checklist_template.map(item => typeof item === 'string' ? item : item.text || '')
        : [],
      categoria: template.tipo_task
    });
    setShowForm(true);
  };

  const handleClone = (template: TaskTemplate) => {
    setFormData({
      nome: `${template.nome} (Copia)`,
      descrizione: template.descrizione,
      durata_stimata_ore: template.durata_stimata_ore,
      ruolo_responsabile: template.ruolo_responsabile || '',
      obbligatorio: template.obbligatorio,
      tipo_task: template.tipo_task,
      checklist_template: Array.isArray(template.checklist_template) 
        ? template.checklist_template.map(item => typeof item === 'string' ? item : item.text || '')
        : [],
      categoria: template.tipo_task
    });
    setEditingTemplate(null);
    setShowForm(true);
  };

  const handleAddChecklistItem = () => {
    if (newChecklistItem.trim()) {
      setFormData(prev => ({
        ...prev,
        checklist_template: [...prev.checklist_template, newChecklistItem.trim()]
      }));
      setNewChecklistItem('');
    }
  };

  const handleRemoveChecklistItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      checklist_template: prev.checklist_template.filter((_, i) => i !== index)
    }));
  };

  const getTaskTypeColor = (type: string) => {
    switch (type) {
      case 'documentation': return 'info';
      case 'review': return 'warning';
      case 'approval': return 'success';
      default: return 'default';
    }
  };

  const getTaskTypeLabel = (type: string) => {
    switch (type) {
      case 'documentation': return 'Documentazione';
      case 'review': return 'Revisione';
      case 'approval': return 'Approvazione';
      default: return 'Standard';
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          Task Templates Library
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setShowForm(true)}
          sx={{ borderRadius: 2 }}
        >
          Nuovo Template
        </Button>
      </Box>

      {/* Filtri */}
      <Paper sx={{ p: 2, mb: 3, borderRadius: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              size="small"
              placeholder="Cerca templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Categoria</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Categoria"
              >
                <MenuItem value="">Tutte</MenuItem>
                <MenuItem value="standard">Standard</MenuItem>
                <MenuItem value="documentation">Documentazione</MenuItem>
                <MenuItem value="review">Revisione</MenuItem>
                <MenuItem value="approval">Approvazione</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Typography variant="body2" color="textSecondary">
              {filteredTemplates.length} template trovati
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Lista Templates */}
      {filteredTemplates.length === 0 ? (
        <Card sx={{ textAlign: 'center', py: 6 }}>
          <CardContent>
            <Assignment sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              {searchTerm || selectedCategory ? 'Nessun template trovato' : 'Nessun template disponibile'}
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              {searchTerm || selectedCategory 
                ? 'Prova a modificare i filtri di ricerca'
                : 'Crea il primo template per iniziare'
              }
            </Typography>
            {!searchTerm && !selectedCategory && (
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setShowForm(true)}
              >
                Crea Primo Template
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {filteredTemplates.map((template) => (
            <Grid item xs={12} md={6} lg={4} key={template.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, flexGrow: 1, mr: 1 }}>
                      {template.nome}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton size="small" onClick={() => handleEdit(template)}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleClone(template)}>
                        <FileCopy />
                      </IconButton>
                    </Box>
                  </Box>

                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    {template.descrizione}
                  </Typography>

                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                    <Chip
                      label={getTaskTypeLabel(template.tipo_task)}
                      size="small"
                      color={getTaskTypeColor(template.tipo_task) as any}
                      variant="outlined"
                    />
                    
                    {template.durata_stimata_ore && (
                      <Chip
                        icon={<Schedule />}
                        label={`${template.durata_stimata_ore}h`}
                        size="small"
                        variant="outlined"
                      />
                    )}

                    {template.ruolo_responsabile && (
                      <Chip
                        icon={<Person />}
                        label={template.ruolo_responsabile}
                        size="small"
                        variant="outlined"
                      />
                    )}

                    {template.obbligatorio && (
                      <Chip
                        icon={<CheckCircle />}
                        label="Obbligatorio"
                        size="small"
                        color="success"
                        variant="outlined"
                      />
                    )}
                  </Box>

                  {template.checklist_template && template.checklist_template.length > 0 && (
                    <Accordion sx={{ mt: 2 }}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="body2">
                          Checklist ({template.checklist_template.length} elementi)
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {template.checklist_template.map((item, index) => (
                            <ListItem key={index} sx={{ px: 0 }}>
                              <ListItemText 
                                primary={typeof item === 'string' ? item : item.text || item}
                                primaryTypographyProps={{ variant: 'body2' }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </CardContent>

                {template.usage_count !== undefined && (
                  <Box sx={{ px: 2, pb: 2 }}>
                    <Alert severity="info" sx={{ py: 0 }}>
                      <Typography variant="caption">
                        Utilizzato in {template.usage_count} milestone
                      </Typography>
                    </Alert>
                  </Box>
                )}
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Dialog Form */}
      <Dialog open={showForm} onClose={() => setShowForm(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingTemplate ? 'Modifica Task Template' : 'Nuovo Task Template'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Nome Template"
                value={formData.nome}
                onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Durata (ore)"
                type="number"
                value={formData.durata_stimata_ore || ''}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  durata_stimata_ore: e.target.value ? parseInt(e.target.value) : null 
                }))}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Descrizione"
                value={formData.descrizione}
                onChange={(e) => setFormData(prev => ({ ...prev, descrizione: e.target.value }))}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Ruolo Responsabile"
                value={formData.ruolo_responsabile}
                onChange={(e) => setFormData(prev => ({ ...prev, ruolo_responsabile: e.target.value }))}
                placeholder="es: analista, senior, commerciale"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo Task</InputLabel>
                <Select
                  value={formData.tipo_task}
                  onChange={(e) => setFormData(prev => ({ ...prev, tipo_task: e.target.value }))}
                  label="Tipo Task"
                >
                  <MenuItem value="standard">Standard</MenuItem>
                  <MenuItem value="documentation">Documentazione</MenuItem>
                  <MenuItem value="review">Revisione</MenuItem>
                  <MenuItem value="approval">Approvazione</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.obbligatorio}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      obbligatorio: e.target.checked 
                    }))}
                  />
                }
                label="Task obbligatorio per default"
              />
            </Grid>

            {/* Checklist */}
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
              
              {formData.checklist_template.length > 0 && (
                <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
                  {formData.checklist_template.map((item, index) => (
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
            setShowForm(false);
            resetForm();
          }}>
            Annulla
          </Button>
          <Button 
            onClick={handleSubmit}
            variant="contained"
            disabled={!formData.nome.trim()}
          >
            {editingTemplate ? 'Aggiorna' : 'Crea'} Template
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskTemplateManager;
