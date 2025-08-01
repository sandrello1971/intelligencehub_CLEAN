
// frontend/src/pages/dashboard/CommercialTickets.tsx
import React, { useState } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Tabs, 
  Tab,
  Paper
} from '@mui/material';
import { 
  Add as AddIcon, 
  AccountTree as TreeIcon 
} from '@mui/icons-material';
import CommercialTicketForm from '../../components/tickets/CommercialTicketForm';
import TicketHierarchyView from '../../components/tickets/TicketHierarchyView';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`commercial-tabpanel-${index}`}
      aria-labelledby={`commercial-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `commercial-tab-${index}`,
    'aria-controls': `commercial-tabpanel-${index}`,
  };
}

const CommercialTickets: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleCommessaCreated = (result: any) => {
    console.log('Commessa creata:', result);
    
    // Trigger refresh della vista albero
    setRefreshTrigger(prev => prev + 1);
    
    // Switch automatico alla tab Vista Albero per vedere il risultato
    setTimeout(() => {
      setActiveTab(1);
    }, 2000); // Dopo 2 secondi, passa alla vista albero
  };

  const handleError = (error: string) => {
    console.error('Errore:', error);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Gestione Ticket Customer Care
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Crea e gestisci ticket commerciali basati sui kit configurati
        </Typography>
      </Box>

      {/* Tabs Navigation */}
      <Paper elevation={0} sx={{ borderBottom: 1, borderColor: 'divider', mb: 0 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange} 
          aria-label="commercial tickets tabs"
          variant="fullWidth"
        >
          <Tab 
            icon={<AddIcon />} 
            label="Crea Ticket" 
            {...a11yProps(0)}
            sx={{ 
              minHeight: 72,
              '& .MuiTab-iconWrapper': { 
                mb: 0.5 
              }
            }}
          />
          <Tab 
            icon={<TreeIcon />} 
            label="Vista Albero" 
            {...a11yProps(1)}
            sx={{ 
              minHeight: 72,
              '& .MuiTab-iconWrapper': { 
                mb: 0.5 
              }
            }}
          />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <TabPanel value={activeTab} index={0}>
        <CommercialTicketForm 
          onSuccess={handleCommessaCreated}
          onError={handleError}
        />
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <TicketHierarchyView 
          refreshTrigger={refreshTrigger}
        />
      </TabPanel>
    </Container>
  );
};

export default CommercialTickets;
