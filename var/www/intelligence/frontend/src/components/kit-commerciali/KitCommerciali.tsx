import React, { useState, useEffect } from 'react';
import './KitCommerciali.css';

interface Article {
  id: number;
  codice: string;
  nome: string;
  descrizione: string;
  tipo_prodotto: 'semplice' | 'composito';
  attivo: boolean;
}

interface KitArticle {
  id: number;
  articolo_id: number;
  articolo_nome: string;
  articolo_codice: string;
  articolo_descrizione: string;
  quantita: number;
  obbligatorio: boolean;
  ordine: number;
}

interface KitCommerciale {
  id: number;
  nome: string;
  descrizione: string;
  articolo_principale_id?: number;
  articolo_principale?: {
    nome: string;
    codice: string;
  };
  attivo: boolean;
  created_at: string;
  articoli: KitArticle[];
}

interface KitFormData {
  nome: string;
  descrizione: string;
  articolo_principale_id?: number;
  attivo: boolean;
}

interface ServiceFormData {
  articolo_id: number;
  quantita: number;
  obbligatorio: boolean;
  ordine: number;
}

const KitCommerciali: React.FC = () => {
  const [kits, setKits] = useState<KitCommerciale[]>([]);
  const [availableArticles, setAvailableArticles] = useState<Article[]>([]);
  const [compositArticles, setCompositArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showServiceModal, setShowServiceModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  
  // Current kit being worked on
  const [editingKit, setEditingKit] = useState<KitCommerciale | null>(null);
  const [detailKit, setDetailKit] = useState<KitCommerciale | null>(null);
  
  // Form data
  const [formData, setFormData] = useState<KitFormData>({
    nome: '',
    descrizione: '',
    attivo: true
  });
  
  const [serviceFormData, setServiceFormData] = useState<ServiceFormData>({
    articolo_id: 0,
    quantita: 1,
    obbligatorio: false,
    ordine: 0
  });

  // Fetch data functions
  const fetchKits = async (search = '') => {
    try {
      const searchParam = search ? `?search=${encodeURIComponent(search)}` : '';
      const response = await fetch(`/api/v1/kit-commerciali/${searchParam}`);
      const data = await response.json();
      
      if (data.success) {
        setKits(data.kit_commerciali || []);
      }
    } catch (error) {
      console.error('Error fetching kits:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableArticles = async () => {
    try {
      const response = await fetch('/api/v1/kit-commerciali/articoli-disponibili');
      const data = await response.json();
      
      if (data.success) {
        setAvailableArticles(data.articoli || []);
      }
    } catch (error) {
      console.error('Error fetching available articles:', error);
    }
  };

  const fetchCompositArticles = async () => {
    try {
      const response = await fetch('/api/v1/kit-commerciali/articoli-compositi');
      const data = await response.json();
      
      if (data.success) {
        setCompositArticles(data.articoli_compositi || []);
      }
    } catch (error) {
      console.error('Error fetching composit articles:', error);
    }
  };

  // CRUD operations
  const createKit = async () => {
    try {
      const response = await fetch('/api/v1/kit-commerciali/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowCreateModal(false);
        setFormData({ nome: '', descrizione: '', attivo: true });
        fetchKits(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Creazione fallita'}`);
      }
    } catch (error) {
      console.error('Error creating kit:', error);
      alert('❌ Errore durante la creazione');
    }
  };

  const updateKit = async () => {
    if (!editingKit) return;
    
    try {
      const response = await fetch(`/api/v1/kit-commerciali/${editingKit.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingKit(null);
        fetchKits(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Aggiornamento fallito'}`);
      }
    } catch (error) {
      console.error('Error updating kit:', error);
      alert('❌ Errore durante l\'aggiornamento');
    }
  };

  const deleteKit = async (kit: KitCommerciale) => {
    if (!window.confirm(`Sei sicuro di voler eliminare il kit "${kit.nome}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`/api/v1/kit-commerciali/${kit.id}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchKits(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Eliminazione fallita'}`);
      }
    } catch (error) {
      console.error('Error deleting kit:', error);
      alert('❌ Errore durante l\'eliminazione');
    }
  };

  const addServiceToKit = async () => {
    if (!editingKit) return;

    try {
      const response = await fetch(`/api/v1/kit-commerciali/${editingKit.id}/articoli`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(serviceFormData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowServiceModal(false);
        setServiceFormData({ articolo_id: 0, quantita: 1, obbligatorio: false, ordine: 0 });
        fetchKits(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Aggiunta servizio fallita'}`);
      }
    } catch (error) {
      console.error('Error adding service to kit:', error);
      alert('❌ Errore durante l\'aggiunta del servizio');
    }
  };

  const removeServiceFromKit = async (kitId: number, serviceId: number, serviceName: string) => {
    if (!window.confirm(`Rimuovere "${serviceName}" dal kit?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/kit-commerciali/${kitId}/articoli/${serviceId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchKits(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Rimozione fallita'}`);
      }
    } catch (error) {
      console.error('Error removing service from kit:', error);
      alert('❌ Errore durante la rimozione');
    }
  };

  // Modal handlers
  const openEditModal = (kit: KitCommerciale) => {
    setEditingKit(kit);
    setFormData({
      nome: kit.nome,
      descrizione: kit.descrizione,
      articolo_principale_id: kit.articolo_principale_id,
      attivo: kit.attivo
    });
    setShowEditModal(true);
  };

  const openServiceModal = (kit: KitCommerciale) => {
    setEditingKit(kit);
    setServiceFormData({
      articolo_id: 0,
      quantita: 1,
      obbligatorio: false,
      ordine: kit.articoli.length
    });
    setShowServiceModal(true);
  };

  const openDetailModal = (kit: KitCommerciale) => {
    setDetailKit(kit);
    setShowDetailModal(true);
  };

  // Effects
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      fetchKits(searchTerm);
    }, 300);
    
    return () => clearTimeout(delayedSearch);
  }, [searchTerm]);

  useEffect(() => {
    fetchKits();
    fetchAvailableArticles();
    fetchCompositArticles();
  }, []);

  const filteredKits = kits.filter(kit =>
    kit.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (kit.descrizione && kit.descrizione.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <div className="kit-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          Caricamento kit commerciali...
        </div>
      </div>
    );
  }

  return (
    <div className="kit-container">
      {/* Header */}
      <div className="kit-header">
        <div className="kit-title">
          <h1>📦 Kit Commerciali</h1>
          <p>Gestisci i tuoi pacchetti di servizi</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          ➕ Nuovo Kit
        </button>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{kits.length}</div>
          <div className="stat-label">Totali</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{kits.filter(k => k.attivo).length}</div>
          <div className="stat-label">Attivi</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{kits.reduce((acc, k) => acc + k.articoli.length, 0)}</div>
          <div className="stat-label">Servizi Totali</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{kits.filter(k => k.articolo_principale_id).length}</div>
          <div className="stat-label">Con Principale</div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="search-section">
        <div className="search-input-container">
          <input
            type="text"
            placeholder="🔍 Cerca per nome o descrizione..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      {/* Kits Grid */}
      <div className="kit-grid">
        {filteredKits.map((kit) => (
          <div key={kit.id} className="kit-card">
            <div className="kit-card-header">
              <div className="kit-card-title">
                <h3>{kit.nome}</h3>
                <span className={`status-badge ${kit.attivo ? 'active' : 'inactive'}`}>
                  {kit.attivo ? '✅ Attivo' : '❌ Inattivo'}
                </span>
              </div>
              <div className="kit-card-actions">
                <button
                  className="btn btn-info btn-sm"
                  onClick={() => openDetailModal(kit)}
                  title="Dettagli"
                >
                  👁️
                </button>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => openEditModal(kit)}
                  title="Modifica"
                >
                  ✏️
                </button>
                <button
                  className="btn btn-success btn-sm"
                  onClick={() => openServiceModal(kit)}
                  title="Aggiungi Servizio"
                >
                  ➕
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => deleteKit(kit)}
                  title="Elimina"
                >
                  🗑️
                </button>
              </div>
            </div>

            {kit.descrizione && (
              <div className="kit-card-description">
                {kit.descrizione}
              </div>
            )}

            {kit.articolo_principale && (
              <div className="kit-card-main">
                <strong>Articolo Principale:</strong> {kit.articolo_principale.codice} - {kit.articolo_principale.nome}
              </div>
            )}

            <div className="kit-card-services">
              <div className="services-header">
                <strong>Servizi ({kit.articoli.length})</strong>
              </div>
              {kit.articoli.length > 0 ? (
                <div className="services-list">
                  {kit.articoli.slice(0, 3).map((service) => (
                    <div key={service.id} className="service-item">
                      <span className="service-code">{service.articolo_codice}</span>
                      <span className="service-name">{service.articolo_nome}</span>
                      <span className="service-qty">x{service.quantita}</span>
                      {service.obbligatorio && <span className="service-required">*</span>}
                      <button
                        className="btn btn-danger btn-xs"
                        onClick={() => removeServiceFromKit(kit.id, service.id, service.articolo_nome)}
                        title="Rimuovi"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                  {kit.articoli.length > 3 && (
                    <div className="services-more">
                      +{kit.articoli.length - 3} altri servizi...
                    </div>
                  )}
                </div>
              ) : (
                <div className="no-services">
                  Nessun servizio configurato
                </div>
              )}
            </div>

            <div className="kit-card-footer">
              <small>Creato: {new Date(kit.created_at).toLocaleDateString()}</small>
            </div>
          </div>
        ))}
      </div>

      {filteredKits.length === 0 && (
        <div className="no-results">
          <div className="no-results-icon">📦</div>
          <h3>Nessun kit trovato</h3>
          <p>
            {searchTerm 
              ? `Nessun risultato per "${searchTerm}"`
              : 'Non ci sono ancora kit commerciali. Creane uno nuovo!'
            }
          </p>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>➕ Nuovo Kit Commerciale</h2>
              <button 
                className="modal-close"
                onClick={() => setShowCreateModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome Kit *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                  placeholder="Es: Kit Marketing Digital"
                />
              </div>
              <div className="form-group">
                <label>Descrizione</label>
                <textarea
                  value={formData.descrizione}
                  onChange={(e) => setFormData({...formData, descrizione: e.target.value})}
                  placeholder="Descrizione del kit commerciale"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Articolo Principale (Opzionale)</label>
                <select
                  value={formData.articolo_principale_id || ''}
                  onChange={(e) => setFormData({...formData, articolo_principale_id: e.target.value ? parseInt(e.target.value) : undefined})}
                >
                  <option value="">Nessun articolo principale</option>
                  {compositArticles.map(article => (
                    <option key={article.id} value={article.id}>
                      {article.codice} - {article.nome}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.attivo}
                    onChange={(e) => setFormData({...formData, attivo: e.target.checked})}
                  />
                  Kit attivo
                </label>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowCreateModal(false)}
              >
                Annulla
              </button>
              <button 
                className="btn btn-primary"
                onClick={createKit}
                disabled={!formData.nome}
              >
                Crea Kit
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingKit && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>✏️ Modifica Kit</h2>
              <button 
                className="modal-close"
                onClick={() => setShowEditModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome Kit *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Descrizione</label>
                <textarea
                  value={formData.descrizione}
                  onChange={(e) => setFormData({...formData, descrizione: e.target.value})}
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Articolo Principale</label>
                <select
                  value={formData.articolo_principale_id || ''}
                  onChange={(e) => setFormData({...formData, articolo_principale_id: e.target.value ? parseInt(e.target.value) : undefined})}
                >
                  <option value="">Nessun articolo principale</option>
                  {compositArticles.map(article => (
                    <option key={article.id} value={article.id}>
                      {article.codice} - {article.nome}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.attivo}
                    onChange={(e) => setFormData({...formData, attivo: e.target.checked})}
                  />
                  Kit attivo
                </label>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowEditModal(false)}
              >
                Annulla
              </button>
              <button 
                className="btn btn-primary"
                onClick={updateKit}
                disabled={!formData.nome}
              >
                Salva Modifiche
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Service Modal */}
      {showServiceModal && editingKit && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>➕ Aggiungi Servizio a {editingKit.nome}</h2>
              <button 
                className="modal-close"
                onClick={() => setShowServiceModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Servizio *</label>
                <select
                  value={serviceFormData.articolo_id}
                  onChange={(e) => setServiceFormData({...serviceFormData, articolo_id: parseInt(e.target.value)})}
                >
                  <option value={0}>Seleziona un servizio</option>
                  {availableArticles.filter(a => a.tipo_prodotto === 'semplice').map(article => (
                    <option key={article.id} value={article.id}>
                      {article.codice} - {article.nome}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Quantità</label>
                  <input
                    type="number"
                    value={serviceFormData.quantita}
                    onChange={(e) => setServiceFormData({...serviceFormData, quantita: parseInt(e.target.value) || 1})}
                    min="1"
                  />
                </div>
                <div className="form-group">
                  <label>Ordine</label>
                  <input
                    type="number"
                    value={serviceFormData.ordine}
                    onChange={(e) => setServiceFormData({...serviceFormData, ordine: parseInt(e.target.value) || 0})}
                    min="0"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={serviceFormData.obbligatorio}
                    onChange={(e) => setServiceFormData({...serviceFormData, obbligatorio: e.target.checked})}
                  />
                  Servizio obbligatorio
                </label>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowServiceModal(false)}
              >
                Annulla
              </button>
              <button 
                className="btn btn-primary"
                onClick={addServiceToKit}
                disabled={!serviceFormData.articolo_id}
              >
                Aggiungi Servizio
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && detailKit && (
        <div className="modal-overlay">
          <div className="modal modal-large">
            <div className="modal-header">
              <h2>👁️ Dettagli Kit: {detailKit.nome}</h2>
              <button 
                className="modal-close"
                onClick={() => setShowDetailModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="kit-detail">
                <div className="detail-section">
                  <h3>Informazioni Generali</h3>
                  <p><strong>Nome:</strong> {detailKit.nome}</p>
                  <p><strong>Descrizione:</strong> {detailKit.descrizione || 'Nessuna descrizione'}</p>
                  <p><strong>Stato:</strong> {detailKit.attivo ? '✅ Attivo' : '❌ Inattivo'}</p>
                  <p><strong>Creato:</strong> {new Date(detailKit.created_at).toLocaleString()}</p>
                </div>

                {detailKit.articolo_principale && (
                  <div className="detail-section">
                    <h3>Articolo Principale</h3>
                    <p>{detailKit.articolo_principale.codice} - {detailKit.articolo_principale.nome}</p>
                  </div>
                )}

                <div className="detail-section">
                  <h3>Servizi Inclusi ({detailKit.articoli.length})</h3>
                  {detailKit.articoli.length > 0 ? (
                    <div className="services-detail-table">
                      <table>
                        <thead>
                          <tr>
                            <th>Ordine</th>
                            <th>Codice</th>
                            <th>Nome</th>
                            <th>Quantità</th>
                            <th>Obbligatorio</th>
                          </tr>
                        </thead>
                        <tbody>
                          {detailKit.articoli
                            .sort((a, b) => a.ordine - b.ordine)
                            .map((service) => (
                            <tr key={service.id}>
                              <td>{service.ordine}</td>
                              <td><span className="service-code">{service.articolo_codice}</span></td>
                              <td>{service.articolo_nome}</td>
                              <td>{service.quantita}</td>
                              <td>{service.obbligatorio ? '✅ Sì' : '❌ No'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p>Nessun servizio configurato per questo kit.</p>
                  )}
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowDetailModal(false)}
              >
                Chiudi
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => {
                  setShowDetailModal(false);
                  openEditModal(detailKit);
                }}
              >
                Modifica Kit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KitCommerciali;
