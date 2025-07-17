import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  Trash2, 
  Search, 
  AlertCircle,
  CheckCircle,
  Loader,
  Database,
  Globe
} from 'lucide-react';
import WebScraping from './WebScraping';

interface Document {
  filename: string;
  size: number;
  modified: string;
  format: string;
}

interface Stats {
  vector_database: {
    total_points: number;
    status: string;
    collection_name: string;
  };
  supported_formats: string[];
  upload_directory: string;
  status: string;
}

const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [stats, setStats] = useState<Stats | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("documents");

  // Carica documenti e stats all'avvio
  useEffect(() => {
    loadDocuments();
    loadStats();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/rag/documents');
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Errore caricamento documenti:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/v1/rag/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Errore caricamento stats:', error);
    }
  };

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_id', '1');
    formData.append('description', `Uploaded: ${file.name}`);

    try {
      const response = await fetch('/api/v1/rag/upload', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.success) {
        await loadDocuments();
        await loadStats();
        alert('✅ Documento caricato con successo!');
      } else {
        alert('❌ Errore durante il caricamento');
      }
    } catch (error) {
      console.error('Errore upload:', error);
      alert('❌ Errore durante il caricamento');
    } finally {
      setUploading(false);
    }
  };
  
  const handleDelete = async (filename: string) => {
    if (!confirm(`Sei sicuro di voler eliminare ${filename}?`)) return;
    
    try {
      const response = await fetch(`/api/v1/rag/documents/${filename}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await loadDocuments();
        await loadStats();
        alert('✅ Documento eliminato con successo!');
      } else {
        alert('❌ Errore durante l\'eliminazione');
      }
    } catch (error) {
      console.error('Errore eliminazione:', error);
      alert('❌ Errore durante l\'eliminazione');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setSearchLoading(true);
    try {
      const response = await fetch('/api/v1/rag/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          limit: 5,
        }),
      });
      
      const results = await response.json();
      console.log('Risultati ricerca:', results);
      // Qui potresti gestire la visualizzazione dei risultati
      alert(`Trovati ${results.results?.length || 0} risultati`);
    } catch (error) {
      console.error('Errore ricerca:', error);
      alert('❌ Errore durante la ricerca');
    } finally {
      setSearchLoading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const renderDocumentsTab = () => (
    <>
      {/* Stats Panel */}
      {stats && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Database className="mr-2 h-5 w-5" />
            Statistiche Sistema
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {stats.vector_database.total_points}
              </div>
              <div className="text-sm text-gray-500">Punti nel Database Vettoriale</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {stats.supported_formats.length}
              </div>
              <div className="text-sm text-gray-500">Formati Supportati</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${stats.status === 'operational' ? 'text-green-600' : 'text-red-600'}`}>
                {stats.status === 'operational' ? '✅' : '❌'}
              </div>
              <div className="text-sm text-gray-500">Stato Sistema</div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Area */}
      <div 
        className={`bg-white rounded-lg shadow-sm border-2 border-dashed p-8 mb-6 text-center transition-colors ${
          dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Carica un nuovo documento
        </h3>
        <p className="text-gray-500 mb-4">
          Trascina un file qui o clicca per selezionarlo
        </p>
        <input
          type="file"
          onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
          className="hidden"
          id="file-upload"
          accept=".pdf,.txt,.docx,.md"
        />
        <label
          htmlFor="file-upload"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
        >
          <Upload className="mr-2 h-4 w-4" />
          {uploading ? 'Caricamento...' : 'Seleziona File'}
        </label>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🔍 Cerca nei Documenti
        </h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Inserisci la tua query di ricerca..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={handleSearch}
            disabled={!searchQuery.trim() || searchLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            {searchLoading ? <Loader className="animate-spin h-4 w-4" /> : <Search className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            📄 Documenti ({documents.length})
          </h3>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">
            <Loader className="animate-spin h-8 w-8 mx-auto mb-4 text-blue-600" />
            <p className="text-gray-500">Caricamento documenti...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-8 text-center">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500">Nessun documento caricato</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {documents.map((doc, index) => (
              <div key={index} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-8 w-8 text-blue-600" />
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">
                        {doc.filename}
                      </h4>
                      <p className="text-sm text-gray-500">
                        {Math.round(doc.size / 1024)} KB • {doc.format} • {doc.modified}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(doc.filename)}
                    className="text-red-600 hover:text-red-800 p-2"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          📁 Gestione Documenti RAG
        </h1>
        <p className="text-gray-600">
          Carica, gestisci e cerca nei tuoi documenti aziendali
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <div className="flex space-x-8">
          <button
            onClick={() => setActiveTab("documents")}
            className={`flex items-center px-1 py-4 border-b-2 font-medium text-sm ${
              activeTab === "documents"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <FileText className="mr-2 h-4 w-4" />
            Documenti
          </button>
          <button
            onClick={() => setActiveTab("scraping")}
            className={`flex items-center px-1 py-4 border-b-2 font-medium text-sm ${
              activeTab === "scraping"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <Globe className="mr-2 h-4 w-4" />
            Web Scraping
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === "scraping" ? (
        <WebScraping />
      ) : (
        renderDocumentsTab()
      )}
    </div>
  );
};

export default DocumentManager;
