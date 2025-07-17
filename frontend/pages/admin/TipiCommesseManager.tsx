// pages/admin/TipiCommesseManager.tsx
// Gestione Tipi Commesse - IntelligenceHUB Admin

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Alert,
  Snackbar,
  Tooltip,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  InputAdornment
} from '@mui/material';

import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  ToggleOn as ToggleOnIcon,
  ToggleOff as ToggleOffIcon,
  Code as CodeIcon,
  Schedule as ScheduleIcon,
  Business as BusinessIcon
} from '@mui/icons-material';

import { TipoCommessa, TipoCommessaFormData, LoadingState } from '../../types/admin';
import tipiCommesseService from '../../services/admin/tipiCommesseService';

interface TipiCommesseManagerState {
  tipiCommesse: TipoCommessa[];
  loading: LoadingState;
  error: string | null;
  selectedItem: TipoCommessa | null;
  isModalOpen: boolean;
  isEditing: boolean;
  formData: TipoCommessaFormData;
  successMessage: string | null;
}

const initialFormData: TipoCommessaFormData = {
  nome: '',
  codice: '',
  descrizione: '',
  sla_default_hours: 48,
  is_active: true
};

const TipiCommesseManager: React.FC = () => {
  const [state, setState] = useState<TipiCommesseManagerState>({
    tipiCommesse: [],
    loading: LoadingState.IDLE,
    error: null,
    selectedItem: null,
    isModalOpen: false,
    isEditing: false,
    formData: { ...initialFormData },
    successMessage: null
  });

  // Carica dati iniziali
  const loadTipiCommesse = useCallback(async () => {
    setState(prev => ({ ...prev, loading: LoadingState.LOADING, error: null }));
    
    try {
      const response = await tipiCommesseService.getAll();
      
      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          tipiCommesse: response.data!,
          loading: LoadingState.SUCCESS
        }));
      } else {
        setState(prev => ({
          ...prev,
          loading: LoadingState.ERROR,
          error: response.error || 'Errore caricamento dati'
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: LoadingState.ERROR,
        error: 'Errore di connessione'
      }));
    }
  }, []);

  useEffect(() => {
    loadTipiCommesse();
  }, [loadTipiCommesse]);

  // Handlers
  const handleOpenModal = (item?: TipoCommessa) => {
    if (item) {
      setState(prev => ({
        ...prev,
        selectedItem: item,
        isEditing: true,
        isModalOpen: true,
        formData: {
          nome: item.nome,
          codice: item.codice,
          descrizione: item.descrizione || '',
          sla_default_hours: item.sla_default_hours,
          is_active: item.is_active
        }
      }));
    } else {
      setState(prev => ({
        ...prev,
        selectedItem: null,
        isEditing: false,
        isModalOpen: true,
        formData: { ...initialFormData }
      }));
    }
  };

  const handleCloseModal = () => {
    setState(prev => ({
      ...prev,
      isModalOpen: false,
      selectedItem: null,
      formData: { ...initialFormData },
      error: null
    }));
  };

  const handleFormChange = (field: keyof TipoCommessaFormData, value: any) => {
    setState(prev => ({
      ...prev,
      formData: {
        ...prev.formData,
        [field]: value
      }
    }));
  };

  const handleSubmit = async () => {
    setState(prev => ({ ...prev, loading: LoadingState.LOADING, error: null }));

    try {
      let response;

      if (state.isEditing && state.selectedItem) {
        response = await tipiCommesseService.update(state.selectedItem.id, state.formData);
      } else {
        response = await tipiCommesseService.create(state.formData);
      }

      if (response.success) {
        setState(prev => ({
          ...prev,
          loading: LoadingState.SUCCESS,
          successMessage: state.isEditing 
            ? 'Tipo commessa aggiornato con successo!' 
            : 'Tipo commessa creato con successo!'
        }));
        
        handleCloseModal();
        await loadTipiCommesse();
      } else {
        setState(prev => ({
          ...prev,
          loading: LoadingState.ERROR,
          error: response.error || 'Errore durante il salvataggio'
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: LoadingState.ERROR,
        error: 'Errore di connessione'
      }));
    }
  };

  const handleDelete = async (item: TipoCommessa) => {
    if (!window.confirm(`Sei sicuro di voler eliminare "${item.nome}"?`)) {
      return;
    }

    setState(prev => ({ ...prev, loading: LoadingState.LOADING }));

    try {
      const response = await tipiCommesseService.delete(item.id);

      if (response.success) {
        setState(prev => ({
          ...prev,
          loading: LoadingState.SUCCESS,
          successMessage: 'Tipo commessa eliminato con successo!'
        }));
        
        await loadTipiCommesse();
      } else {
        setState(prev => ({
          ...prev,
          loading: LoadingState.ERROR,
          error: response.error || 'Errore durante l\'eliminazione'
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: LoadingState.ERROR,
        error: 'Errore di connessione'
      }));
    }
  };

  const handleToggleActive = async (item: TipoCommessa) => {
    try {
      const response = await tipiCommesseService.toggleActive(item.id, !item.is_active);

      if (response.success) {
        setState(prev => ({
          ...prev,
          successMessage: `Tipo commessa ${!item.is_active ? 'attivato' : 'disattivato'} con successo!`
        }));
        
        await loadTipiCommesse();
      } else {
        setState(prev => ({
          ...prev,
          error: response.error || 'Errore durante l\'aggiornamento'
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Errore di connessione'
      }));
    }
  };

  const handleCloseSnackbar = () => {
    setState(prev => ({
      ...prev,
      error: null,
      successMessage: null
    }));
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BusinessIcon fontSize="large" color="primary" />
          Gestione Tipi Commesse
        </Typography>
        
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenModal()}
          disabled={state.loading === LoadingState.LOADING}
        >
          Nuovo Tipo Commessa
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Totale Tipi Commesse
              </Typography>
              <Typography variant="h5" component="div">
                {state.tipiCommesse.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Tipi Attivi
              </Typography>
              <Typography variant="h5" component="div" color="success.main">
                {state.tipiCommesse.filter(t => t.is_active).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Loading */}
      {state.loading === LoadingState.LOADING && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Tabella */}
      {state.loading !== LoadingState.LOADING && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nome</TableCell>
                <TableCell>Codice</TableCell>
                <TableCell>Descrizione</TableCell>
                <TableCell align="center">SLA Default (ore)</TableCell>
                <TableCell align="center">Stato</TableCell>
                <TableCell align="center">Azioni</TableCell>
              </TableRow>
            </TableHead>
            
            <TableBody>
              {state.tipiCommesse.map((item) => (
                <TableRow key={item.id} hover>
                  <TableCell>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {item.nome}
                    </Typography>
                  </TableCell>
                  
                  <TableCell>
                    <Chip 
                      icon={<CodeIcon />}
                      label={item.codice}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  
                  <TableCell>
                    <Typography variant="body2" color="textSecondary">
                      {item.descrizione || '-'}
                    </Typography>
                  </TableCell>
                  
                  <TableCell align="center">
                    <Chip 
                      icon={<ScheduleIcon />}
                      label={`${item.sla_default_hours}h`}
                      size="small"
                      color="info"
                    />
                  </TableCell>
                  
                  <TableCell align="center">
                    <Chip
                      label={item.is_active ? 'Attivo' : 'Inattivo'}
                      color={item.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                      <Tooltip title="Modifica">
                        <IconButton 
                          size="small" 
                          onClick={() => handleOpenModal(item)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title={item.is_active ? 'Disattiva' : 'Attiva'}>
                        <IconButton 
                          size="small" 
                          onClick={() => handleToggleActive(item)}
                          color={item.is_active ? 'warning' : 'success'}
                        >
                          {item.is_active ? <ToggleOffIcon /> : <ToggleOnIcon />}
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Elimina">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDelete(item)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
              
              {state.tipiCommesse.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography color="textSecondary">
                      Nessun tipo commessa configurato
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Modal Form */}
      <Dialog 
        open={state.isModalOpen} 
        onClose={handleCloseModal}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {state.isEditing ? 'Modifica Tipo Commessa' : 'Nuovo Tipo Commessa'}
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              label="Nome *"
              value={state.formData.nome}
              onChange={(e) => handleFormChange('nome', e.target.value)}
              fullWidth
              placeholder="es: Incarico 24 mesi"
            />
            
            <TextField
              label="Codice *"
              value={state.formData.codice}
              onChange={(e) => handleFormChange('codice', e.target.value.toUpperCase())}
              fullWidth
              placeholder="es: I24"
              InputProps={{
                startAdornment: <InputAdornment position="start"><CodeIcon /></InputAdornment>
              }}
            />
            
            <TextField
              label="Descrizione"
              value={state.formData.descrizione}
              onChange={(e) => handleFormChange('descrizione', e.target.value)}
              fullWidth
              multiline
              rows={3}
              placeholder="Descrizione dettagliata del tipo di commessa..."
            />
            
            <TextField
              label="SLA Default (ore)"
              type="number"
              value={state.formData.sla_default_hours}
              onChange={(e) => handleFormChange('sla_default_hours', parseInt(e.target.value) || 0)}
              fullWidth
              InputProps={{
                startAdornment: <InputAdornment position="start"><ScheduleIcon /></InputAdornment>
              }}
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={state.formData.is_active}
                  onChange={(e) => handleFormChange('is_active', e.target.checked)}
                />
              }
              label="Tipo commessa attivo"
            />
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseModal}>
            Annulla
          </Button>
          <Button 
            onClick={handleSubmit}
            variant="contained"
            disabled={!state.formData.nome || !state.formData.codice || state.loading === LoadingState.LOADING}
          >
            {state.loading === LoadingState.LOADING ? (
              <CircularProgress size={20} />
            ) : (
              state.isEditing ? 'Aggiorna' : 'Crea'
            )}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notifications */}
      <Snackbar
        open={!!state.error}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert severity="error" onClose={handleCloseSnackbar}>
          {state.error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!state.successMessage}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert severity="success" onClose={handleCloseSnackbar}>
          {state.successMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default TipiCommesseManager;
