// components/wiki/WikiUploader.tsx
// Component for uploading documents to Wiki

import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  LinearProgress,
  Switch,
  FormControlLabel,
  Grid,
  Paper,
  Divider
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as DocumentIcon,
  Check as CheckIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

import { wikiService, WikiCategory, WikiUploadResult } from '../../services/wikiService';

interface WikiUploaderProps {
  categories: WikiCategory[];
  onUploadSuccess?: (result: WikiUploadResult) => void;
  onUploadError?: (error: string) => void;
}

export const WikiUploader: React.FC<WikiUploaderProps> = ({
  categories,
  onUploadSuccess,
  onUploadError
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [autoPublish, setAutoPublish] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<WikiUploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (!title) {
        // Auto-generate title from filename
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
        setTitle(nameWithoutExt);
      }
      setError(null);
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleTagInputKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleAddTag();
    }
  };

  const validateForm = (): boolean => {
    if (!selectedFile) {
      setError('Seleziona un file da caricare');
      return false;
    }
    if (!title.trim()) {
      setError('Inserisci un titolo per il documento');
      return false;
    }
    
    // Check file size (max 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('Il file è troppo grande (max 10MB)');
      return false;
    }

    // Check file type
    const allowedTypes = ['.pdf', '.docx', '.txt', '.md', '.html'];
    const fileExtension = '.' + selectedFile.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      setError(`Tipo file non supportato. Formati ammessi: ${allowedTypes.join(', ')}`);
      return false;
    }

    return true;
  };

  const handleUpload = async () => {
    if (!validateForm()) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);
    setUploadResult(null);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const result = await wikiService.uploadDocument(
        selectedFile!,
        title,
        category,
        tags,
        autoPublish
      );

      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadResult(result);

      if (result.processing_status === 'success') {
        onUploadSuccess?.(result);
      } else {
        const errorMsg = result.errors.length > 0 ? result.errors.join(', ') : 'Upload failed';
        setError(errorMsg);
        onUploadError?.(errorMsg);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore durante l\'upload');
      onUploadError?.(err instanceof Error ? err.message : 'Upload error');
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadProgress(0), 2000);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setTitle('');
    setCategory('');
    setTags([]);
    setTagInput('');
    setAutoPublish(false);
    setUploadResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <UploadIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Carica Documento Wiki
        </Typography>

        <Grid container spacing={3}>
          {/* File Selection */}
          <Grid item xs={12}>
            <Paper
              sx={{
                p: 3,
                border: '2px dashed',
                borderColor: selectedFile ? 'success.main' : 'grey.300',
                backgroundColor: selectedFile ? 'success.50' : 'grey.50',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept=".pdf,.docx,.txt,.md,.html"
                style={{ display: 'none' }}
              />
              
              {selectedFile ? (
                <Box>
                  <DocumentIcon sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
                  <Typography variant="h6" color="success.main">
                    {selectedFile.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <UploadIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
                  <Typography variant="h6" color="text.secondary">
                    Clicca per selezionare un file
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Formati supportati: PDF, Word, TXT, Markdown, HTML
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Form Fields */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Titolo"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              helperText="Titolo che apparirà nella wiki"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Categoria</InputLabel>
              <Select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                label="Categoria"
              >
                <MenuItem value="">
                  <em>Nessuna categoria</em>
                </MenuItem>
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.slug}>
                    {cat.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Tags */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Aggiungi tag"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={handleTagInputKeyPress}
              helperText="Premi Enter per aggiungere un tag"

              InputProps={{
                endAdornment: (
                  <Button onClick={handleAddTag} disabled={!tagInput.trim()}>
                    Aggiungi
                  </Button>
                )
              }}
            />
            {tags.length > 0 && (
              <Box sx={{ mt: 1 }}>
                {tags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    onDelete={() => handleRemoveTag(tag)}
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>
            )}
          </Grid>

          {/* Upload Progress */}
          {isUploading && (
            <Grid item xs={12}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Upload in corso... {uploadProgress}%
                </Typography>
                <LinearProgress variant="determinate" value={uploadProgress} />
              </Box>
            </Grid>
          )}

          {/* Error Display */}
          {error && (
            <Grid item xs={12}>
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            </Grid>
          )}

          {/* Success Result */}
          {uploadResult && uploadResult.processing_status === 'success' && (
            <Grid item xs={12}>
              <Alert severity="success" sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  <CheckIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                  Documento caricato con successo!
                </Typography>
                <Typography variant="body2">
                  • Sezioni create: {uploadResult.sections_created}
                  <br />
                  • Status: {uploadResult.processing_status}
                  {uploadResult.wiki_page_id && (
                    <>
                      <br />
                      • Pagina wiki creata con ID: {uploadResult.wiki_page_id}
                    </>
                  )}
                </Typography>
              </Alert>
            </Grid>
          )}

          {/* Auto Publish Toggle */}
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={autoPublish}
                  onChange={(e) => setAutoPublish(e.target.checked)}
                  color="primary"
                />
              }
              label="Pubblica automaticamente dopo il caricamento"
            />
          </Grid>

          {/* Action Buttons */}
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                onClick={handleReset}
                disabled={isUploading}
              >
                Reset
              </Button>
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={!selectedFile || !title || isUploading}
                startIcon={<UploadIcon />}
              >
                {isUploading ? 'Caricamento...' : (autoPublish ? 'Carica e Pubblica' : 'Carica')}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default WikiUploader;
