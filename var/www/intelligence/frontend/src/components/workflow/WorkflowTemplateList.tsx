// components/workflow/WorkflowTemplateList.tsx
// Lista e gestione Workflow Templates - IntelligenceHUB

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  Collapse,
  Alert,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  MoreVert,
  Edit,
  Delete,
  FileCopy,
  Visibility,
  CheckCircle,
  Warning,
  Search,
  FilterList,
  Add
} from '@mui/icons-material';
import WorkflowTemplateForm from './WorkflowTemplateForm';
import { workflowApi, WorkflowTemplate, Articolo } from '../../services/workflowApi';

interface WorkflowTemplateListProps {
  workflows: WorkflowTemplate[];
  onReload: () => void;
  showCreateForm: boolean;
  onCloseCreateForm: () => void;
  onWorkflowCreated: () => void;
  onViewDetails?: (workflow: WorkflowTemplate) => void;
  onEditWorkflow?: (workflow: WorkflowTemplate) => void;
  onCloneWorkflow?: (workflow: WorkflowTemplate) => void;
  onDeleteWorkflow?: (workflow: WorkflowTemplate) => void;
}

const WorkflowTemplateList: React.FC<WorkflowTemplateListProps> = ({
  workflows,
  onEditWorkflow,
  onCloneWorkflow,
  onDeleteWorkflow,
  onReload,
  showCreateForm,
  onCloseCreateForm,
  onWorkflowCreated,
  onViewDetails
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowTemplate | null>(null);
  const [articoli, setArticoli] = useState<Articolo[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredWorkflows, setFilteredWorkflows] = useState<WorkflowTemplate[]>(workflows);

  useEffect(() => {
    loadArticoli();
  }, []);

  useEffect(() => {
    filterWorkflows();
  }, [workflows, searchTerm]);

  const loadArticoli = async () => {
    try {
      const response = await workflowApi.getArticoli();
      if (response.success && response.data) {
        setArticoli(response.data);
      }
    } catch (error) {
      console.error('Errore caricamento articoli:', error);
    }
  };

  const filterWorkflows = () => {
    if (!searchTerm) {
      setFilteredWorkflows(workflows);
      return;
    }

    const filtered = workflows.filter(workflow =>
      workflow.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      workflow.descrizione?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      workflow.wkf_code?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredWorkflows(filtered);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, workflow: WorkflowTemplate) => {
    setAnchorEl(event.currentTarget);
    setSelectedWorkflow(workflow);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedWorkflow(null);
  };

  const handleCloneWorkflow = async () => {
    if (!selectedWorkflow) return;

    try {
      const cloneData = {
        new_name: `${selectedWorkflow.nome} (Copia)`,
        clone_milestones: true,
        clone_tasks: true
      };

      const response = await workflowApi.cloneWorkflow(selectedWorkflow.id, cloneData);
      if (response.success) {
        onReload();
      }
    } catch (error) {
      console.error('Errore clonazione workflow:', error);
    }

    handleMenuClose();
  };

  const getArticoloName = (articoloId: number | null) => {
    if (!articoloId) return 'Generico';
    const articolo = articoli.find(a => a.id === articoloId);
    return articolo ? `${articolo.codice} - ${articolo.nome}` : 'N/A';
  };

  const getWorkflowStatus = (workflow: WorkflowTemplate) => {
    // Placeholder logic - in futuro verrà dalla validazione
    if (workflow.attivo) {
      return { status: 'active', color: 'success', icon: <CheckCircle /> };
    }
    return { status: 'inactive', color: 'default', icon: <Warning /> };
  };

  return (
    <Box>
      {/* Header con ricerca */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Workflow Templates ({filteredWorkflows.length})
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            placeholder="Cerca workflow..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            size="small"
            sx={{ flexGrow: 1 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
          <Button
            variant="outlined"
            startIcon={<FilterList />}
            size="small"
          >
            Filtri
          </Button>
        </Box>
      </Box>

      {/* Form di creazione */}
      <Collapse in={showCreateForm}>
        <Box sx={{ mb: 3 }}>
          <WorkflowTemplateForm
            articoli={articoli}
            onCancel={onCloseCreateForm}
            onSuccess={onWorkflowCreated}
          />
        </Box>
      </Collapse>

      {/* Lista workflow */}
      {filteredWorkflows.length === 0 ? (
        <Card sx={{ borderRadius: 3, textAlign: 'center', py: 6 }}>
          <CardContent>
            <Add sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              {searchTerm ? 'Nessun workflow trovato' : 'Nessun workflow configurato'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {searchTerm 
                ? 'Prova a modificare i termini di ricerca' 
                : 'Inizia creando il tuo primo workflow template'
              }
            </Typography>
            {!searchTerm && (
              <Button
                variant="contained"
                startIcon={<Add />}
                sx={{ mt: 2 }}
                onClick={() => {/* Trigger create form */}}
              >
                Crea Primo Workflow
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {filteredWorkflows.map((workflow) => {
            const status = getWorkflowStatus(workflow);
            
            return (
              <Grid item xs={12} md={6} lg={4} key={workflow.id}>
                <Card 
                  sx={{ 
                    borderRadius: 3, 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: 4
                    }
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600, flexGrow: 1, mr: 1 }}>
                        {workflow.nome}
                      </Typography>
                      <IconButton 
                        size="small" 
                        onClick={(e) => handleMenuOpen(e, workflow)}
                      >
                        <MoreVert />
                      </IconButton>
                    </Box>

                    {workflow.descrizione && (
                      <Typography 
                        variant="body2" 
                        color="textSecondary" 
                        sx={{ mb: 2, display: '-webkit-box', '-webkit-line-clamp': 2, '-webkit-box-orient': 'vertical', overflow: 'hidden' }}
                      >
                        {workflow.descrizione}
                      </Typography>
                    )}

                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      <Chip
                        icon={status.icon}
                        label={status.status === 'active' ? 'Attivo' : 'Inattivo'}
                        size="small"
                        color={status.color as any}
                        variant="outlined"
                      />
                      
                      {workflow.wkf_code && (
                        <Chip
                          label={workflow.wkf_code}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>

                    <Typography variant="caption" color="textSecondary">
                      <strong>Articolo:</strong> {getArticoloName(workflow.articolo_id)}
                    </Typography>
                    
                    {workflow.durata_stimata_giorni && (
                      <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                        <strong>Durata:</strong> {workflow.durata_stimata_giorni} giorni
                      </Typography>
                    )}
                  </CardContent>

                  <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                    <Button
                      size="small"
                      startIcon={<Visibility />}
                      onClick={() => onViewDetails?.(workflow)}
                    >
                      Dettagli
                    </Button>
<Button
  size="small"
                      startIcon={<Edit />}
                      variant="outlined"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log("CAZZO DI MODIFICA CLICKED:", workflow);
                        onEditWorkflow?.(workflow);
                      }}
                    >
                      Modifica
                    </Button>


                  </CardActions>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* Menu contestuale */}
<Menu
  anchorEl={anchorEl}
  open={!!anchorEl}
  onClose={() => {setAnchorEl(null); setSelectedWorkflow(null);}}
>
  <MenuItem onClick={() => {
    if (selectedWorkflow && onViewDetails) {
      onViewDetails(selectedWorkflow);
    }
    setAnchorEl(null); setSelectedWorkflow(null);
  }}>
    <Visibility fontSize="small" sx={{ mr: 1 }} />
    Visualizza Dettagli
  </MenuItem>
  <MenuItem onClick={() => {
    if (selectedWorkflow && onEditWorkflow) {
      onEditWorkflow(selectedWorkflow);
    }
    setAnchorEl(null); setSelectedWorkflow(null);
  }}>
    <Edit fontSize="small" sx={{ mr: 1 }} />
    Modifica
  </MenuItem>
  <MenuItem onClick={() => {
    if (selectedWorkflow && onCloneWorkflow) {
      onCloneWorkflow(selectedWorkflow);
    }
    setAnchorEl(null); setSelectedWorkflow(null);
  }}>
    <FileCopy fontSize="small" sx={{ mr: 1 }} />
    Clona
  </MenuItem>
  <MenuItem onClick={() => {
    if (selectedWorkflow && confirm(`Sei sicuro di voler eliminare ${selectedWorkflow.nome}?`)) {
      if (selectedWorkflow && onDeleteWorkflow) {
        onDeleteWorkflow(selectedWorkflow);
      }
    }
    setAnchorEl(null); setSelectedWorkflow(null);
  }}>
    <Delete fontSize="small" sx={{ mr: 1 }} />
    Elimina
  </MenuItem>
</Menu>


    </Box>
  );
};

export default WorkflowTemplateList;
