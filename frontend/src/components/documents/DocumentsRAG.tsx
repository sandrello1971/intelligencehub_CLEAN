import React, { useState, useEffect } from 'react';

interface Document {
  filename: string;
  size: number;
  modified: string;
  format: string;
}

interface DocumentsResponse {
  documents: Document[];
  total: number;
  upload_directory: string;
  timestamp: string;
}

const DocumentsRAG: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [stats, setStats] = useState({ total: 0, upload_directory: '', timestamp: '' });

  // Carica documenti dal backend
  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/rag/documents');
      if (response.ok) {
        const data: DocumentsResponse = await response.json();
        setDocuments(data.documents || []);
        setStats({
          total: data.total,
          upload_directory: data.upload_directory,
          timestamp: data.timestamp
        });
      } else {
        console.error('Errore caricamento documenti:', response.status);
      }
    } catch (error) {
      console.error('Errore connessione:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (format: string) => {
    switch (format.toLowerCase()) {
      case '.pdf': return '📄';
      case '.docx': case '.doc': return '📝';
      case '.xlsx': case '.xls': return '📊';
      case '.txt': return '📋';
      case '.md': return '📖';
      default: return '📁';
    }
  };

  const getCleanFilename = (filename: string) => {
    // Rimuove timestamp e UUID dal nome file
    const parts = filename.split('_');
    if (parts.length >= 3) {
      return parts.slice(2).join('_'); // Rimuove data e UUID
    }
    return filename;
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    
    for (const file of Array.from(files)) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/api/v1/rag/upload', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          console.log(`File ${file.name} caricato con successo`);
        } else {
          console.error(`Errore caricamento ${file.name}:`, response.status);
        }
      } catch (error) {
        console.error(`Errore caricamento ${file.name}:`, error);
      }
    }

    setUploading(false);
    loadDocuments(); // Ricarica lista documenti
  };

  const deleteDocument = async (filename: string) => {
    if (!window.confirm(`Sei sicuro di voler eliminare il documento "${getCleanFilename(filename)}"?`)) return;
    
    try {
      const response = await fetch(`/api/v1/rag/documents/${encodeURIComponent(filename)}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        console.log('Documento eliminato:', filename);
        loadDocuments(); // Ricarica lista
      } else {
        console.error('Errore eliminazione:', response.status);
        alert('Errore durante l\'eliminazione del documento');
      }
    } catch (error) {
      console.error('Errore eliminazione:', error);
      alert('Errore di connessione durante l\'eliminazione');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('it-IT');
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <svg className="w-8 h-8 mr-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Documenti RAG
        </h1>
        <p className="text-gray-600">Gestione documenti per Retrieval Augmented Generation - Knowledge Base intelligente</p>
        {stats.timestamp && (
          <p className="text-sm text-gray-500 mt-1">
            Ultimo aggiornamento: {formatDate(stats.timestamp)} • Directory: {stats.upload_directory}
          </p>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-lg text-white">
          <div className="text-2xl font-bold">{stats.total}</div>
          <div className="text-sm opacity-90">Documenti Totali</div>
        </div>
        <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-lg text-white">
          <div className="text-2xl font-bold">{documents.filter(d => d.format === '.pdf').length}</div>
          <div className="text-sm opacity-90">PDF</div>
        </div>
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-lg text-white">
          <div className="text-2xl font-bold">{documents.filter(d => d.format === '.docx').length}</div>
          <div className="text-sm opacity-90">DOCX</div>
        </div>
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-6 rounded-lg text-white">
          <div className="text-2xl font-bold">✅</div>
          <div className="text-sm opacity-90">Sistema Operativo</div>
        </div>
      </div>

      {/* Upload Area */}
      <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-8 mb-6 text-center hover:border-blue-400 transition-colors">
        <div className="text-4xl mb-4">📤</div>
        <h3 className="text-lg font-semibold mb-2">Carica Nuovi Documenti</h3>
        <p className="text-gray-600 mb-4">Trascina i file qui o clicca per selezionare</p>
        <p className="text-sm text-gray-500 mb-4">Formati supportati: PDF, DOCX, XLSX, TXT, MD - Max 50MB per file</p>
        
        <input
          type="file"
          multiple
          accept=".pdf,.docx,.xlsx,.txt,.md"
          onChange={handleFileUpload}
          className="hidden"
          id="file-upload"
        />
        
        <label
          htmlFor="file-upload"
          className={`inline-block px-6 py-3 rounded-lg font-medium transition-colors cursor-pointer ${
            uploading 
              ? 'bg-gray-400 text-white cursor-not-allowed' 
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          {uploading ? '⏳ Caricamento...' : '📁 Seleziona File'}
        </label>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold">📋 Documenti Caricati ({stats.total})</h2>
          <button 
            onClick={loadDocuments}
            disabled={loading}
            className="text-blue-600 hover:text-blue-800 font-medium text-sm disabled:opacity-50"
          >
            {loading ? '⏳' : '🔄'} Aggiorna
          </button>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="text-gray-600 mt-2">Caricamento documenti...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-lg font-semibold mb-2">Nessun documento caricato</h3>
            <p className="text-gray-600">Carica il primo documento per iniziare con RAG</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {documents.map((doc, index) => (
              <div key={`${doc.filename}-${index}`} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-2xl">{getFileIcon(doc.format)}</div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{getCleanFilename(doc.filename)}</h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                        <span>{formatFileSize(doc.size)}</span>
                        <span>•</span>
                        <span>{formatDate(doc.modified)}</span>
                        <span>•</span>
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                          {doc.format.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="Visualizza">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors" title="Scarica">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </button>
                    <button 
                      onClick={() => deleteDocument(doc.filename)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors" 
                      title="Elimina"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info RAG */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Sistema RAG Attivo
        </h3>
        <p className="text-blue-800 text-sm">
          I documenti caricati sono automaticamente processati e vettorizzati per la ricerca semantica. 
          IntelliChat può accedere a questi contenuti per fornire risposte basate sulla knowledge base aziendale.
        </p>
      </div>
    </div>
  );
};

export default DocumentsRAG;
