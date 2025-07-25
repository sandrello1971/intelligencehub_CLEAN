// components/workflow/WorkflowManagement.tsx
// Componente principale per gestione Workflow - IntelligenceHUB

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Button,
  Tabs, 
  Tab, 
  Paper, 
  Typography, 
  Button, 
  Alert,
  CircularProgress,
  Fab
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
  const [showMilestoneDialog, setShowMilestoneDialog] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowTemplate | null>(null);
  const [workflowMilestones, setWorkflowMilestones] = useState<any[]>([]);

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

const handleViewDetails = (workflow: WorkflowTemplate) => {
  console.log("Apro gestione milestone per:", workflow);
  setSelectedWorkflow(workflow);
  setShowMilestoneDialog(true);

const loadWorkflowMilestones = async (workflowId: number) => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await fetch(`/api/v1/admin/workflow-config/workflow-templates/${workflowId}/milestones`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      setWorkflowMilestones(data.milestones || []);
    }
  } catch (error) {
    console.error("Errore caricamento milestone:", error);
  }
};
  loadWorkflowMilestones(workflow.id);
};

  const handleWorkflowCreated = () => {
    setShowCreateForm(false);
    loadWorkflows();
  };

  if (loading && workflows.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', minHeight: '100vh', backgroundColor: '#f5f5f5', p: 3 }}>
      <Paper elevation={1} sx={{ borderRadius: 2 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            px: 3,
            pt: 2
          }}>
            <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2' }}>
              Gestione Workflow
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Settings />}
                onClick={handleShowWizard}
                sx={{ borderRadius: 2 }}
              >
                Configuration Wizard
              </Button>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={handleCreateWorkflow}
                sx={{ borderRadius: 2, boxShadow: 2 }}
              >
                Nuovo Workflow
              </Button>
            </Box>
          </Box>

          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            sx={{ px: 3 }}
            TabIndicatorProps={{ sx: { height: 3, borderRadius: 1 } }}
          >
            <Tab 
              icon={<Dashboard />} 
              label="Dashboard" 
              sx={{ minHeight: 60, fontSize: '1rem' }}
            />
            <Tab 
              icon={<Timeline />} 
              label="Workflow Templates" 
              sx={{ minHeight: 60, fontSize: '1rem' }}
            />
            <Tab 
              icon={<Assignment />} 
              label="Milestone Templates" 
              sx={{ minHeight: 60, fontSize: '1rem' }} 
            />
          </Tabs>
        </Box>

        {error && (
          <Box sx={{ p: 2 }}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Box>
        )}

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
          />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <MilestoneTemplateLibrary />
        </TabPanel>
      </Paper>

      {/* Configuration Wizard Modal */}
      {/* Milestone Management Dialog */}
      {showMilestoneDialog && (
        <Dialog
          open={showMilestoneDialog}
          onClose={() => {
            setShowMilestoneDialog(false);
            setSelectedWorkflow(null);
          }}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            Gestione Milestone: {selectedWorkflow?.nome}
          </DialogTitle>
          <DialogContent>
            <Typography>
              Qui sarà possibile gestire le milestone del workflow.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowMilestoneDialog(false)}>
              Chiudi
            </Button>
          </DialogActions>
        </Dialog>
      )}

      {showWizard && (
        <ConfigurationWizard
          open={showWizard}
          onClose={() => setShowWizard(false)}
          onWorkflowCreated={handleWorkflowCreated}
            onViewDetails={handleViewDetails}
        />
      )}

      {/* Floating Action Button per quick actions */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          boxShadow: 4,
        }}
        onClick={handleCreateWorkflow}
      >
        <Add />
      </Fab>
    </Box>
  );
};

export default WorkflowManagement;

