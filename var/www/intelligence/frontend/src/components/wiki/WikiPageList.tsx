// components/wiki/WikiPageList.tsx
// Component for displaying list of wiki pages

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  IconButton,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Tooltip,
  Avatar,
  Divider
} from '@mui/material';
import {
  Article as ArticleIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  CalendarToday as DateIcon,
  Person as AuthorIcon
} from '@mui/icons-material';

import { wikiService, WikiPage, WikiCategory } from '../../services/wikiService';

interface WikiPageListProps {
  categories: WikiCategory[];
  onPageSelect?: (page: WikiPage) => void;
  onPageEdit?: (page: WikiPage) => void;
  onPageDelete?: (page: WikiPage) => void;
}

export const WikiPageList: React.FC<WikiPageListProps> = ({
  categories,
  onPageSelect,
  onPageEdit,
  onPageDelete
}) => {
  const [pages, setPages] = useState<WikiPage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  
  // Pagination
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const navigate = useNavigate();

  const loadPages = async (reset: boolean = false) => {
    setLoading(true);
    setError(null);

    try {
      const offset = reset ? 0 : pages.length;
      const response = await wikiService.getPages({
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
        limit: 10,
        offset
      });

      if (response.success && response.data) {
        if (reset) {
          setPages(response.data);
        } else {
          setPages(prev => [...prev, ...response.data!]);
        }
        setHasMore(response.data.length === 10);
      } else {
        setError('Errore nel caricamento delle pagine');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore nel caricamento');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPages(true);
  }, [statusFilter, categoryFilter]);

  const handleSearch = () => {
    // Implement search functionality
    if (searchQuery.trim()) {
      // This would typically call a search endpoint
      console.log('Search for:', searchQuery);
    }
  };

  const handleRefresh = () => {
    loadPages(true);
  };

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      loadPages(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'success';
      case 'draft': return 'warning';
      case 'review': return 'info';
      case 'archived': return 'default';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'published': return 'Pubblicata';
      case 'draft': return 'Bozza';
      case 'review': return 'In Revisione';
      case 'archived': return 'Archiviata';
      default: return status;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateText = (text: string, maxLength: number = 150) => {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
  };

  return (
    <Box>
      {/* Header with Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <ArticleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Pagine Wiki ({pages.length})
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            {/* Search */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="Cerca pagine..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <IconButton onClick={handleSearch} size="small">
                      <SearchIcon />
                    </IconButton>
                  )
                }}
              />
            </Grid>

            {/* Status Filter */}
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">Tutti</MenuItem>
                  <MenuItem value="published">Pubblicata</MenuItem>
                  <MenuItem value="draft">Bozza</MenuItem>
                  <MenuItem value="review">In Revisione</MenuItem>
                  <MenuItem value="archived">Archiviata</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Category Filter */}
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Categoria</InputLabel>
                <Select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  label="Categoria"
                >
                  <MenuItem value="">Tutte</MenuItem>
                  {categories.map((cat) => (
                    <MenuItem key={cat.id} value={cat.slug}>
                      {cat.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Refresh Button */}
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={handleRefresh}
                disabled={loading}
                startIcon={<FilterIcon />}
              >
                Aggiorna
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Pages List */}
      <Grid container spacing={2}>
        {pages.map((page) => (
          <Grid item xs={12} key={page.id}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  boxShadow: 4,
                  transform: 'translateY(-2px)'
                }
              }}
              onClick={() => navigate(`/wiki/pages/${page.slug}`)}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  {/* Page Info */}
                  <Box sx={{ flex: 1, pr: 2 }}>
                    {/* Title and Status */}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Typography variant="h6" component="h3" sx={{ mr: 2 }}>
                        {page.title}
                      </Typography>
                      <Chip
                        label={getStatusLabel(page.status)}
                        color={getStatusColor(page.status) as any}
                        size="small"
                      />
                    </Box>

                    {/* Excerpt */}
                    {page.excerpt && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {truncateText(page.excerpt)}
                      </Typography>
                    )}

                    {/* Metadata Row */}
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
                      {/* Category */}
                      {page.category && (
                        <Chip
                          label={page.category}
                          variant="outlined"
                          size="small"
                          sx={{ textTransform: 'capitalize' }}
                        />
                      )}

                      {/* Tags */}
                      {page.tags && page.tags.length > 0 && (
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          {page.tags.slice(0, 3).map((tag) => (
                            <Chip
                              key={tag}
                              label={tag}
                              size="small"
                              variant="outlined"
                              color="primary"
                            />
                          ))}
                          {page.tags.length > 3 && (
                            <Chip
                              label={`+${page.tags.length - 3}`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      )}

                      {/* View Count */}
                      <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
                        <ViewIcon sx={{ fontSize: 16, mr: 0.5 }} />
                        <Typography variant="caption">
                          {page.view_count} visualizzazioni
                        </Typography>
                      </Box>

                      {/* Date */}
                      <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
                        <DateIcon sx={{ fontSize: 16, mr: 0.5 }} />
                        <Typography variant="caption">
                          {formatDate(page.updated_at)}
                        </Typography>
                      </Box>

                      {/* Author */}
                      {page.author_id && (
                        <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
                          <AuthorIcon sx={{ fontSize: 16, mr: 0.5 }} />
                          <Typography variant="caption">
                            {page.author_id}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </Box>

                  {/* Action Buttons */}
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Tooltip title="Modifica">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          onPageEdit?.(page);
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    
                    <Tooltip title="Elimina">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={(e) => {
                          e.stopPropagation();
                          onPageDelete?.(page);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Loading State */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Load More Button */}
      {!loading && hasMore && pages.length > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Button
            variant="outlined"
            onClick={handleLoadMore}
            disabled={loading}
          >
            Carica altre pagine
          </Button>
        </Box>
      )}

      {/* Empty State */}
      {!loading && pages.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <ArticleIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Nessuna pagina trovata
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Inizia caricando il tuo primo documento nella wiki!
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default WikiPageList;
