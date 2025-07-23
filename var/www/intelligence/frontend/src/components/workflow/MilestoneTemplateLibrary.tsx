// components/workflow/MilestoneTemplateLibrary.tsx
// Libreria Milestone Templates Riutilizzabili - IntelligenceHUB

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Add,
  Edit,
  FileCopy,
  Delete,
  Assignment,
  Schedule
} from '@mui/icons-material';
import { workflowApi } from '../../services/workflowApi';

interface MilestoneTemplate {
  id: number;
  nome: string;
  descrizione: string;
  durata_stimata_giorni: number;
  sla_giorni: number;
  categoria: string;
  task_templates?: any[];
  usage_count?: number;
}

const MilestoneTemplateLibrary: React.FC = () => {
  const [templates, setTemplates] = useState<MilestoneTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<MilestoneTemplate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    nome: '',
    descrizione: '',
    durata_stimata_giorni: null as number | null,
    categoria: 'iniziale',
    sla_giorni: null as number | null
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      // Per ora usiamo dati mock perché l'API backend non è ancora implementata
      const mockTemplates: MilestoneTemplate[] = [
        {
          id: 1,
          nome: "Raccolta Documentazione",
          descrizione: "Fase di raccolta e verifica documentazione cliente",
          durata_stimata_giorni: 5,
          sla_giorni: 7,
          categoria: "iniziale",
          task_templates: [
            { nome: "Richiesta documenti", ordine: 1 },
            { nome: "Verifica completezza", ordine: 2 },
            { nome: "Validazione", ordine: 3 }
          ],
          usage_count: 5
        },
        {
          id: 2,
          nome: "Analisi Preliminare", 
          descrizione: "Analisi della situazione aziendale",
          durata_stimata_giorni: 7,
          sla_giorni: 10,
          categoria: "analisi",
          task_templates: [
            { nome: "Analisi bilanci", ordine: 1 },
            { nome: "Verifica requisiti", ordine: 2 },
            { nome: "Report preliminare", ordine: 3 }
          ],
          usage_count: 3
        },
        {
          id: 3,
          nome: "Sviluppo Progetto",
          descrizione: "Fase di sviluppo e implementazione",
          durata_stimata_giorni: 15,
          sla_giorni: 20,
          categoria: "sviluppo",
          task_templates: [
            { nome: "Pianificazione dettagliata", ordine: 1 },
            { nome: "Implementazione", ordine: 2 },
            { nome: "Test e validazione", ordine: 3 }
          ],
          usage_count: 2
        },
        {
          id: 4,
          nome: "Consegna Finale",
          descrizione: "Fase di consegna e chiusura progetto",
          durata_stimata_giorni: 3,
          sla_giorni: 5,
          categoria: "finale",
          task_templates: [
            { nome: "Preparazione consegna", ordine: 1 },
            { nome: "Presentazione cliente", ordine: 2 },
            { nome: "Chiusura progetto", ordine: 3 }
          ],
          usage_count: 8
        }
      ];
      setTemplates(mockTemplates);
    } catch (error) {
      setError('Errore caricamento templates');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      nome: '',
      descrizione: '',
      durata_stimata_giorni: null,
      categoria: 'iniziale',
      sla_giorni: null
    });
    setEditingTemplate(null);
  };

  const handleSubmit = async () => {
    if (!formData.nome.trim()) {
      setError('Nome template obbligatorio');
      return;
    }

    setLoading(true);
    try {
      // Simula salvataggio (implementare API reale quando sarà pronta)
      const newTemplate: MilestoneTemplate = {
        id: Date.now(), // Temporary ID
        ...formData,
        durata_stimata_giorni: formData.durata_stimata_giorni || 5,
        sla_giorni: formData.sla_giorni || 7,
        task_templates: [],
        usage_count: 0
      };

      if (editingTemplate) {
        // Update existing
        setTemplates(prev => prev.map(t => t.id === editingTemplate.id ? { ...newTemplate, id: editingTemplate.id } : t));
      } else {
        // Add new
        setTemplates(prev => [...prev, newTemplate]);
      }

      setShowForm(false);
      resetForm();
      setError(null);
    } catch (error) {
      setError('Errore salvataggio template');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (template: MilestoneTemplate) => {
    setEditingTemplate(template);
    setFormData({
      nome: template.nome,
      descrizione: template.descrizione,
      durata_stimata_giorni: template.durata_stimata_giorni,
      categoria: template.categoria,
      sla_giorni: template.sla_giorni
    });
    setShowForm(true);
  };

  const handleClone = (template: MilestoneTemplate) => {
    setFormData({
      nome: `${template.nome} (Copia)`,
      descrizione: template.descrizione,
      durata_stimata_giorni: template.durata_stimata_giorni,
      categoria: template.categoria,
      sla_giorni: template.sla_giorni
    });
    setEditingTemplate(null);
    setShowForm(true);
  };

  const handleDelete = async (template: MilestoneTemplate) => {
    if (window.confirm(`Eliminare il template "${template.nome}"?`)) {
      setTemplates(prev => prev.filter(t => t.id !== template.id));
    }
  };

  const getCategoryColor = (categoria: string) => {
    switch (categoria) {
      case 'iniziale': return 'primary';
      case 'analisi': return 'info';
      case 'sviluppo': return 'warning';
      case 'finale': return 'success';
      default: return 'default';
    }
  };

  if (loading && templates.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          Milestone Templates Library
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

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
        Crea milestone riutilizzabili che possono essere assegnate a diversi workflow. 
        Ogni template può contenere task predefiniti e configurazioni SLA.
      </Typography>

      {templates.length === 0 ? (
        <Card sx={{ textAlign: 'center', py: 6 }}>
          <CardContent>
            <Assignment sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Nessun milestone template disponibile
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              Crea il primo template per iniziare a standardizzare i tuoi processi
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setShowForm(true)}
            >
              Crea Primo Template
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {templates.map((template) => (
            <Grid item xs={12} md={6} lg={4} key={template.id}>
              <Card sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                '&:hover': { boxShadow: 4 }
              }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, flexGrow: 1, mr: 1 }}>
                      {template.nome}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <IconButton size="small" onClick={() => handleEdit(template)}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleClone(template)}>
                        <FileCopy />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleDelete(template)} color="error">
                        <Delete />
                      </IconButton>
                    </Box>
                  </Box>

                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    {template.descrizione}
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    <Chip
                      label={template.categoria}
                      size="small"
                      color={getCategoryColor(template.categoria) as any}
                      variant="outlined"
                    />
                    <Chip
                      icon={<Schedule />}
                      label={`${template.durata_stimata_giorni}g`}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      icon={<Assignment />}
                      label={`${template.task_templates?.length || 0} task`}
                      size="small"
                      variant="outlined"
                    />
                  </Box>

                  <Typography variant="caption" color="textSecondary">
                    SLA: {template.sla_giorni} giorni • Utilizzato in {template.usage_count || 0} workflow
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Dialog Form */}
      <Dialog open={showForm} onClose={() => setShowForm(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingTemplate ? 'Modifica Milestone Template' : 'Nuovo Milestone Template'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nome Template"
                value={formData.nome}
                onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
                required
                placeholder="es: Raccolta Documentazione"
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
                placeholder="Descrizione del template e quando utilizzarlo"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Durata Stimata (giorni)"
                type="number"
                value={formData.durata_stimata_giorni || ''}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  durata_stimata_giorni: e.target.value ? parseInt(e.target.value) : null 
                }))}
                inputProps={{ min: 1, max: 365 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="SLA (giorni)"
                type="number"
                value={formData.sla_giorni || ''}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  sla_giorni: e.target.value ? parseInt(e.target.value) : null 
                }))}
                inputProps={{ min: 1, max: 365 }}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
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
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowForm(false);
            resetForm();
            setError(null);
          }}>
            Annulla
          </Button>
          <Button 
            onClick={handleSubmit}
            variant="contained"
            disabled={loading || !formData.nome.trim()}
          >
            {editingTemplate ? 'Aggiorna' : 'Crea'} Template
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MilestoneTemplateLibrary;
