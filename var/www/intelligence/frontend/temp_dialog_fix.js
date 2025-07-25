// Cerca questa funzione in WorkflowManagement.tsx:
const handleViewDetails = (workflow: WorkflowTemplate) => {
  console.log('Apro dettagli workflow:', workflow);
  alert(`Dettagli workflow: ${workflow.nome}`);
  // TODO: Aprire dialog milestone
};

// E sostituiscila con:
const [showMilestoneDialog, setShowMilestoneDialog] = useState(false);
const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowTemplate | null>(null);
const [workflowMilestones, setWorkflowMilestones] = useState<any[]>([]);

const handleViewDetails = async (workflow: WorkflowTemplate) => {
  console.log('Apro dettagli workflow:', workflow);
  setSelectedWorkflow(workflow);
  setShowMilestoneDialog(true);
  
  // Carica le milestone del workflow
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`/api/v1/admin/workflow-config/workflow-templates/${workflow.id}/milestones`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      setWorkflowMilestones(data.milestones || []);
    }
  } catch (error) {
    console.error('Errore caricamento milestone:', error);
  }
};
