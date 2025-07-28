// frontend/src/components/tickets/CommercialTicketForm.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import {
  Box,
  Paper,
  Typography,
  Autocomplete,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import { Send as SendIcon, Business as BusinessIcon } from '@mui/icons-material';

interface Company {
  id: number;
  name: string;
  partita_iva?: string;
  settore?: string;
}

interface KitCommerciale {
  id: number;
  nome: string;
  descrizione?: string;
  articoli?: any[];
}

interface CommercialTicketFormProps {
  onSuccess?: (result: any) => void;
  onError?: (error: string) => void;
}

const CommercialTicketForm: React.FC<CommercialTicketFormProps> = ({ 
  onSuccess, 
  onError 
}) => {
  // State
  const [companies, setCompanies] = useState<Company[]>([]);
  const [kits, setKits] = useState<KitCommerciale[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [selectedKit, setSelectedKit] = useState<number | ''>('');
  const [notes, setNotes] = useState('');
  const { user } = useAuth();
  const [companySearch, setCompanySearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [companiesLoading, setCompaniesLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load companies with search
  useEffect(() => {
    const loadCompanies = async () => {
      if (companySearch.length < 2) {
        setCompanies([]);
        return;
      }

      setCompaniesLoading(true);
      try {
        // API call per cercare aziende
        const response = await fetch(`/api/v1/companies/search?q=${encodeURIComponent(companySearch)}`);
        if (response.ok) {
          const data = await response.json();
          setCompanies(data.companies || []);
        }
      } catch (err) {
        console.error('Errore caricamento aziende:', err);
      } finally {
        setCompaniesLoading(false);
      }
    };

    const timeoutId = setTimeout(loadCompanies, 300); // Debounce
    return () => clearTimeout(timeoutId);
  }, [companySearch]);

  // Load kit commerciali
  useEffect(() => {
    const loadKits = async () => {
      try {
        const response = await fetch('/api/v1/kit-commerciali/?attivo=true');
        if (response.ok) {
          const data = await response.json();
          setKits(data.kit_commerciali || []);
        }
      } catch (err) {
        console.error('Errore caricamento kit:', err);
      }
    };

    loadKits();
  }, []);

  // Submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedCompany || !selectedKit) {
      setError('Seleziona azienda e kit commerciale');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/tickets/commercial/create-commessa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          company_id: selectedCompany.id,
          kit_commerciale_id: selectedKit,
          notes: notes.trim(),
          owner_id: user?.id || 'default-user'
        })
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess(`Commessa ${result.commessa_code} creata con successo!`);
        
        // Reset form
        setSelectedCompany(null);
        setSelectedKit('');
        setNotes('');
        setCompanySearch('');
        
        if (onSuccess) {
          onSuccess(result);
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Errore creazione commessa');
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Errore durante la creazione';
      setError(errorMessage);
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, display: 'flex', alignItems: 'center' }}>
          <BusinessIcon sx={{ mr: 1, color: 'primary.main' }} />
          Crea Ticket Commerciale
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Seleziona un'azienda e un kit commerciale per creare una nuova commessa
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Autocomplete Aziende */}
          <Autocomplete
            value={selectedCompany}
            onChange={(_, newValue) => setSelectedCompany(newValue)}
            inputValue={companySearch}
            onInputChange={(_, newValue) => setCompanySearch(newValue)}
            options={companies}
            getOptionLabel={(option) => option.name}
            loading={companiesLoading}
            filterOptions={(x) => x} // Disabilita filtro locale, usiamo quello server
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
                  {option.settore && (
                    <Chip 
                      label={option.settore} 
                      size="small" 
                      sx={{ ml: 1, height: 16 }}
                    />
                  )}
                </Box>
              </Box>
            )}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Azienda"
                placeholder="Digita per cercare un'azienda..."
                required
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {companiesLoading && <CircularProgress color="inherit" size={20} />}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                }}
                helperText="Digita almeno 2 caratteri per cercare"
              />
            )}
          />

          {/* Select Kit Commerciale */}
          <FormControl fullWidth required>
            <InputLabel>Kit Commerciale</InputLabel>
            <Select
              value={selectedKit}
              onChange={(e) => setSelectedKit(e.target.value)}
              label="Kit Commerciale"
            >
              {kits.map((kit) => (
                <MenuItem key={kit.id} value={kit.id}>
                  <Box>
                    <Typography variant="body2" fontWeight={500}>
                      {kit.nome}
                    </Typography>
                    {kit.descrizione && (
                      <Typography variant="caption" color="textSecondary" display="block">
                        {kit.descrizione}
                      </Typography>
                    )}
                    <Chip 
                      label={`${kit.articoli?.length || 0} articoli`} 
                      size="small" 
                      sx={{ mt: 0.5 }}
                    />
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Note */}
          <TextField
            label="Note aggiuntive"
            multiline
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Aggiungi note o dettagli specifici per questa commessa..."
            helperText="Informazioni aggiuntive che verranno incluse nella descrizione della commessa"
          />

          {/* Submit Button */}
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={loading || !selectedCompany || !selectedKit}
            startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
            sx={{ alignSelf: 'flex-start', minWidth: 200 }}
          >
            {loading ? 'Creazione in corso...' : 'Crea Commessa'}
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default CommercialTicketForm;
