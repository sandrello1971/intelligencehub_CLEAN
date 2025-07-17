import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  Avatar,
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
  Snackbar,
  Fab,
  Tooltip,
  AppBar,
  Toolbar,
  Container,
  Stack,
  Divider,
  Badge,
  LinearProgress
} from '@mui/material';

import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  AdminPanelSettings as AdminIcon,
  Security as ManagerIcon,
  Work as OperatorIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Download as ExportIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreIcon
} from '@mui/icons-material';

interface User {
  id: string;
  name: string;
  surname: string;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
  crm_id: number | null;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  const roleConfig = {
    admin: { icon: AdminIcon, color: '#e53e3e', label: 'Administrator', bgColor: '#fed7d7' },
    manager: { icon: ManagerIcon, color: '#d69e2e', label: 'Manager', bgColor: '#faf089' },
    operator: { icon: OperatorIcon, color: '#38a169', label: 'Operator', bgColor: '#c6f6d5' }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/users');
      const data = await response.json();
      setUsers(data.users || []);
    } catch (error) {
      setSnackbar({ open: true, message: 'Errore nel caricamento utenti', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.surname.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = filterRole === 'all' || user.role === filterRole;
    
    return matchesSearch && matchesRole;
  });

  const getRoleStats = () => {
    const stats = { admin: 0, manager: 0, operator: 0, total: users.length, active: 0 };
    users.forEach(user => {
      if (user.role in stats) stats[user.role as keyof typeof stats]++;
      if (user.is_active) stats.active++;
    });
    return stats;
  };

  const stats = getRoleStats();

  const getInitials = (name: string, surname: string) => {
    return `${name.charAt(0)}${surname.charAt(0)}`.toUpperCase();
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Mai';
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const UserCard: React.FC<{ user: User }> = ({ user }) => {
    const roleInfo = roleConfig[user.role as keyof typeof roleConfig];
    const RoleIcon = roleInfo?.icon || PersonIcon;

    return (
      <Card 
        elevation={2}
        sx={{ 
          height: '100%',
          transition: 'all 0.3s ease',
          '&:hover': { 
            elevation: 8,
            transform: 'translateY(-2px)',
            borderColor: 'primary.main'
          },
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
            <Avatar 
              sx={{ 
                width: 56, 
                height: 56, 
                bgcolor: roleInfo?.color,
                fontSize: '1.2rem',
                fontWeight: 'bold'
              }}
            >
              {getInitials(user.name, user.surname)}
            </Avatar>
            
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="h6" noWrap sx={{ fontWeight: 600, mb: 0.5 }}>
                {user.name} {user.surname}
              </Typography>
              
              <Typography variant="body2" color="text.secondary" noWrap sx={{ mb: 1 }}>
                {user.email}
              </Typography>
              
              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  icon={<RoleIcon />}
                  label={roleInfo?.label || user.role}
                  size="small"
                  sx={{ 
                    bgcolor: roleInfo?.bgColor,
                    color: roleInfo?.color,
                    fontWeight: 500,
                    '& .MuiChip-icon': { color: roleInfo?.color }
                  }}
                />
                
                <Chip
                  label={user.is_active ? 'Attivo' : 'Inattivo'}
                  size="small"
                  color={user.is_active ? 'success' : 'default'}
                  variant="outlined"
                />
              </Stack>
            </Box>
            
            <IconButton size="small" onClick={() => setSelectedUser(user)}>
              <MoreIcon />
            </IconButton>
          </Box>
          
          <Divider sx={{ my: 2 }} />
          
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary" display="block">
                CRM ID
              </Typography>
              <Typography variant="body2" fontWeight={500}>
                {user.crm_id || 'N/A'}
              </Typography>
            </Grid>
            
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary" display="block">
                Ultimo accesso
              </Typography>
              <Typography variant="body2" fontWeight={500}>
                {formatDate(user.last_login)}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography>Caricamento utenti...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <AppBar position="static" color="transparent" elevation={0} sx={{ mb: 3 }}>
        <Toolbar sx={{ px: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <PersonIcon />
            </Avatar>
            <Box>
              <Typography variant="h4" fontWeight={700} color="text.primary">
                Gestione Utenti
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Amministrazione sistema utenti IntelligenceHUB
              </Typography>
            </Box>
          </Box>
          
          <Stack direction="row" spacing={1}>
            <Button startIcon={<RefreshIcon />} onClick={fetchUsers} variant="outlined">
              Aggiorna
            </Button>
            <Button startIcon={<ExportIcon />} variant="outlined">
              Esporta
            </Button>
            <Button startIcon={<AddIcon />} variant="contained">
              Nuovo Utente
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight={700}>
                    {stats.total}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Utenti Totali
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                  <PersonIcon />
                </Avatar>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight={700}>
                    {stats.active}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Utenti Attivi
                  </Typography>
                </Box>
                <Badge badgeContent={stats.active} color="error">
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                    <PersonIcon />
                  </Avatar>
                </Badge>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'warning.main', color: 'white' }}>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight={700}>
                    {stats.admin}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Amministratori
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                  <AdminIcon />
                </Avatar>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'info.main', color: 'white' }}>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight={700}>
                    {stats.manager + stats.operator}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Staff
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                  <ManagerIcon />
                </Avatar>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
          <TextField
            placeholder="Cerca utenti..."
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
            sx={{ minWidth: 300 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Ruolo</InputLabel>
            <Select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              label="Ruolo"
            >
              <MenuItem value="all">Tutti</MenuItem>
              <MenuItem value="admin">Amministratori</MenuItem>
              <MenuItem value="manager">Manager</MenuItem>
              <MenuItem value="operator">Operatori</MenuItem>
            </Select>
          </FormControl>
          
          <Box sx={{ flex: 1 }} />
          
          <Typography variant="body2" color="text.secondary">
            {filteredUsers.length} di {users.length} utenti
          </Typography>
        </Stack>
      </Paper>

      {/* Users Grid */}
      <Grid container spacing={3}>
        {filteredUsers.map((user) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={user.id}>
            <UserCard user={user} />
          </Grid>
        ))}
      </Grid>

      {filteredUsers.length === 0 && (
        <Paper sx={{ p: 8, textAlign: 'center', mt: 4 }}>
          <PersonIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Nessun utente trovato
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Prova a modificare i filtri di ricerca
          </Typography>
        </Paper>
      )}

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
        onClick={() => setOpenDialog(true)}
      >
        <AddIcon />
      </Fab>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default UserManagement;
