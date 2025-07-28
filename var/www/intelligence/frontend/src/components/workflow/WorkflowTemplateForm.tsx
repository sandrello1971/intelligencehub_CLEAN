// components/workflow/WorkflowTemplateForm.tsx
// Form per creazione/modifica Workflow Templates - IntelligenceHUB

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Grid,
  Alert,
  Chip,
  IconButton,
  Collapse
} from '@mui/material';
import {
  Save,
  Cancel,
  Add,
  Remove,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';
import { workflowApi, Articolo, WorkflowTemplate } from '../../services/workflowApi';

interface WorkflowTemplateFormProps {
  articoli: Articolo[];
  workflow?: WorkflowTemplate;
  onCancel: () => void;
  onSuccess: () => void;
}

interface FormData {
  nome: string;
  descrizione: string;
  durata_stimata_giorni: number | null;
  wkf_code: string;
  wkf_description: string;
  attivo: boolean;
}

const WorkflowTemplateForm: React.FC<WorkflowTemplateFormProps> = ({
  articoli,
  workflow,
  onCancel,
  onSuccess
}) => {
  const [formData, setFormData] = useState<FormData>({
    nome: workflow?.nome || '',
    descrizione: workflow?.descrizione || '',
    durata_stimata_giorni: workflow?.durata_stimata_giorni || null,
    wkf_code: workflow?.wkf_code || '',
    wkf_description: workflow?.wkf_description || '',
    attivo: workflow?.attivo ?? true
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [errors, setErrors] = useState<Partial<FormData>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<FormData> = {};

    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome obbligatorio';
    }

    if (formData.durata_stimata_giorni && formData.durata_stimata_giorni <= 0) {
      newErrors.durata_stimata_giorni = 'Durata deve essere positiva';
    }

    if (formData.wkf_code && !/^[A-Z0-9_]+$/.test(formData.wkf_code)) {
      newErrors.wkf_code = 'Codice deve contenere solo lettere maiuscole, numeri e underscore';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const submitData = {
        ...formData,
        ordine: 0 // Default order
      };

      const response = workflow 
        ? await workflowApi.updateWorkflowTemplate(workflow.id, submitData) 
        : await workflowApi.createWorkflowTemplate(submitData);
      
      if (response.success) {
        onSuccess();
      } else {
        setError(response.error || 'Errore durante il salvataggio');
      }
    } catch (err) {
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof FormData) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | any
  ) => {
    const value = event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value === '' ? null : value
    }));

    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const generateWorkflowCode = () => {
    if (!formData.nome) return;
    
    const code = formData.nome
      .toUpperCase()
      .replace(/[^A-Z0-9\s]/g, '')
      .replace(/\s+/g, '_')
      .substring(0, 20);
    
    setFormData(prev => ({
      ...prev,
      wkf_code: `WKF_${code}`
    }));
  };

  const getArticoloName = (id: number) => {
    const articolo = articoli.find(a => a.id === id);
    return articolo ? `${articolo.codice} - ${articolo.nome}` : '';
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
          {workflow ? 'Modifica Workflow Template' : 'Nuovo Workflow Template'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Configura un template workflow riutilizzabile per i tuoi processi
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* Informazioni Base */}
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Nome Workflow"
              value={formData.nome}
              onChange={handleInputChange('nome')}
              error={!!errors.nome}
              helperText={errors.nome || 'Nome identificativo del workflow'}
              required
            />
          </Grid>


          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Descrizione"
              value={formData.descrizione}
              onChange={handleInputChange('descrizione')}
              multiline
              rows={3}
              helperText="Descrizione dettagliata del workflow e quando utilizzarlo"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Durata Stimata (giorni)"
              type="number"
              value={formData.durata_stimata_giorni || ''}
              onChange={handleInputChange('durata_stimata_giorni')}
              error={!!errors.durata_stimata_giorni}
              helperText={errors.durata_stimata_giorni || 'Durata stimata totale del workflow'}
              inputProps={{ min: 1, max: 365 }}
            />
          </Grid>

          {/* Configurazioni Avanzate */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
                 onClick={() => setShowAdvanced(!showAdvanced)}>
              <Typography variant="subtitle2" sx={{ mr: 1 }}>
                Configurazioni Avanzate
              </Typography>
              {showAdvanced ? <ExpandLess /> : <ExpandMore />}
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Collapse in={showAdvanced}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      fullWidth
                      label="Codice Workflow"
                      value={formData.wkf_code}
                      onChange={handleInputChange('wkf_code')}
                      error={!!errors.wkf_code}
                      helperText={errors.wkf_code || 'Codice univoco per il workflow (es: WKF_I24_STD)'}
                      placeholder="WKF_NOME_WORKFLOW"
                    />
                    <Button
                      variant="outlined"
                      onClick={generateWorkflowCode}
                      sx={{ minWidth: 'auto', px: 2 }}
                      disabled={!formData.nome}
                    >
                      Auto
                    </Button>
                  </Box>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Descrizione Tecnica"
                    value={formData.wkf_description}
                    onChange={handleInputChange('wkf_description')}
                    multiline
                    rows={2}
                    helperText="Descrizione tecnica dettagliata per sviluppatori e amministratori"
                  />
                </Grid>
              </Grid>
            </Collapse>
          </Grid>

          {/* Azioni */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', pt: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Cancel />}
                onClick={onCancel}
                disabled={loading}
              >
                Annulla
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={<Save />}
                loading={loading}
                disabled={loading}
                sx={{ boxShadow: 2 }}
              >
                {workflow ? 'Aggiorna Workflow' : 'Crea Workflow'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default WorkflowTemplateForm;
