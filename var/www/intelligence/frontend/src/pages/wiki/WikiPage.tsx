// pages/wiki/WikiPage.tsx
// Main Wiki page component

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Breadcrumbs,
  Link
} from '@mui/material';
import {
  MenuBook as WikiIcon,
  CloudUpload as UploadIcon,
  List as ListIcon,
  BarChart as StatsIcon,
  Chat as ChatIcon,
  Home as HomeIcon
} from '@mui/icons-material';

import WikiUploader from '../../components/wiki/WikiUploader';
import WikiPageList from '../../components/wiki/WikiPageList';
import { wikiService, WikiCategory, WikiPage, WikiStats, WikiUploadResult } from '../../services/wikiService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`wiki-tabpanel-${index}`}
      aria-labelledby={`wiki-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

export const WikiPage: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [categories, setCategories] = useState<WikiCategory[]>([]);
  const [stats, setStats] = useState<WikiStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load categories and stats in parallel
      const [categoriesResponse, statsResponse] = await Promise.all([
        wikiService.getCategories(),
        wikiService.getStats()
      ]);

      if (categoriesResponse.success && categoriesResponse.data) {
        setCategories(categoriesResponse.data);
      }

      if (statsResponse.success && statsResponse.data) {
        setStats(statsResponse.data);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore nel caricamento dei dati');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleUploadSuccess = (result: WikiUploadResult) => {
    // Refresh stats after successful upload
    loadInitialData();
    
    // Switch to pages list if a page was created
    if (result.wiki_page_id) {
      setCurrentTab(1); // Switch to "Pagine" tab
    }

    // Show success message
    console.log('Upload successful:', result);
  };

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error);
  };

  const handlePageSelect = (page: WikiPage) => {
    // Navigate to page view (implement navigation)
    console.log('Selected page:', page);
  };

  const handlePageEdit = (page: WikiPage) => {
    // Navigate to page editor (implement navigation)
    console.log('Edit page:', page);
  };

  const handlePageDelete = async (page: WikiPage) => {
    if (window.confirm(`Sei sicuro di voler eliminare la pagina "${page.title}"?`)) {
      try {
        const response = await wikiService.deletePage(page.id);
        if (response.success) {
          // Refresh the data
          loadInitialData();
        }
      } catch (err) {
        console.error('Delete error:', err);
      }
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link underline="hover" color="inherit" href="/">
          <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Dashboard
        </Link>
        <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
          <WikiIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Wiki
        </Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <WikiIcon sx={{ mr: 2, fontSize: 40 }} />
          Intelligence Wiki
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Gestisci la conoscenza aziendale attraverso documenti intelligenti e ricerca semantica
        </Typography>
      </Box>

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="overline">
                  Pagine Totali
                </Typography>
                <Typography variant="h4" component="div">
                  {stats.total_pages}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="overline">
                  Pagine Pubblicate
                </Typography>
                <Typography variant="h4" component="div" color="success.main">
                  {stats.published_pages}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="overline">
                  Categorie
                </Typography>
                <Typography variant="h4" component="div">
                  {stats.total_categories}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="overline">
                  Visualizzazioni
                </Typography>
                <Typography variant="h4" component="div">
                  {stats.total_views}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Main Content */}
      <Paper sx={{ width: '100%' }}>
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={currentTab} 
            onChange={handleTabChange} 
            aria-label="wiki tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab 
              icon={<UploadIcon />} 
              label="Carica Documento" 
              id="wiki-tab-0"
              aria-controls="wiki-tabpanel-0"
            />
            <Tab 
              icon={<ListIcon />} 
              label={`Pagine (${stats?.total_pages || 0})`}
              id="wiki-tab-1"
              aria-controls="wiki-tabpanel-1"
            />
            <Tab 
              icon={<StatsIcon />} 
              label="Statistiche" 
              id="wiki-tab-2"
              aria-controls="wiki-tabpanel-2"
            />
            <Tab 
              icon={<ChatIcon />} 
              label="Chat (Coming Soon)" 
              id="wiki-tab-3"
              aria-controls="wiki-tabpanel-3"
              disabled
            />
          </Tabs>
        </Box>

        {/* Tab Panels */}
        <TabPanel value={currentTab} index={0}>
          <WikiUploader
            categories={categories}
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <WikiPageList
            categories={categories}
            onPageSelect={handlePageSelect}
            onPageEdit={handlePageEdit}
            onPageDelete={handlePageDelete}
          />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <Grid container spacing={3}>
            {/* Detailed Stats */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Distribuzione Pagine
                  </Typography>
                  {stats && (
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Pubblicate</Typography>
                        <Typography variant="body2">{stats.published_pages}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Bozze</Typography>
                        <Typography variant="body2">{stats.draft_pages}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Totale Visualizzazioni</Typography>
                        <Typography variant="body2">{stats.total_views}</Typography>
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Categories List */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Categorie ({categories.length})
                  </Typography>
                  <Box>
                    {categories.map((category) => (
                      <Box key={category.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">{category.name}</Typography>
                        <Typography variant="body2">{category.page_count} pagine</Typography>
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Quick Actions */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Azioni Rapide
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item>
                      <Button
                        variant="outlined"
                        startIcon={<UploadIcon />}
                        onClick={() => setCurrentTab(0)}
                      >
                        Carica Nuovo Documento
                      </Button>
                    </Grid>
                    <Grid item>
                      <Button
                        variant="outlined"
                        startIcon={<ListIcon />}
                        onClick={() => setCurrentTab(1)}
                      >
                        Visualizza Tutte le Pagine
                      </Button>
                    </Grid>
                    <Grid item>
                      <Button
                        variant="outlined"
                        startIcon={<StatsIcon />}
                        onClick={() => loadInitialData()}
                      >
                        Aggiorna Statistiche
                      </Button>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <ChatIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Chat Interface
              </Typography>
              <Typography variant="body2" color="text.secondary">
                La funzionalità di chat con contenuti wiki sarà disponibile presto!
              </Typography>
            </CardContent>
          </Card>
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default WikiPage;
