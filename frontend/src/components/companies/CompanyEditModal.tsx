import React, { useState, useEffect } from 'react';

interface Company {
  id: number;
  name: string;
  settore?: string;
  partita_iva?: string;
  email?: string;
  telefono?: string;
  sito_web?: string;
  citta?: string;
  provincia?: string;
  is_partner: boolean;
  is_supplier: boolean;
  partner_category?: string;
  partner_description?: string;
  partner_expertise?: string[];
  partner_rating: number;
  partner_status: string;
  scraping_status: string;
  ai_analysis_summary?: string;
  numero_dipendenti?: number;
  created_at: string;
}

interface CompanyEditModalProps {
  company: Company | null;
  onClose: () => void;
  onSave: (updatedCompany: Company) => void;
}

const PARTNER_CATEGORIES = [
  'Cloud Computing',
  'AI/Machine Learning', 
  'Cybersecurity',
  'Software Development',
  'Consulting',
  'Marketing',
  'Design',
  'Data Analytics',
  'Infrastructure',
  'Other'
];

const CompanyEditModal: React.FC<CompanyEditModalProps> = ({ company, onClose, onSave }) => {
  const [formData, setFormData] = useState<Partial<Company>>({});
  const [loading, setLoading] = useState(false);
  const [scrapingLoading, setScrapingLoading] = useState(false);
  const [scrapingStatus, setScrapingStatus] = useState<string>('');

  useEffect(() => {
    if (company) {
      setFormData({
        name: company.name,
        settore: company.settore,
        email: company.email,
        telefono: company.telefono,
        sito_web: company.sito_web,
        is_partner: company.is_partner,
        is_supplier: company.is_supplier,
        partner_category: company.partner_category,
        partner_description: company.partner_description,
        partner_expertise: company.partner_expertise || [],
        partner_rating: company.partner_rating,
        partner_status: company.partner_status
      });
    }
  }, [company]);

  if (!company) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`/api/v1/companies/${company.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const updatedCompany = await response.json();
        onSave(updatedCompany);
        onClose();
      } else {
        throw new Error('Errore nel salvataggio');
      }
    } catch (error) {
      console.error('Error updating company:', error);
      alert('Errore nel salvataggio della modifica');
    } finally {
      setLoading(false);
    }
  };

  const handleScrapWebsite = async () => {
    if (!company.sito_web) {
      alert('Nessun sito web configurato per questa azienda');
      return;
    }

    setScrapingLoading(true);
    setScrapingStatus('Avvio scraping...');

    try {
      // Prova diversi endpoint scraping disponibili
      let response;
      const websiteUrl = company.sito_web.startsWith('http') 
        ? company.sito_web 
        : `https://${company.sito_web}`;

      // Endpoint 1: /api/web-scraping/scrape-url
      try {
        response = await fetch('/api/web-scraping/scrape-url', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            url: websiteUrl,
            company_id: company.id,
          })
        });
      } catch (error) {
        console.log('Trying alternative endpoint...');
      }

      // Endpoint 2: /scrape-url (fallback)
      if (!response || !response.ok) {
        response = await fetch('/scrape-url', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            url: websiteUrl,
          })
        });
      }


if (response.ok) {
  const result = await response.json();
  if (result.success) {
    setScrapingStatus('✅ Scraping completato con successo!');
    
    // Aggiorna lo status nel database
    try {
      await fetch(`/api/v1/companies/${company.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scraping_status: "completed" })
      });
    } catch (error) {
      console.log('Error updating company status:', error);
    }
    
  } else if (result.message.includes('duplicate key')) {
    setScrapingStatus('✅ Sito già analizzato!');
    
    // Aggiorna lo status anche per duplicati
    try {
      await fetch(`/api/v1/companies/${company.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scraping_status: "completed" })
      });
    } catch (error) {
      console.log('Error updating company status:', error);
    }
    
  } else {
    setScrapingStatus('⚠️ Problema durante lo scraping');
  }

  // Aggiorna lo status scraping nel form locale
  setFormData(prev => ({
    ...prev,
    scraping_status: 'completed'
  }));



        setTimeout(() => {
          setScrapingStatus('');
        }, 3000);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Scraping error:', error);
      setScrapingStatus('❌ Errore durante lo scraping');
      setTimeout(() => {
        setScrapingStatus('');
      }, 3000);
    } finally {
      setScrapingLoading(false);
    }
  };

  const addExpertise = () => {
    const newExpertise = prompt('Inserisci una nuova competenza:');
    if (newExpertise && newExpertise.trim()) {
      setFormData(prev => ({
        ...prev,
        partner_expertise: [...(prev.partner_expertise || []), newExpertise.trim()]
      }));
    }
  };

  const removeExpertise = (index: number) => {
    setFormData(prev => ({
      ...prev,
      partner_expertise: (prev.partner_expertise || []).filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            ✏️ Modifica Azienda: {company.name?.replace(/'/g, '')}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Informazioni Base */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nome Azienda *
              </label>
              <input
                type="text"
                value={formData.name || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Settore
              </label>
              <input
                type="text"
                value={formData.settore || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, settore: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={formData.email || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Telefono
              </label>
              <input
                type="tel"
                value={formData.telefono || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, telefono: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Sito Web con Scraping */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sito Web
            </label>
            <div className="flex gap-2">
              <input
                type="url"
                value={formData.sito_web || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, sito_web: e.target.value }))}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="https://example.com"
              />
              <button
                type="button"
                onClick={handleScrapWebsite}
                disabled={scrapingLoading || !formData.sito_web}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {scrapingLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Scraping...
                  </>
                ) : (
                  <>🕷️ Scraping</>
                )}
              </button>
            </div>
            {scrapingStatus && (
              <p className={`mt-2 text-sm ${scrapingStatus.includes('✅') ? 'text-green-600' : 'text-red-600'}`}>
                {scrapingStatus}
              </p>
            )}
          </div>

          {/* Partner Management */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🤝 Gestione Partner</h3>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="flex items-center gap-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_partner || false}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_partner: e.target.checked }))}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">È Partner</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_supplier || false}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_supplier: e.target.checked }))}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">È Supplier</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status Partner
                </label>
                <select
                  value={formData.partner_status || 'active'}
                  onChange={(e) => setFormData(prev => ({ ...prev, partner_status: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="active">Attivo</option>
                  <option value="inactive">Inattivo</option>
                  <option value="pending">In Valutazione</option>
                </select>
              </div>
            </div>

            {(formData.is_partner || formData.is_supplier) && (
              <>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Categoria Partner
                    </label>
                    <select
                      value={formData.partner_category || ''}
                      onChange={(e) => setFormData(prev => ({ ...prev, partner_category: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Seleziona categoria...</option>
                      {PARTNER_CATEGORIES.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Rating Partner (1-5)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      step="0.1"
                      value={formData.partner_rating || 0}
                      onChange={(e) => setFormData(prev => ({ ...prev, partner_rating: parseFloat(e.target.value) || 0 }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Descrizione Partner
                  </label>
                  <textarea
                    value={formData.partner_description || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, partner_description: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Descrivi i servizi e competenze del partner..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Competenze & Expertise
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {(formData.partner_expertise || []).map((expertise, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {expertise}
                        <button
                          type="button"
                          onClick={() => removeExpertise(index)}
                          className="ml-2 text-blue-600 hover:text-blue-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <button
                    type="button"
                    onClick={addExpertise}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    + Aggiungi Competenza
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Scraping Status */}
          {company.scraping_status && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">🕷️ Status Scraping</h3>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  company.scraping_status === 'completed' 
                    ? 'bg-green-100 text-green-800' 
                    : company.scraping_status === 'pending'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {company.scraping_status}
                </span>
                {company.ai_analysis_summary && (
                  <span className="text-sm text-gray-600">
                    AI Analysis disponibile
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-6 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annulla
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Salvando...
                </>
              ) : (
                <>💾 Salva Modifiche</>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CompanyEditModal;
