
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
  priorita: string;
  owner: string;
  owner_name: string;
  due_date: string | null;
  created_at: string;
  ticket_id: string | null;
  ticket_code: string;
  siblings: Array<{id: string, title: string, status: string}>;
  note: string | null;
}

interface User {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

const TaskDetailPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  
  // Form state per editing
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: '',
    priority: '',
    owner: '',
  });
    note: ''

  useEffect(() => {
    if (taskId) {
      loadTaskDetail();
    }
  }, [taskId]);

  useEffect(() => {
    loadUsers();
  }, []);

  const handleGoBack = () => {
    if (task?.ticket_id) {
      navigate(`/tickets/${task.ticket_id}`);
    } else {
      navigate(-1);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await fetch('/api/v1/users/');
      if (response.ok) {
        const userData = await response.json();
        setUsers(userData);
      }
    } catch (error) {
      console.error('Errore caricamento utenti:', error);
    }
  };

  const loadTaskDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/tasks/${taskId}`);
      
      if (!response.ok) {
        throw new Error('Task non trovato');
      }
      
      const taskData = await response.json();
      
      // Normalizza i dati per gestire sia 'priority' che 'priorita'
      const normalizedTaskData = {
        ...taskData,
        priority: taskData.priority || taskData.priorita || 'normale'
      };
      
      setTask(normalizedTaskData);
      
      // Inizializza form data
      setFormData({
        title: normalizedTaskData.title || '',
        description: normalizedTaskData.description || '',
        status: normalizedTaskData.status || '',
        priority: normalizedTaskData.priority || '',
        owner: normalizedTaskData.owner || '',
        note: normalizedTaskData.note || ''
      });
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Task non trovato');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!task) return;
    
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
      
      // Ricarica i dati aggiornati
      await loadTaskDetail();
      setEditMode(false);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore nel salvataggio');
    } finally {
      setSaving(false);
    }
  };

  const getPriorityColor = (priority: string | undefined) => {
    switch (priority?.toLowerCase()) {
      case 'alta':
      case 'critica':
        return 'error';
      case 'media':
      case 'normale':
        return 'warning';
      case 'bassa':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string | undefined) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'completato':
      case 'chiuso':
        return 'success';
      case 'in_progress':
      case 'in corso':
        return 'info';
      case 'todo':
      case 'da fare':
      case 'aperto':
        return 'warning';
      case 'cancelled':
      case 'annullato':
        return 'error';
      default:
        return 'default';
    }
  };

  const getUserDisplayName = (userId: string) => {
    const user = users.find(u => u.id === userId);
    return user ? `${user.first_name} ${user.last_name}` : 'Non assegnato';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
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
          onClick={handleGoBack}
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
            onClick={handleGoBack}
            variant="outlined"
          >
            Indietro
          </Button>
          <TaskIcon sx={{ color: 'primary.main' }} />
          <Typography variant="h4" fontWeight={600}>
            Dettaglio Task
          </Typography>
        </Box>
        <Typography variant="subtitle1" color="textSecondary">
          Gestione del task operativo
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Informazioni Principali */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" fontWeight={600}>
                Informazioni Task
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {!editMode ? (
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={() => setEditMode(true)}
                    size="small"
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
                          title: task.title || '',
                          description: task.description || '',
                          status: task.status || '',
                          priority: task.priority || '',
                          owner: task.owner || '',
                        });
                          note: task.note || ''
                      }}
                      size="small"
                    >
                      Annulla
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<SaveIcon />}
                      onClick={handleSave}
                      disabled={saving}
                      size="small"
                    >
                      {saving ? 'Salvataggio...' : 'Salva'}
                    </Button>
                  </>
                )}
              </Box>
            </Box>

            <Grid container spacing={3}>
              <Grid item xs={12}>
                {editMode ? (
                  <TextField
                    fullWidth
                    label="Titolo"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                  />
                ) : (
                  <>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Titolo
                    </Typography>
                    <Typography variant="h6" fontWeight={500}>
                      {task.title}
                    </Typography>
                  </>
                )}
              </Grid>

              <Grid item xs={12}>
                {editMode ? (
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Descrizione"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                  />
                ) : (
                  <>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Descrizione
                    </Typography>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {task.description || 'Nessuna descrizione disponibile'}
                    </Typography>
                  </>
                )}
              </Grid>

              <Grid item xs={12}>
                {editMode ? (
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Note"
                    value={formData.note}
                    onChange={(e) => setFormData({...formData, note: e.target.value})}
                  />
                ) : (
                  <>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Note
                    </Typography>
                    <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                      {task.note || "Nessuna nota disponibile"}
                    </Typography>
                  </>
                )}
              </Grid>

              <Grid item xs={6}>
                {editMode ? (
                  <TextField
                    select
                    fullWidth
                    label="Status"
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                  >
                    <MenuItem value="todo">Da Fare</MenuItem>
                    <MenuItem value="in_progress">In Corso</MenuItem>
                    <MenuItem value="completed">Completato</MenuItem>
                    <MenuItem value="cancelled">Annullato</MenuItem>
                  </TextField>
                ) : (
                  <>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Status
                    </Typography>
                    <Chip
                      label={task.status || 'Da Fare'}
                      color={getStatusColor(task.status)}
                      size="small"
                    />
                  </>
                )}
              </Grid>

              <Grid item xs={6}>
                {editMode ? (
                  <TextField
                    select
                    fullWidth
                    label="Priorità"
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value})}
                  >
                    <MenuItem value="bassa">Bassa</MenuItem>
                    <MenuItem value="normale">Normale</MenuItem>
                    <MenuItem value="alta">Alta</MenuItem>
                    <MenuItem value="critica">Critica</MenuItem>
                  </TextField>
                ) : (
                  <>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Priorità
                    </Typography>
                    <Chip
                      label={task.priority || 'Normale'}
                      color={getPriorityColor(task.priority)}
                      size="small"
                    />
                  </>
                )}
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Status */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Status
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2">
                <strong>Stato Attuale</strong>
              </Typography>
              <Chip
                label={task.status || 'Da Fare'}
                color={getStatusColor(task.status)}
                size="small"
                sx={{ alignSelf: 'flex-start' }}
              />
              <Typography variant="body2" sx={{ mt: 1 }}>
                <strong>Priorità</strong>
              </Typography>
              <Chip
                label={task.priority || 'Normale'}
                color={getPriorityColor(task.priority)}
                size="small"
                sx={{ alignSelf: 'flex-start' }}
              />
            </Box>
          </Paper>

          {/* Ticket Collegato */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Ticket Collegato
            </Typography>
            {task.ticket_id ? (
              <Box 
                sx={{ cursor: 'pointer', '&:hover': { backgroundColor: 'action.hover' }, p: 1, borderRadius: 1 }}
                onClick={() => navigate(`/tickets/${task.ticket_id}`)}
              >
                <Typography variant="body2" color="primary.main" fontWeight={500}>
                  {task.ticket_code || `Ticket ID: ${task.ticket_id}`}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Clicca per visualizzare il ticket
                </Typography>
              </Box>
            ) : (
              <Typography variant="body2" color="textSecondary">
                Nessun ticket collegato
              </Typography>
            )}
          </Paper>

          {/* Owner */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              <PersonIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Owner
            </Typography>
            {editMode ? (
              <TextField
                select
                fullWidth
                label="Owner"
                value={formData.owner || ''}
                onChange={(e) => setFormData({...formData, owner: e.target.value})}
                size="small"
              >
                <MenuItem value="">Nessun assegnato</MenuItem>
                {users.map((user) => (
                  <MenuItem key={user.id} value={user.id}>
                    {user.first_name} {user.last_name} ({user.email})
                  </MenuItem>
                ))}
              </TextField>
            ) : (
              <Typography variant="body2">
                {task.owner_name || getUserDisplayName(task.owner) || 'Non assegnato'}
              </Typography>
            )}
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
      </Grid>
    </Container>
  );
};

export default TaskDetailPage;
