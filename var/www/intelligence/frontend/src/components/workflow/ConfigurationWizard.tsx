// components/workflow/ConfigurationWizard.tsx
// Wizard guidato per configurazione Workflow - IntelligenceHUB

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Typography,
  TextField,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  FormControlLabel,
  LinearProgress
} from '@mui/material';
import {
  Timeline,
  Assignment,
  CheckCircle,
  Settings,
  Launch,
  ArrowForward,
  ArrowBack
} from '@mui/icons-material';
import { workflowApi, Articolo, KitCommerciale } from '../../services/workflowApi';

interface ConfigurationWizardProps {
  open: boolean;
  onClose: () => void;
  onWorkflowCreated: () => void;
}

interface WizardData {
  nome: string;
  descrizione: string;
  workflowType: 'simple' | 'complete';
  includeMilestones: boolean;
  includeTasks: boolean;
  autoGenerate: boolean;
}

const ConfigurationWizard: React.FC<ConfigurationWizardProps> = ({
  open,
  onClose,
  onWorkflowCreated
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [articoli, setArticoli] = useState<Articolo[]>([]);
  const [kits, setKits] = useState<KitCommerciale[]>([]);
  const [loading, setLoading] = useState(false);
  const [wizardData, setWizardData] = useState<WizardData>({
    nome: "",
    descrizione: "",
    workflowType: "simple",
    includeMilestones: true,
    includeTasks: true,
    autoGenerate: false
  });

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [articoliResponse, kitsResponse] = await Promise.all([
        workflowApi.getArticoli(),
        workflowApi.getKitCommerciali()
      ]);

      if (articoliResponse.success && articoliResponse.data) {
        setArticoli(articoliResponse.data);
      }

      if (kitsResponse.success && kitsResponse.data) {
        setKits(kitsResponse.data);
      }
    } catch (error) {
      console.error('Errore caricamento dati:', error);
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    {
      label: 'Configurazione Base',
      description: 'Configura nome e descrizione del workflow'
    },
    {
      label: 'Tipo Workflow',
      description: 'Configura il tipo di workflow da creare'
    },
    {
      label: 'Conferma e Crea',
      description: 'Rivedi la configurazione e crea il workflow'
    }
  ];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setWizardData({
      nome: "",
      descrizione: "",
      workflowType: "simple",
      includeMilestones: true,
      includeTasks: true,
      autoGenerate: false
    });
  };

  const handleCreateWorkflow = async () => {
    if (!wizardData.nome.trim()) return;

    setLoading(true);
    try {
      const workflowData = {
        nome: wizardData.nome,
        descrizione: wizardData.descrizione || `Workflow ${wizardData.nome}`,
        durata_stimata_giorni: 30,
        wkf_code: `WKF_${wizardData.nome.replace(/s+/g, "_").toUpperCase()}`,
        wkf_description: wizardData.descrizione || `Workflow per ${wizardData.nome}`,
        attivo: true
      };

      const response = await workflowApi.createWorkflowTemplate(workflowData);
      
      if (response.success) {
        onWorkflowCreated();
        onClose();
        handleReset();
      }
    } catch (error) {
      console.error("Errore creazione workflow:", error);
    } finally {
      setLoading(false);
    }
  };

  const canProceed = (step: number) => {
    switch (step) {
      case 0:
        return wizardData.nome.trim() !== "";
      case 1:
        return true;
      case 2:
        return true;
      default:
        return false;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ sx: { borderRadius: 3, minHeight: '70vh' } }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Settings color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Configuration Wizard
          </Typography>
        </Box>
        <Typography variant="body2" color="textSecondary">
          Crea rapidamente un workflow template guidato step-by-step
        </Typography>
      </DialogTitle>

      <DialogContent sx={{ px: 3 }}>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {step.label}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {step.description}
                </Typography>
              </StepLabel>
              <StepContent>
                {/* Step 0: Configurazione Base */}
                {index === 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 2 }}>
                      Configura le informazioni base del workflow:
                    </Typography>
                    
                    <Grid container spacing={3}>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Nome Workflow"
                          placeholder="Es: Workflow Gestione Commesse"
                          value={wizardData.nome}
                          onChange={(e) => setWizardData(prev => ({ ...prev, nome: e.target.value }))}
                          variant="outlined"
                          required
                          sx={{ mb: 2 }}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Descrizione" 
                          placeholder="Descrizione dettagliata del workflow..."
                          value={wizardData.descrizione}
                          onChange={(e) => setWizardData(prev => ({ ...prev, descrizione: e.target.value }))}
                          variant="outlined"
                          multiline
                          rows={3}
                        />
                      </Grid>
                    </Grid>
                  </Box>
                )}

                {/* Step 1: Tipo Workflow */
                {index === 1 && (
                  <Box sx={{ mt: 2 }}>

                    <Typography variant="subtitle2" sx={{ mb: 2 }}>
                      Configura le opzioni del workflow:
                    </Typography>

                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={wizardData.includeMilestones}
                                onChange={(e) => setWizardData(prev => ({
                                  ...prev,
                                  includeMilestones: e.target.checked
                                }))}
                              />
                            }
                            label=""
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary="Includi Milestone Template"
                          secondary="Crea milestone predefinite per questo tipo di servizio"
                        />
                      </ListItem>

                      <ListItem>
                        <ListItemIcon>
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={wizardData.includeTasks}
                                onChange={(e) => setWizardData(prev => ({
                                  ...prev,
                                  includeTasks: e.target.checked
                                }))}
                                disabled={!wizardData.includeMilestones}
                              />
                            }
                            label=""
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary="Includi Task Template"
                          secondary="Aggiungi task predefiniti alle milestone"
                        />
                      </ListItem>

                      <ListItem>
                        <ListItemIcon>
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={wizardData.autoGenerate}
                                onChange={(e) => setWizardData(prev => ({
                                  ...prev,
                                  autoGenerate: e.target.checked
                                }))}
                              />
                            }
                            label=""
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary="Configurazione Automatica"
                          secondary="Genera automaticamente milestone e task basati sul tipo di servizio"
                        />
                      </ListItem>
                    </List>
                  </Box>
                )}


                {/* Step 2: Conferma */}
                {index === 2 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 2 }}>
                      Riepilogo configurazione:
                    </Typography>
                    <Card variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" color="textSecondary">
                              NOME WORKFLOW
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 600 }}>
                              {wizardData.nome}
                            </Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" color="textSecondary">
                              TIPO WORKFLOW
                            </Typography>
                            <Typography variant="body1">
                              {wizardData.workflowType === "simple" ? "Semplice" : "Completo"}
                            </Typography>
                          </Grid>
                          <Grid item xs={12}>
                            <Typography variant="caption" color="textSecondary">
                              DESCRIZIONE
                            </Typography>
                            <Typography variant="body1">
                              {wizardData.descrizione || "Nessuna descrizione fornita"}
                            </Typography>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Box>
                )}

                <Box sx={{ mb: 2, mt: 3 }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      disabled={index === 0}
                      onClick={handleBack}
                      startIcon={<ArrowBack />}
                    >
                      Indietro
                    </Button>
                    
                    {index === steps.length - 1 ? (
                      <Button
                        variant="contained"
                        onClick={handleCreateWorkflow}
                        disabled={!canProceed(index) || loading}
                        startIcon={<Launch />}
                        sx={{ boxShadow: 2 }}
                      >
                        Crea Workflow
                      </Button>
                    ) : (
                      <Button
                        variant="contained"
                        onClick={handleNext}
                        disabled={!canProceed(index)}
                        endIcon={<ArrowForward />}
                      >
                        Avanti
                      </Button>
                    )}
                  </Box>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>

        {loading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress />
            <Typography variant="body2" sx={{ textAlign: 'center', mt: 1 }}>
              Creazione workflow in corso...
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose} disabled={loading}>
          Chiudi
        </Button>
        {activeStep === steps.length && (
          <Button onClick={handleReset} variant="outlined">
            Crea Altro Workflow
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ConfigurationWizard;
