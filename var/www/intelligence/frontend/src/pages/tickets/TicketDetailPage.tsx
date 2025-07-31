// src/pages/tickets/TicketDetailPage.tsx
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
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Assignment as AssignmentIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  CalendarToday as CalendarIcon,
  Task as TaskIcon,
  CheckCircle as CheckCircleIcon,
  HourglassEmpty as HourglassEmptyIcon,
  Edit as EditIcon
} from '@mui/icons-material';

interface TicketDetail {
  id: string;
  ticket_code: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  owner: string;
  customer_name: string;
  company_id: number;
  due_date: string | null;
  created_at: string;
  note: string | null;
  tasks: Array<{
    id: string;
    title: string;
    description: string;
    status: string;
    priority: string;
    owner_name: string | null;
    due_date: string | null;
  }>;
  tasks_stats: {
    total: number;
    completed: number;
    pending: number;
  };
  account_manager_id: string | null;
  account_manager_name: string | null;
}

const TicketDetailPage: React.FC = () => {
  const { ticketId } = useParams<{ ticketId: string }>();
  const navigate = useNavigate();
  
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: '',
    priority: '',
    note: ''
  });

  useEffect(() => {
    if (ticketId) {
      loadTicketDetail();
    }
  }, [ticketId]);

  const loadTicketDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/tickets/${ticketId}`);
      
      if (!response.ok) {
        throw new Error('Ticket non trovato');
      }
      
      const ticketData = await response.json();
      setTicket(ticketData);
      setFormData({
        title: ticketData.title,
        description: ticketData.description || '',
        status: ticketData.status,
        priority: ticketData.priority
      });
    } catch (err: any) {
      setError(err.message || 'Errore nel caricamento del ticket');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await fetch(`/api/v1/tickets/${ticketId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Errore nel salvataggio');
      }

      await loadTicketDetail();
      setEditMode(false);
    } catch (err: any) {
      setError(err.message || 'Errore nel salvataggio');
    } finally {
      setSaving(false);
    }
  };

  const handleTaskClick = (taskId: string) => {
    navigate(`/tasks/${taskId}`);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'aperto': return 'primary';
      case 'in_corso': return 'warning';
      case 'chiuso': return 'success';
      case 'annullato': return 'error';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'bassa': return 'success';
      case 'media': return 'primary';
      case 'alta': return 'warning';
      case 'critica': return 'error';
      default: return 'default';
    }
  };

  const getCompletionPercentage = () => {
    if (!ticket?.tasks_stats || ticket.tasks_stats.total === 0) return 0;
    return Math.round((ticket.tasks_stats.completed / ticket.tasks_stats.total) * 100);
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

  if (error || !ticket) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || 'Ticket non trovato'}
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
          <AssignmentIcon sx={{ color: 'primary.main' }} />
          <Typography variant="h4" fontWeight={600}>
            {ticket.ticket_code}
          </Typography>
        </Box>
        <Typography variant="h5" color="textSecondary" gutterBottom>
          {ticket.title}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Chip 
            label={ticket.status} 
            color={getStatusColor(ticket.status) as any}
            variant="filled"
          />
          <Chip 
            label={ticket.priority} 
            color={getPriorityColor(ticket.priority) as any}
            variant="outlined"
          />
          <Typography variant="body2" color="textSecondary" sx={{ ml: 2 }}>
            Progresso: {getCompletionPercentage()}%
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Informazioni Principali */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" fontWeight={600}>
                Dettagli Ticket
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {!editMode ? (
                  <Button
                    variant="contained"
                    startIcon={<EditIcon />}
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
                          title: ticket.title,
                          description: ticket.description || '',
                          status: ticket.status,
                          priority: ticket.priority,
                          note: ticket.note || ''
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
                  value={editMode ? formData.title : ticket.title}
                  onChange={(e) => editMode && setFormData({...formData, title: e.target.value})}
                  fullWidth
                  disabled={!editMode}
                  variant={editMode ? 'outlined' : 'filled'}
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  label="Descrizione"
                  value={editMode ? formData.description : ticket.description}
                  onChange={(e) => editMode && setFormData({...formData, description: e.target.value})}
                  fullWidth
                  multiline
                  rows={6}
                  disabled={!editMode}
                  variant={editMode ? 'outlined' : 'filled'}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  label="Note"
                  value={editMode ? formData.note : (ticket.note || "")}
                  onChange={(e) => editMode && setFormData({...formData, note: e.target.value})}
                  fullWidth
                  multiline
                  rows={3}
                  disabled={!editMode}
                  variant={editMode ? "outlined" : "filled"}
                  placeholder="Aggiungi note per questo ticket..."
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="Status"
                  select
                  value={editMode ? formData.status : ticket.status}
                  onChange={(e) => editMode && setFormData({...formData, status: e.target.value})}
                  fullWidth
                  disabled={!editMode}
                  variant={editMode ? 'outlined' : 'filled'}
                >
                  <MenuItem value="aperto">Aperto</MenuItem>
                  <MenuItem value="in_corso">In Corso</MenuItem>
                  <MenuItem value="chiuso">Chiuso</MenuItem>
                  <MenuItem value="annullato">Annullato</MenuItem>
                </TextField>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="Priorità"
                  select
                  value={editMode ? formData.priority : ticket.priority}
                  onChange={(e) => editMode && setFormData({...formData, priority: e.target.value})}
                  fullWidth
                  disabled={!editMode}
                  variant={editMode ? 'outlined' : 'filled'}
                >
                  <MenuItem value="bassa">Bassa</MenuItem>
                  <MenuItem value="media">Media</MenuItem>
                  <MenuItem value="alta">Alta</MenuItem>
                  <MenuItem value="critica">Critica</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </Paper>

          {/* Task List */}
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" fontWeight={600}>
                <TaskIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Task ({ticket.tasks?.length || 0})
              </Typography>
              <Box sx={{ minWidth: 200 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Progresso {getCompletionPercentage()}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={getCompletionPercentage()} 
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </Box>

            {ticket.tasks && ticket.tasks.length > 0 ? (
              <List>
                {ticket.tasks.map((task) => {
                  const isCompleted = task.status === 'completed' || task.status === 'chiuso';
                  
                  return (
                    <ListItem
                      key={task.id}
                      sx={{
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1,
                        mb: 1,
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                      onClick={() => handleTaskClick(task.id)}
                    >
                      <ListItemIcon>
                        {isCompleted ? (
                          <CheckCircleIcon sx={{ color: 'success.main' }} />
                        ) : (
                          <HourglassEmptyIcon sx={{ color: 'grey.600' }} />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography
                            sx={{
                              textDecoration: isCompleted ? 'line-through' : 'none',
                              color: isCompleted ? 'text.secondary' : 'text.primary',
                              fontWeight: 500
                            }}
                          >
                            {task.title}
                          </Typography>
                        }
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="body2" color="textSecondary" paragraph>
                              {task.description}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                              <Chip 
                                label={task.status} 
                                size="small" 
                                color={getStatusColor(task.status) as any}
                              />
                              {task.owner_name && (
                                <Chip 
                                  label={task.owner_name} 
                                  size="small" 
                                  variant="outlined"
                                />
                              )}
                              {task.due_date && (
                                <Typography variant="caption" color="textSecondary">
                                  Scadenza: {new Date(task.due_date).toLocaleDateString('it-IT')}
                                </Typography>
                              )}
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                  );
                })}
              </List>
            ) : (
              <Alert severity="info">
                Nessun task configurato per questo ticket
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Statistiche Task */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Statistiche Task
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary.main">
                    {ticket.tasks_stats?.total || 0}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Totali
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {ticket.tasks_stats?.completed || 0}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Completati
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    {ticket.tasks_stats?.pending || 0}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    In Attesa
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Account Manager */}
          {ticket.account_manager_name && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                <PersonIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Account Manager
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                {ticket.account_manager_name}
              </Typography>
              {ticket.account_manager_id && (
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  ID: {ticket.account_manager_id}
                </Typography>
              )}
            </Paper>
          )}

          {/* Cliente */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              <BusinessIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Cliente
            </Typography>
            <Typography variant="body2">
              {ticket.customer_name || 'Non specificato'}
            </Typography>
          </Paper>

          {/* Owner */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              <PersonIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Responsabile
            </Typography>
            <Typography variant="body2">
              {ticket.owner || 'Non assegnato'}
            </Typography>
          </Paper>

          {/* Date */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              <CalendarIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Date
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2">
                <strong>Creato:</strong> {new Date(ticket.created_at).toLocaleDateString('it-IT')}
              </Typography>
              {ticket.due_date && (
                <Typography variant="body2">
                  <strong>Scadenza:</strong> {new Date(ticket.due_date).toLocaleDateString('it-IT')}
                </Typography>
              )}
            </Box>
          </Paper>

          {/* Azioni Rapide */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Azioni Rapide
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => navigate(`/ticket-commerciali`)}
              >
                Torna alla Lista
              </Button>
              
              {ticket.company_id && (
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => navigate(`/aziende/${ticket.company_id}`)}
                >
                  Visualizza Azienda
                </Button>
              )}
              
              <Button
                variant="outlined"
                size="small"
                color="error"
                onClick={() => {
                  if (window.confirm('Sei sicuro di voler chiudere questo ticket?')) {
                    console.log('Chiusura ticket:', ticket.id);
                  }
                }}
                disabled={ticket.status === 'chiuso'}
              >
                Chiudi Ticket
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default TicketDetailPage;
