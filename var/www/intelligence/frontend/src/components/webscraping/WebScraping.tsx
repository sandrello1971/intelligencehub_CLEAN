import React, { useState, useEffect } from 'react';
import { Globe, Download, Database, AlertCircle, CheckCircle } from 'lucide-react';

interface ScrapedSite {
  url: string;
  last_scraped: string;
}

interface ScrapingResult {
  success: boolean;
  url: string;
  content?: string;
  title?: string;
  knowledge_document_id?: string;
  chunks_created?: number;
  rag_integrated: boolean;
  message: string;
}

interface ScrapingStats {
  total_documents: number;
  scraped_documents: number;
  total_chunks: number;
  rag_integrated: boolean;
}

const WebScraping: React.FC = () => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScrapingResult | null>(null);
  const [stats, setStats] = useState<ScrapingStats | null>(null);
  const [sites, setSites] = useState<ScrapedSite[]>([]);

  useEffect(() => {
    loadStats();
    loadSites();
  }, []);

  const loadSites = async () => {
    try {
      const response = await fetch('/api/web-scraping/scraped-sites');
      const data = await response.json();
      console.log("DEBUG: Sites loaded from API:", data.scraped_sites);
      setSites(data.scraped_sites || []);
    } catch (error) {
      console.error('Error loading sites:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/web-scraping/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/web-scraping/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      });

      const data = await response.json();
      setResult(data);
      
      if (data.success) {
        loadStats();
        loadSites();
      }
    } catch (error) {
      setResult({
        success: false,
        url: url,
        message: 'Errore di connessione al server',
        rag_integrated: false
      });
    } finally {
      setIsLoading(false);
    }
  };

  const deleteSite = async (siteUrl: string) => {
    if (!confirm('Sei sicuro di voler eliminare questo sito?')) return;
    
    try {
      const response = await fetch('/api/web-scraping/delete-scraped-site-complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: siteUrl })
      });
      
      if (response.ok) {
        alert('Sito eliminato con successo!');
        loadSites();
        loadStats();
      } else {
        alert('Errore durante l\'eliminazione');
      }
    } catch (error) {
      alert('Errore di connessione');
    }
  };

  console.log("DEBUG RENDER: Sites array length:", sites.length);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Globe className="mr-3 h-6 w-6 text-blue-600" />
          🚨 Web Scraping DEBUG
        </h1>
        <p className="text-gray-600 mt-2">
          Estrai contenuti da pagine web e aggiungili automaticamente alla knowledge base
        </p>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Database className="h-5 w-5 text-blue-600 mr-2" />
              <div>
                <p className="text-sm text-blue-600 font-medium">Documenti Totali</p>
                <p className="text-2xl font-bold text-blue-900">{stats.total_documents}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Globe className="h-5 w-5 text-green-600 mr-2" />
              <div>
                <p className="text-sm text-green-600 font-medium">Documenti Scrappati</p>
                <p className="text-2xl font-bold text-green-900">{stats.scraped_documents}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Download className="h-5 w-5 text-purple-600 mr-2" />
              <div>
                <p className="text-sm text-purple-600 font-medium">Chunks Totali</p>
                <p className="text-2xl font-bold text-purple-900">{stats.total_chunks}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-yellow-600 mr-2" />
              <div>
                <p className="text-sm text-yellow-600 font-medium">Status</p>
                <p className="text-lg font-bold text-yellow-900">
                  {stats.rag_integrated ? 'Attivo' : 'Non Attivo'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scraping Form */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Nuovo Scraping</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
              URL da Scrappare
            </label>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={isLoading}
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading || !url.trim()}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Scraping in corso...
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Avvia Scraping
              </>
            )}
          </button>
        </form>

        {/* Result */}
        {result && (
          <div className="mt-6 p-4 rounded-lg border">
            <div className="flex items-center mb-2">
              {result.success ? (
                <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
              )}
              <h3 className={`font-semibold ${result.success ? 'text-green-800' : 'text-red-800'}`}>
                {result.success ? 'Scraping Completato' : 'Errore Scraping'}
              </h3>
            </div>
            
            <p className="text-gray-700 mb-2">{result.message}</p>
            
            {result.success && (
              <div className="text-sm text-gray-600 space-y-1">
                <p><strong>URL:</strong> {result.url}</p>
                {result.title && (
                  <p><strong>Titolo:</strong> {result.title}</p>
                )}
                {result.knowledge_document_id && (
                  <p><strong>ID Documento:</strong> {result.knowledge_document_id}</p>
                )}
                {result.chunks_created && (
                  <p><strong>Chunks creati:</strong> {result.chunks_created}</p>
                )}
                {result.rag_integrated && (
                  <p className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-600 mr-1" />
                    <strong>Integrato nella Knowledge Base</strong>
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Sezione Siti Scrappati */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <Database className="mr-2 h-5 w-5 text-blue-600" />
            Siti Scrappati ({sites.length})
          </h2>
        </div>

        {sites.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Nessun sito scrappato trovato</p>
        ) : (
          <div className="space-y-2">
            {sites.map((site) => (
              <div key={site.url} className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                <div className="flex-1">
                  <p className="font-medium text-gray-900 truncate">{site.url}</p>
                  <p className="text-sm text-gray-500">Scrappato: {new Date(site.last_scraped).toLocaleString()}</p>
                </div>
                <button
                  onClick={() => deleteSite(site.url)}
                  className="ml-3 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                >
                  Elimina
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default WebScraping;
