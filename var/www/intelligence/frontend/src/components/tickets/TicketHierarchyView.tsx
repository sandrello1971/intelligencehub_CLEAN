
// frontend/src/components/tickets/TicketHierarchyView.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Autocomplete,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Card,
  CardContent,
  Grid,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Business as BusinessIcon,
  Assignment as AssignmentIcon,
  Task as TaskIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  AccountTree as TreeIcon
} from '@mui/icons-material';
import { ticketApi, Company, TicketHierarchy } from '../../services/ticketApi';

interface TicketHierarchyViewProps {
  refreshTrigger?: number; // Per aggiornare quando viene creata una nuova commessa
}

const TicketHierarchyView: React.FC<TicketHierarchyViewProps> = ({ refreshTrigger }) => {
  // State
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [companySearch, setCompanySearch] = useState('');
  const [hierarchy, setHierarchy] = useState<TicketHierarchy | null>(null);
  const [companiesLoading, setCompaniesLoading] = useState(false);
  const [hierarchyLoading, setHierarchyLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load companies with search
  useEffect(() => {
    const loadCompanies = async () => {
      if (companySearch.length < 2) {
        setCompanies([]);
        return;
      }

      setCompaniesLoading(true);
      try {
        const response = await ticketApi.searchCompanies(companySearch);
        setCompanies(response.companies || []);
      } catch (err) {
        console.error('Errore caricamento aziende:', err);
      } finally {
        setCompaniesLoading(false);
      }
    };

    const timeoutId = setTimeout(loadCompanies, 300);
    return () => clearTimeout(timeoutId);
  }, [companySearch]);

  // Load hierarchy when company changes
  useEffect(() => {
    if (selectedCompany) {
      loadHierarchy();
    } else {
      setHierarchy(null);
    }
  }, [selectedCompany, refreshTrigger]);

  const loadHierarchy = async () => {
    if (!selectedCompany) return;

    setHierarchyLoading(true);
    setError(null);

    try {
      const data = await ticketApi.getTicketHierarchy(selectedCompany.id);
      setHierarchy(data);
    } catch (err: any) {
      setError(err.message || 'Errore durante il caricamento della gerarchia');
    } finally {
      setHierarchyLoading(false);
    }
  };

  const getStatusColor = (status: number) => {
    switch (status) {
      case 0: return 'primary'; // Aperto
      case 1: return 'warning'; // In corso
      case 2: return 'success'; // Chiuso
      default: return 'default';
    }
  };

  const getStatusText = (status: number) => {
    switch (status) {
      case 0: return 'Aperto';
      case 1: return 'In corso';
      case 2: return 'Chiuso';
      default: return 'Sconosciuto';
    }
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 0: return 'success'; // Bassa
      case 1: return 'warning'; // Media
      case 2: return 'error';   // Alta
      default: return 'default';
    }
  };

  const getPriorityText = (priority: number) => {
    switch (priority) {
      case 0: return 'Bassa';
      case 1: return 'Media';
      case 2: return 'Alta';
      default: return 'Media';
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, display: 'flex', alignItems: 'center' }}>
          <TreeIcon sx={{ mr: 1, color: 'primary.main' }} />
          Vista Albero Ticket Commerciali
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Seleziona un'azienda per visualizzare la gerarchia dei ticket commerciali
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Selezione Azienda */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Autocomplete
          value={selectedCompany}
          onChange={(_, newValue) => setSelectedCompany(newValue)}
          inputValue={companySearch}
          onInputChange={(_, newValue) => setCompanySearch(newValue)}
          options={companies}
          getOptionLabel={(option) => option.name}
          loading={companiesLoading}
          filterOptions={(x) => x}
          sx={{ flexGrow: 1 }}
          renderOption={(props, option) => (
            <Box component="li" {...props}>
              <Box>
                <Typography variant="body2" fontWeight={500}>
                  {option.name}
                </Typography>
                {option.partita_iva && (
                  <Typography variant="caption" color="textSecondary">
                    P.IVA: {option.partita_iva}
                  </Typography>
                )}
              </Box>
            </Box>
          )}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Seleziona Azienda"
              placeholder="Digita per cercare..."
              InputProps={{
                ...params.InputProps,
                endAdornment: (
                  <>
                    {companiesLoading && <CircularProgress color="inherit" size={20} />}
                    {params.InputProps.endAdornment}
                  </>
                ),
              }}
            />
          )}
        />

        <Tooltip title="Aggiorna">
          <IconButton 
            onClick={loadHierarchy} 
            disabled={!selectedCompany || hierarchyLoading}
            color="primary"
          >
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Loading */}
      {hierarchyLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Gerarchia */}
      {hierarchy && !hierarchyLoading && (
        <Box>
          {/* Statistiche */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary.main">
                    {hierarchy.statistics.total_commesse}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Commesse Totali
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="secondary.main">
                    {hierarchy.statistics.total_tickets_padre}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Ticket Padre
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {hierarchy.statistics.total_tickets_figli}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Ticket Figli
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Ticket Padre */}
          {hierarchy.tickets_padre.length > 0 ? (
            <Box>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <AssignmentIcon sx={{ mr: 1 }} />
                Ticket Commerciali Padre ({hierarchy.tickets_padre.length})
              </Typography>

              {hierarchy.tickets_padre.map((ticket, index) => (
                <Accordion key={ticket.id} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                      <Typography variant="subtitle1" fontWeight={500}>
                        {ticket.ticket_code} - {ticket.title}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, ml: 'auto' }}>
                        <Chip 
                          label={getStatusText(ticket.status)} 
                          color={getStatusColor(ticket.status)}
                          size="small"
                        />
                        <Chip 
                          label={getPriorityText(ticket.priority)} 
                          color={getPriorityColor(ticket.priority)}
                          size="small"
                        />
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Descrizione:
                        </Typography>
                        <Typography variant="body2" paragraph>
                          {ticket.description || 'Nessuna descrizione'}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Dettagli:
                        </Typography>
                        <Typography variant="body2">
                          <strong>Owner:</strong> {ticket.owner || 'Non assegnato'}<br />
                          <strong>Cliente:</strong> {ticket.customer_name || 'N/A'}<br />
                          <strong>Creato:</strong> {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : 'N/A'}
                        </Typography>
                      </Grid>
                      {ticket.tasks && ticket.tasks.length > 0 && (
                        <Grid item xs={12}>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Task ({ticket.tasks.length}):
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {ticket.tasks.map((task: any) => (
                              <Chip 
                                key={task.id}
                                icon={<TaskIcon />}
                                label={`${task.title} (${task.status})`}
                                variant="outlined"
                                size="small"
                              />
                            ))}
                          </Box>
                        </Grid>
                      )}
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          ) : (
            <Alert severity="info">
              Nessun ticket commerciale trovato per questa azienda.
            </Alert>
          )}

          {/* Ticket Figli */}
          {hierarchy.tickets_figli.length > 0 && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <TaskIcon sx={{ mr: 1 }} />
                Ticket Servizi Specifici ({hierarchy.tickets_figli.length})
              </Typography>

              {hierarchy.tickets_figli.map((ticket, index) => (
                <Card key={ticket.id} variant="outlined" sx={{ mb: 1 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle2" fontWeight={500}>
                        {ticket.ticket_code} - {ticket.title}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip 
                          label={getStatusText(ticket.status)} 
                          color={getStatusColor(ticket.status)}
                          size="small"
                        />
                      </Box>
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      {ticket.description || 'Nessuna descrizione'}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </Box>
      )}

      {/* Empty State */}
      {!selectedCompany && !hierarchyLoading && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <BusinessIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary" gutterBottom>
            Seleziona un'azienda
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Cerca e seleziona un'azienda per visualizzare i suoi ticket commerciali
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default TicketHierarchyView;
