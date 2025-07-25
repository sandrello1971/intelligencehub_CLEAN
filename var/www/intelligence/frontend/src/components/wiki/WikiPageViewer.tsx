// components/wiki/WikiPageViewer.tsx
// Component for viewing individual wiki pages

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Chip,
  Breadcrumbs,
  Link,
  CircularProgress,
  Alert,
  IconButton,
  Divider
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Home as HomeIcon,
  MenuBook as WikiIcon
} from '@mui/icons-material';

import { wikiService, WikiPage } from '../../services/wikiService';

export const WikiPageViewer: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [page, setPage] = useState<WikiPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (slug) {
      loadPage(slug);
    }
  }, [slug]);

  const loadPage = async (pageSlug: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await wikiService.getPageBySlug(pageSlug);
      if (response.success && response.data) {
        setPage(response.data);
      } else {
        setError('Pagina non trovata');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore nel caricamento della pagina');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/wiki');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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

  if (error || !page) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || 'Pagina non trovata'}
        </Alert>
        <Box>
          <IconButton onClick={handleBack} sx={{ mr: 2 }}>
            <BackIcon />
          </IconButton>
          Torna alla Wiki
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
        <Link underline="hover" color="inherit" onClick={handleBack} sx={{ cursor: 'pointer' }}>
          <WikiIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Wiki
        </Link>
        <Typography color="text.primary">
          {page.title}
        </Typography>
      </Breadcrumbs>

      {/* Back Button */}
      <Box sx={{ mb: 3 }}>
        <IconButton onClick={handleBack} sx={{ mr: 2 }}>
          <BackIcon />
        </IconButton>
        <Typography variant="button" onClick={handleBack} sx={{ cursor: 'pointer' }}>
          Torna alla Wiki
        </Typography>
      </Box>

      {/* Page Content */}
      <Paper sx={{ p: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Typography variant="h3" component="h1" gutterBottom>
              {page.title}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton color="primary" title="Modifica">
                <EditIcon />
              </IconButton>
            </Box>
          </Box>

          {/* Metadata */}
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center', mb: 2 }}>
            {/* Status */}
            <Chip
              label={page.status === 'published' ? 'Pubblicata' : page.status}
              color={page.status === 'published' ? 'success' : 'default'}
            />

            {/* Category */}
            {page.category && (
              <Chip
                label={page.category}
                variant="outlined"
                sx={{ textTransform: 'capitalize' }}
              />
            )}

            {/* Tags */}
            {page.tags && page.tags.map((tag) => (
              <Chip
                key={tag}
                label={tag}
                size="small"
                variant="outlined"
                color="primary"
              />
            ))}

            {/* View Count */}
            <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
              <ViewIcon sx={{ fontSize: 16, mr: 0.5 }} />
              <Typography variant="caption">
                {page.view_count} visualizzazioni
              </Typography>
            </Box>
          </Box>

          {/* Dates and Author */}
          <Typography variant="body2" color="text.secondary">
            Creata il {formatDate(page.created_at)}
            {page.updated_at !== page.created_at && (
              <> • Aggiornata il {formatDate(page.updated_at)}</>
            )}
            {page.author_id && <> • da {page.author_id}</>}
          </Typography>

          {/* Excerpt */}
          {page.excerpt && (
            <Typography variant="body1" sx={{ mt: 2, fontStyle: 'italic', color: 'text.secondary' }}>
              {page.excerpt}
            </Typography>
          )}
        </Box>

        <Divider sx={{ mb: 4 }} />

        {/* Content */}
        <Box sx={{ mb: 4 }}>
          {page.content_html ? (
            <div 
              dangerouslySetInnerHTML={{ __html: page.content_html }}
              style={{ 
                lineHeight: 1.7,
                fontSize: '16px'
              }}
            />
          ) : page.content_markdown ? (
            <Box sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
              {page.content_markdown}
            </Box>
          ) : (
            <Typography color="text.secondary">
              Nessun contenuto disponibile
            </Typography>
          )}
        </Box>

        {/* Sections */}
        {page.sections && page.sections.length > 0 && (
          <Box>
            <Typography variant="h5" gutterBottom>
              Sezioni ({page.sections.length})
            </Typography>
            {page.sections
              .sort((a, b) => a.section_order - b.section_order)
              .map((section) => (
                <Box key={section.id} sx={{ mb: 3 }}>
                  {section.section_title && (
                    <Typography 
                      variant={`h${Math.min(6, section.section_level + 3)}` as any}
                      gutterBottom
                    >
                      {section.section_title}
                    </Typography>
                  )}
                  {section.content_markdown && (
                    <Typography sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>
                      {section.content_markdown}
                    </Typography>
                  )}
                </Box>
              ))}
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default WikiPageViewer;
