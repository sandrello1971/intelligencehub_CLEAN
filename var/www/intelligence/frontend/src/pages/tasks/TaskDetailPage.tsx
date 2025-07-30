
// src/pages/tasks/TaskDetailPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Chip,
  Button,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
  Divider,
  Card,
  CardContent
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Task as TaskIcon,
  Person as PersonIcon,
  CalendarToday as CalendarIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';

interface TaskDetail {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  owner: string;
  owner_name: string;
  due_date: string | null;
  created_at: string;
  ticket_id: string;
  ticket_code: string;
  siblings: Array<{id: string, title: string, status: string}>;
}

const TaskDetailPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  
  // Form state per editing
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: '',
    priority: '',
    owner: ''
  });

  useEffect(() => {
    if (taskId) {
      loadTaskDetail();
    }
  }, [taskId]);

  const loadTaskDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/tasks/${taskId}`);
      
      if (!response.ok) {
        throw new Error('Task non trovato');
      }
      
      const taskData = await response.json();
      const normalizedTaskData = {...taskData, priority: taskData.priority || taskData.priorita || "normale"}; setTask(normalizedTaskData);
      setFormData({
        title: taskData.title,
        description: taskData.description || '',
        status: taskData.status,
        priority: taskData.priority,
        owner: taskData.owner || ''
      });
    } catch (err: any) {
      setError(err.message || 'Errore nel caricamento del task');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await fetch(`/api/v1/tasks/${taskId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Errore nel salvataggio');
      }

      await loadTaskDetail(); // Ricarica i dati
      setEditMode(false);
    } catch (err: any) {
      setError(err.message || 'Errore nel salvataggio');
    } finally {
      setSaving(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase() || "") {
      case 'todo': return 'primary';
      case 'in_progress': return 'warning';
      case 'completed': case 'chiuso': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase() || "") {
      case 'bassa': return 'success';
      case 'normale': return 'primary';
      case 'alta': return 'warning';
      case 'critica': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !task) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || 'Task non trovato'}
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(-1)}
        >
          Torna Indietro
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate(-1)}
            variant="outlined"
          >
            Indietro
          </Button>
          <TaskIcon sx={{ color: 'primary.main' }} />
          <Typography variant="h4" fontWeight={600}>
            Dettaglio Task
          </Typography>
        </Box>
        <Typography variant="body1" color="textSecondary">
          Gestione del task operativo
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Informazioni Principali */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" fontWeight={600}>
                Informazioni Task
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {!editMode ? (
                  <Button
                    variant="contained"
                    onClick={() => setEditMode(true)}
                  >
                    Modifica
                  </Button>
                ) : (
                  <>
                    <Button
                      variant="outlined"
                      onClick={() => {
                        setEditMode(false);
                        setFormData({
                          title: task.title,
                          description: task.description || '',
                          status: task.status,
                          priority: task.priority,
                          owner: task.owner || ''
                        });
                      }}
                    >
                      Annulla
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<SaveIcon />}
                      onClick={handleSave}
                      disabled={saving}
                    >
                      {saving ? 'Salvando...' : 'Salva'}
                    </Button>
                  </>
                )}
              </Box>
            </Box>

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  label="Titolo"
                  value={editMode ? formData.title : task.title}
                  onChange={(e) => editMode && setFormData({...formData, title: e.target.value})}
                  fullWidth
                  disabled={!editMode}
                  variant={editMode ? 'outlined' : 'filled'}
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  label="Descrizione"
                  value={editMode ? formData.description : task.description}
                  onChange={(e) => editMode && setFormData({...formData, description: e.target.value})}
                  fullWidth
                  multiline
                  rows={4}
                  disabled={!editMode}
                  variant={editMode ? 'outlined' : 'filled'}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="Status"
                  select
                  value={editMode ? formData.status : task.status}
                  onChange={(e) => editMode && setFormData({...formData, status: e.target.value})}
                  fullWidth
                  disabled={!editMode}
                  variant={editMode ? 'outlined' : 'filled'}
                >
                  <MenuItem value="todo">Da Fare</MenuItem>
                  <MenuItem value="in_progress">In Corso</MenuItem>
                  <MenuItem value="completed">Completato</MenuItem>
                  <MenuItem value="cancelled">Annullato</MenuItem>
                </TextField>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="Priorità"
                  select
                  value={editMode ? formData.priority : task.priority}
                  onChange={(e) => editMode && setFormData({...formData, priority: e.target.value})}
                  fullWidth
                  disabled={!editMode}
                  variant={editMode ? 'outlined' : 'filled'}
                >
                  <MenuItem value="bassa">Bassa</MenuItem>
                  <MenuItem value="normale">Normale</MenuItem>
                  <MenuItem value="alta">Alta</MenuItem>
                  <MenuItem value="critica">Critica</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Status e Priorità */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Status
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Stato Attuale
                </Typography>
                <Chip 
                  label={task.status} 
                  color={getStatusColor(task.status) as any}
                  variant="filled"
                />
              </Box>
              <Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Priorità
                </Typography>
                <Chip 
                  label={task.priority} 
                  color={getPriorityColor(task.priority) as any}
                  variant="outlined"
                />
              </Box>
            </Box>
          </Paper>

          {/* Informazioni Ticket */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Ticket Collegato
            </Typography>
            <Box 
              sx={{ cursor: 'pointer', '&:hover': { backgroundColor: 'action.hover' }, p: 1, borderRadius: 1 }}
              onClick={() => navigate(`/tickets/${task.ticket_id}`)}
            >
              <Typography variant="body2" color="primary.main" fontWeight={500}>
                {task.ticket_code}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Clicca per visualizzare il ticket
              </Typography>
            </Box>
          </Paper>

          {/* Owner */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              <PersonIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Owner
            </Typography>
            <Typography variant="body2">
              {task.owner_name || 'Non assegnato'}
            </Typography>
          </Paper>

          {/* Date */}
          {task.due_date && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                <CalendarIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Scadenza
              </Typography>
              <Typography variant="body2">
                {new Date(task.due_date).toLocaleDateString('it-IT')}
              </Typography>
            </Paper>
          )}
        </Grid>

        {/* Task Correlati */}
        {task.siblings && task.siblings.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                <AssignmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Altri Task del Ticket
              </Typography>
              <Grid container spacing={2}>
                {task.siblings.map((sibling) => (
                  <Grid item xs={12} sm={6} md={4} key={sibling.id}>
                    <Card 
                      variant="outlined" 
                      sx={{ 
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                      onClick={() => navigate(`/tasks/${sibling.id}`)}
                    >
                      <CardContent sx={{ pb: 2 }}>
                        <Typography variant="body2" fontWeight={500} noWrap>
                          {sibling.title}
                        </Typography>
                        <Chip 
                          label={sibling.status} 
                          size="small" 
                          color={getStatusColor(sibling.status) as any}
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default TaskDetailPage;
