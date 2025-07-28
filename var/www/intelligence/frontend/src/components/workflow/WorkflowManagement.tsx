// components/workflow/WorkflowManagement.tsx
// Componente principale per gestione Workflow - IntelligenceHUB

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Tabs, 
  Tab, 
  Paper, 
  Typography, 
  Button, 
  Alert,
  CircularProgress,
  Fab,
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  List, 
  ListItem, 
  ListItemText, 
  Chip 
} from '@mui/material';
import { Add, Dashboard, Settings, Timeline, Assignment } from '@mui/icons-material';
import WorkflowDashboard from './WorkflowDashboard';
import WorkflowTemplateList from './WorkflowTemplateList';
import WorkflowTemplateForm from './WorkflowTemplateForm';
import ConfigurationWizard from './ConfigurationWizard';
import MilestoneTemplateLibrary from './MilestoneTemplateLibrary';
import { workflowApi, WorkflowTemplate } from '../../services/workflowApi';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`workflow-tabpanel-${index}`}
      aria-labelledby={`workflow-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const WorkflowManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [workflows, setWorkflows] = useState<WorkflowTemplate[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showWizard, setShowWizard] = useState(false);
  
  // Stati per dialog milestone
  const [showMilestoneDialog, setShowMilestoneDialog] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowTemplate | null>(null);
  const [workflowMilestones, setWorkflowMilestones] = useState<any[]>([]);
  const [showManageMilestonesDialog, setShowManageMilestonesDialog] = useState(false);
  const [availableTemplates, setAvailableTemplates] = useState<any[]>([]);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState<WorkflowTemplate | null>(null);

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await workflowApi.getWorkflowTemplates();
      if (response.success && response.data) {
        setWorkflows(response.data);
      } else {
        setError(response.error || 'Errore caricamento workflow');
      }
    } catch (err) {
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleCreateWorkflow = () => {
    setShowCreateForm(true);
    setActiveTab(1); // Vai al tab Templates
  };

  const handleShowWizard = () => {
    setShowWizard(true);
  };

  const handleEditWorkflow = (workflow: WorkflowTemplate) => {
    console.log("Modifica workflow:", workflow);
    setEditingWorkflow(workflow);
    setShowEditForm(true);
  };

  const handleCloneWorkflow = async (workflow: WorkflowTemplate) => {
    const newName = prompt(`Clona workflow "${workflow.nome}"\n\nInserisci nuovo nome:`, `${workflow.nome} - Copia`);
    if (!newName) return;
    
    try {
      const response = await workflowApi.createWorkflowTemplate({
        nome: newName,
        descrizione: workflow.descrizione,
        articolo_id: workflow.articolo_id,
        durata_stimata_giorni: workflow.durata_stimata_giorni,
        wkf_code: `${workflow.wkf_code || ""}_COPY`,
        wkf_description: workflow.wkf_description,
        attivo: true,
        ordine: workflow.ordine + 1
      });
      
      if (response.success) {
        alert("Workflow clonato con successo!");
        loadWorkflows();
      } else {
        alert(`Errore: ${response.error || "Impossibile clonare workflow"}`);
      }
    } catch (error) {
      console.error("Errore clonazione:", error);
      alert("Errore di connessione");
    }
  };

  const handleDeleteWorkflow = async (workflow: WorkflowTemplate) => {
    if (!confirm(`Sei sicuro di voler eliminare "${workflow.nome}"?\n\nQuesta azione non può essere annullata.`)) return;
    
    try {
      const response = await fetch(`/api/v1/admin/workflow-config/workflow-templates/${workflow.id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        }
      });
      
      if (response.ok) {
        alert("Workflow eliminato con successo!");
        loadWorkflows();
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail || "Impossibile eliminare workflow"}`);
      }
    } catch (error) {
      console.error("Errore eliminazione:", error);
      alert("Errore di connessione");
    }
  };

  const handleViewDetails = async (workflow: WorkflowTemplate) => {
    setSelectedWorkflow(workflow);
    setShowMilestoneDialog(true);
    try {
      const response = await workflowApi.getWorkflowTemplate(workflow.id);
      if (response.success && response.data) {
        setWorkflowMilestones(response.data.milestones || []);
      }
    } catch (error) {
      console.error("Errore caricamento milestone:", error);
    }
  };

  const handleRemoveMilestone = async (milestoneId: number) => {
    if (!selectedWorkflow) return;
    
    if (!confirm("Sei sicuro di voler rimuovere questa milestone dal workflow?")) return;
    
    try {
      const response = await fetch(`/api/v1/admin/workflow-config/workflow-templates/${selectedWorkflow.id}/milestones/${milestoneId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        }
      });
      
      if (response.ok) {
        alert("Milestone rimossa con successo!");
        const updatedResponse = await workflowApi.getWorkflowTemplate(selectedWorkflow.id);
        if (updatedResponse.success && updatedResponse.data) {
          setWorkflowMilestones(updatedResponse.data.milestones || []);
        }
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail || "Impossibile rimuovere milestone"}`);
      }
    } catch (error) {
      console.error("Errore rimozione:", error);
      alert("Errore di connessione");
    }
  };

  const handleAssignTemplate = async (templateId: number) => {
    if (!selectedWorkflow) return;
    
    try {
      const response = await fetch(`/api/v1/admin/workflow-config/workflow-templates/${selectedWorkflow.id}/milestones/${templateId}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ordine: workflowMilestones.length + 1,
          durata_stimata_giorni: null
        })
      });
      
      if (response.ok) {
        alert("Template milestone associato con successo!");
        // Ricarica le milestone del workflow
        const updatedResponse = await workflowApi.getWorkflowTemplate(selectedWorkflow.id);
        if (updatedResponse.success && updatedResponse.data) {
          setWorkflowMilestones(updatedResponse.data.milestones || []);
        }
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail || "Impossibile associare template"}`);
      }
    } catch (error) {
      console.error("Errore associazione:", error);
      alert("Errore di connessione");
    }
  };

  const handleManageMilestones = async () => {
    setShowMilestoneDialog(false);
    setShowManageMilestonesDialog(true);
    
    // Carica i template milestone disponibili
    try {
      const response = await fetch("/api/v1/admin/milestone-templates/", {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        }
      });
      if (response.ok) {
        const templates = await response.json();
        setAvailableTemplates(templates);
      }
    } catch (error) {
      console.error("Errore caricamento template:", error);
    }
  };

  const handleWorkflowCreated = () => {
    setShowCreateForm(false);
    loadWorkflows();
  };

  return (
    <Box sx={{ width: '100%' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="workflow tabs">
            <Tab icon={<Dashboard />} label="Dashboard" />
            <Tab icon={<Settings />} label="Workflow Templates" />
            <Tab icon={<Timeline />} label="Milestone Templates" />
          </Tabs>
        </Box>

        <TabPanel value={activeTab} index={0}>
          <WorkflowDashboard workflows={workflows} onReload={loadWorkflows} />
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <WorkflowTemplateList
            workflows={workflows}
            onReload={loadWorkflows}
            showCreateForm={showCreateForm}
            onCloseCreateForm={() => setShowCreateForm(false)}
            onWorkflowCreated={handleWorkflowCreated}
            onViewDetails={handleViewDetails}
            onEditWorkflow={handleEditWorkflow}
            onCloneWorkflow={handleCloneWorkflow}
            onDeleteWorkflow={handleDeleteWorkflow}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <MilestoneTemplateLibrary />
        </TabPanel>
      </Paper>

      {/* FAB per azioni rapide */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleCreateWorkflow}
      >
        <Add />
      </Fab>

      {/* Dialog Milestone Details */}
      <Dialog
        open={showMilestoneDialog}
        onClose={() => setShowMilestoneDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Milestone del Workflow: {selectedWorkflow?.nome}
        </DialogTitle>
        <DialogContent>
          {workflowMilestones.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2 }}>
              Nessuna milestone configurata per questo workflow
            </Typography>
          ) : (
            <List>
              {workflowMilestones.map((milestone, index) => (
                <ListItem key={milestone.id || index} divider>
                  <ListItemText
                    primary={`${milestone.ordine}. ${milestone.nome}`}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {milestone.descrizione || "Nessuna descrizione"}
                        </Typography>
                        <Box sx={{ mt: 1, display: "flex", gap: 1 }}>
                          <Chip label={milestone.tipo_milestone} size="small" />
                          <Chip label={`${milestone.durata_stimata_giorni || milestone.sla_giorni} giorni`} size="small" />
                          <Chip label={`${milestone.task_templates?.length || 0} task`} size="small" />
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMilestoneDialog(false)}>
            Chiudi
          </Button>
          <Button variant="contained" onClick={handleManageMilestones}>
            Gestisci Milestone
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog Modifica Workflow */}
      <Dialog
        open={showEditForm}
        onClose={() => {
          setShowEditForm(false);
          setEditingWorkflow(null);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogContent>
          {editingWorkflow && (
            <WorkflowTemplateForm
              workflow={editingWorkflow}
              articoli={[]}
              onCancel={() => {
                setShowEditForm(false);
                setEditingWorkflow(null);
              }}
              onSuccess={() => {
                setShowEditForm(false);
                setEditingWorkflow(null);
                loadWorkflows();
              }}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Dialog Gestione Milestone */}
      <Dialog
        open={showManageMilestonesDialog}
        onClose={() => setShowManageMilestonesDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Gestione Milestone per: {selectedWorkflow?.nome}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", gap: 3 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" gutterBottom>Template Milestone Disponibili</Typography>
              {availableTemplates.length === 0 ? (
                <Typography color="text.secondary">Caricamento template...</Typography>
              ) : (
                <List>
                  {availableTemplates.map((template) => (
                    <ListItem key={template.id} divider>
                      <ListItemText primary={template.nome} secondary={template.descrizione} />
                      <Button variant="contained" size="small" onClick={() => handleAssignTemplate(template.id)}>Assegna</Button>
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" gutterBottom>Milestone Assegnate</Typography>
              {workflowMilestones.length === 0 ? (
                <Typography color="text.secondary">Nessuna milestone assegnata</Typography>
              ) : (
                <List>
                  {workflowMilestones.map((milestone, index) => (
                    <ListItem key={milestone.id || index} divider>
                      <ListItemText primary={`${milestone.ordine}. ${milestone.nome}`} />
                      <Button variant="outlined" color="error" size="small" onClick={() => handleRemoveMilestone(milestone.id)}>Rimuovi</Button>
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowManageMilestonesDialog(false)}>Chiudi</Button>
        </DialogActions>
      </Dialog>

      {/* Dialog Modifica Workflow */}
      <Dialog
        open={showEditForm}
        onClose={() => {
          setShowEditForm(false);
          setEditingWorkflow(null);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogContent>
          {editingWorkflow && (
            <WorkflowTemplateForm
              workflow={editingWorkflow}
              articoli={[]}
              onCancel={() => {
                setShowEditForm(false);
                setEditingWorkflow(null);
              }}
              onSuccess={() => {
                setShowEditForm(false);
                setEditingWorkflow(null);
                loadWorkflows();
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};


export default WorkflowManagement;
