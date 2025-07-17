import './Partner.css';
import React, { useState, useEffect } from 'react';

interface Partner {
  id: number;
  nome: string;
  ragione_sociale?: string;
  partita_iva?: string;
  email?: string;
  telefono?: string;
  sito_web?: string;
  indirizzo?: string;
  note?: string;
  attivo: boolean;
  servizi_count: number;
  created_at?: string;
}

interface PartnerFormData {
  nome: string;
  ragione_sociale: string;
  partita_iva: string;
  email: string;
  telefono: string;
  sito_web: string;
  indirizzo: string;
  note: string;
  attivo: boolean;
}

interface PartnerServizio {
  id: number;
  articolo_id: number;
  articolo_codice: string;
  articolo_nome: string;
  articolo_descrizione: string;
  tipo_prodotto: string;
  tipologia_nome?: string;
  tipologia_colore?: string;
  tipologia_icona?: string;
  prezzo_partner?: number;
  note?: string;
  created_at?: string;
}

interface Articolo {
  id: number;
  codice: string;
  nome: string;
  descrizione?: string;
  tipo_prodotto: string;
  tipologia_servizio_id?: number;
}

interface ServizioFormData {
  articolo_id: number;
  prezzo_partner?: number;
  note: string;
}

const Partner: React.FC = () => {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [articoli, setArticoli] = useState<Articolo[]>([]);
  const [partnerServizi, setPartnerServizi] = useState<PartnerServizio[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showServicesModal, setShowServicesModal] = useState(false);
  const [showAddServiceModal, setShowAddServiceModal] = useState(false);
  const [editingPartner, setEditingPartner] = useState<Partner | null>(null);
  const [selectedPartner, setSelectedPartner] = useState<Partner | null>(null);
  const [formData, setFormData] = useState<PartnerFormData>({
    nome: '',
    ragione_sociale: '',
    partita_iva: '',
    email: '',
    telefono: '',
    sito_web: '',
    indirizzo: '',
    note: '',
    attivo: true
  });
  const [servizioFormData, setServizioFormData] = useState<ServizioFormData>({
    articolo_id: 0,
    prezzo_partner: undefined,
    note: ''
  });

  // API Calls
  const fetchPartners = async (search: string = '') => {
    try {
      const searchParam = search ? `?search=${encodeURIComponent(search)}` : '';
      const response = await fetch(`/api/v1/partner/${searchParam}`);
      const data = await response.json();
      
      if (data.success) {
        setPartners(data.partner);
      }
    } catch (error) {
      console.error('Error fetching partners:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchArticoli = async () => {
    try {
      const response = await fetch('/api/v1/articles/?tipo_prodotto=semplice');
      const data = await response.json();
      
      if (data.success) {
        setArticoli(data.articles);
      }
    } catch (error) {
      console.error('Error fetching articoli:', error);
    }
  };

  const fetchPartnerServizi = async (partnerId: number) => {
    try {
      const response = await fetch(`/api/v1/partner/${partnerId}/servizi`);
      const data = await response.json();
      
      if (data.success) {
        setPartnerServizi(data.servizi);
      }
    } catch (error) {
      console.error('Error fetching partner servizi:', error);
    }
  };

  const createPartner = async () => {
    try {
      const response = await fetch('/api/v1/partner/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowCreateModal(false);
        resetForm();
        fetchPartners(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Creazione fallita'}`);
      }
    } catch (error) {
      console.error('Error creating partner:', error);
      alert('❌ Errore durante la creazione');
    }
  };

  const updatePartner = async () => {
    if (!editingPartner) return;
    
    try {
      const response = await fetch(`/api/v1/partner/${editingPartner.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingPartner(null);
        fetchPartners(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Aggiornamento fallito'}`);
      }
    } catch (error) {
      console.error('Error updating partner:', error);
      alert('❌ Errore durante l\'aggiornamento');
    }
  };

  const deletePartner = async (partner: Partner) => {
    if (!window.confirm(`Sei sicuro di voler eliminare "${partner.nome}"?`)) return;
    
    try {
      const response = await fetch(`/api/v1/partner/${partner.id}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchPartners(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Eliminazione fallita'}`);
      }
    } catch (error) {
      console.error('Error deleting partner:', error);
      alert('❌ Errore durante l\'eliminazione');
    }
  };

  const addServizioToPartner = async () => {
    if (!selectedPartner || !servizioFormData.articolo_id) return;

    try {
      const response = await fetch(`/api/v1/partner/${selectedPartner.id}/servizi`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(servizioFormData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowAddServiceModal(false);
        resetServizioForm();
        fetchPartnerServizi(selectedPartner.id);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Aggiunta servizio fallita'}`);
      }
    } catch (error) {
      console.error('Error adding servizio:', error);
      alert('❌ Errore durante l\'aggiunta del servizio');
    }
  };

  const removeServizioFromPartner = async (servizioId: number) => {
    if (!selectedPartner) return;
    
    try {
      const response = await fetch(`/api/v1/partner/${selectedPartner.id}/servizi/${servizioId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchPartnerServizi(selectedPartner.id);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Rimozione fallita'}`);
      }
    } catch (error) {
      console.error('Error removing servizio:', error);
      alert('❌ Errore durante la rimozione');
    }
  };

  const openEditModal = (partner: Partner) => {
    setEditingPartner(partner);
    setFormData({
      nome: partner.nome,
      ragione_sociale: partner.ragione_sociale || '',
      partita_iva: partner.partita_iva || '',
      email: partner.email || '',
      telefono: partner.telefono || '',
      sito_web: partner.sito_web || '',
      indirizzo: partner.indirizzo || '',
      note: partner.note || '',
      attivo: partner.attivo
    });
    setShowEditModal(true);
  };

  const openServicesModal = (partner: Partner) => {
    setSelectedPartner(partner);
    setShowServicesModal(true);
    fetchPartnerServizi(partner.id);
  };

  const openAddServiceModal = () => {
    resetServizioForm();
    setShowAddServiceModal(true);
  };

  const resetForm = () => {
    setFormData({
      nome: '',
      ragione_sociale: '',
      partita_iva: '',
      email: '',
      telefono: '',
      sito_web: '',
      indirizzo: '',
      note: '',
      attivo: true
    });
  };

  const resetServizioForm = () => {
    setServizioFormData({
      articolo_id: 0,
      prezzo_partner: undefined,
      note: ''
    });
  };

  const openCreateModal = () => {
    resetForm();
    setShowCreateModal(true);
  };

  // Effects
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      fetchPartners(searchTerm);
    }, 300);
    
    return () => clearTimeout(delayedSearch);
  }, [searchTerm]);

  useEffect(() => {
    fetchPartners();
    fetchArticoli();
  }, []);

  // Get available articles for partner (excluding already added)
  const getAvailableArticoli = () => {
    const assignedIds = partnerServizi.map(ps => ps.articolo_id);
    return articoli.filter(a => !assignedIds.includes(a.id));
  };

  if (loading) {
    return (
      <div className="partner-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          Caricamento partner...
        </div>
      </div>
    );
  }

  return (
    <div className="partner-container">
      {/* Header */}
      <div className="partner-header">
        <div className="partner-title">
          <h1>🤝 Gestione Partner</h1>
          <p>Gestisci i tuoi partner commerciali e fornitori</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={openCreateModal}
        >
          ➕ Nuovo Partner
        </button>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number primary">{partners.length}</div>
          <div className="stat-label">Totali</div>
        </div>
        <div className="stat-card">
          <div className="stat-number success">{partners.filter(p => p.attivo).length}</div>
          <div className="stat-label">Attivi</div>
        </div>
        <div className="stat-card">
          <div className="stat-number danger">{partners.filter(p => !p.attivo).length}</div>
          <div className="stat-label">Inattivi</div>
        </div>
      </div>

      {/* Search */}
      <div className="search-section">
        <input
          type="text"
          className="search-input"
          placeholder="🔍 Cerca partner..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Partners Table */}
      <div className="table-container">
        <div className="table-header">
          <h3>Lista Partner ({partners.filter(partner =>
            partner.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (partner.ragione_sociale && partner.ragione_sociale.toLowerCase().includes(searchTerm.toLowerCase()))
          ).length})</h3>
        </div>
        
        {partners.filter(partner =>
          partner.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (partner.ragione_sociale && partner.ragione_sociale.toLowerCase().includes(searchTerm.toLowerCase()))
        ).length === 0 ? (
          <div className="empty-state">
            <p>
              {searchTerm 
                ? `Nessun risultato per "${searchTerm}"`
                : 'Non ci sono ancora partner. Creane uno nuovo!'
              }
            </p>
          </div>
        ) : (
          <div className="table-content">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Ragione Sociale</th>
                  <th>Email</th>
                  <th>Telefono</th>
                  <th>Servizi</th>
                  <th>Stato</th>
                  <th>Azioni</th>
                </tr>
              </thead>
              <tbody>
                {partners.filter(partner =>
                  partner.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  (partner.ragione_sociale && partner.ragione_sociale.toLowerCase().includes(searchTerm.toLowerCase()))
                ).map((partner) => (
                  <tr key={partner.id}>
                    <td>
                      <div className="partner-name">
                        <strong>{partner.nome}</strong>
                        {partner.partita_iva && (
                          <div className="partner-piva">P.IVA: {partner.partita_iva}</div>
                        )}
                      </div>
                    </td>
                    <td>{partner.ragione_sociale || '-'}</td>
                    <td>{partner.email || '-'}</td>
                    <td>{partner.telefono || '-'}</td>
                    <td>
                      <span className="service-count">{partner.servizi_count || 0} servizi</span>
                    </td>
                    <td>
                      <span className={`status-badge ${partner.attivo ? 'active' : 'inactive'}`}>
                        {partner.attivo ? '✅ Attivo' : '❌ Inattivo'}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button
                          className="btn btn-service"
                          onClick={() => openServicesModal(partner)}
                          title="Gestisci Servizi"
                        >
                          🔧
                        </button>
                        <button
                          className="btn btn-edit"
                          onClick={() => openEditModal(partner)}
                          title="Modifica"
                        >
                          ✏️
                        </button>
                        <button
                          className="btn btn-delete"
                          onClick={() => deletePartner(partner)}
                          title="Elimina"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>➕ Nuovo Partner</h2>
              <button 
                className="modal-close"
                onClick={() => setShowCreateModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                  placeholder="Nome del partner"
                />
              </div>
              <div className="form-group">
                <label>Ragione Sociale</label>
                <input
                  type="text"
                  value={formData.ragione_sociale}
                  onChange={(e) => setFormData({...formData, ragione_sociale: e.target.value})}
                  placeholder="Ragione sociale completa"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>P.IVA</label>
                  <input
                    type="text"
                    value={formData.partita_iva}
                    onChange={(e) => setFormData({...formData, partita_iva: e.target.value})}
                    placeholder="Partita IVA"
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="email@partner.com"
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Telefono</label>
                  <input
                    type="tel"
                    value={formData.telefono}
                    onChange={(e) => setFormData({...formData, telefono: e.target.value})}
                    placeholder="+39 123 456 7890"
                  />
                </div>
                <div className="form-group">
                  <label>Sito Web</label>
                  <input
                    type="url"
                    value={formData.sito_web}
                    onChange={(e) => setFormData({...formData, sito_web: e.target.value})}
                    placeholder="https://www.partner.com"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Indirizzo</label>
                <input
                  type="text"
                  value={formData.indirizzo}
                  onChange={(e) => setFormData({...formData, indirizzo: e.target.value})}
                  placeholder="Via, Città, CAP"
                />
              </div>
              <div className="form-group">
                <label>Note</label>
                <textarea
                  value={formData.note}
                  onChange={(e) => setFormData({...formData, note: e.target.value})}
                  placeholder="Note aggiuntive sul partner"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.attivo}
                    onChange={(e) => setFormData({...formData, attivo: e.target.checked})}
                  />
                  Partner attivo
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
                onClick={createPartner}
                disabled={!formData.nome}
              >
                Crea Partner
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingPartner && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>✏️ Modifica Partner</h2>
              <button 
                className="modal-close"
                onClick={() => setShowEditModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Ragione Sociale</label>
                <input
                  type="text"
                  value={formData.ragione_sociale}
                  onChange={(e) => setFormData({...formData, ragione_sociale: e.target.value})}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>P.IVA</label>
                  <input
                    type="text"
                    value={formData.partita_iva}
                    onChange={(e) => setFormData({...formData, partita_iva: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Telefono</label>
                  <input
                    type="tel"
                    value={formData.telefono}
                    onChange={(e) => setFormData({...formData, telefono: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Sito Web</label>
                  <input
                    type="url"
                    value={formData.sito_web}
                    onChange={(e) => setFormData({...formData, sito_web: e.target.value})}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Indirizzo</label>
                <input
                  type="text"
                  value={formData.indirizzo}
                  onChange={(e) => setFormData({...formData, indirizzo: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Note</label>
                <textarea
                  value={formData.note}
                  onChange={(e) => setFormData({...formData, note: e.target.value})}
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.attivo}
                    onChange={(e) => setFormData({...formData, attivo: e.target.checked})}
                  />
                  Partner attivo
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
                onClick={updatePartner}
                disabled={!formData.nome}
              >
                Salva Modifiche
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Services Management Modal */}
      {showServicesModal && selectedPartner && (
        <div className="modal-overlay">
          <div className="modal modal-large">
            <div className="modal-header">
              <h2>🔧 Servizi di {selectedPartner.nome}</h2>
              <button 
                className="modal-close"
                onClick={() => setShowServicesModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3>Servizi Erogabili ({partnerServizi.length})</h3>
                <button 
                  className="btn btn-primary"
                  onClick={openAddServiceModal}
                  disabled={getAvailableArticoli().length === 0}
                >
                  ➕ Aggiungi Servizio
                </button>
              </div>
              
              {partnerServizi.length === 0 ? (
                <div className="empty-state">
                  <p>Nessun servizio assegnato a questo partner</p>
                </div>
              ) : (
                <div className="services-list">
                  {partnerServizi.map((servizio) => (
                    <div key={servizio.id} className="service-item">
                      <div className="service-info">
                        <div className="service-header">
                          <strong>{servizio.articolo_codice} - {servizio.articolo_nome}</strong>
                          {servizio.tipologia_nome && (
                            <span className="service-type" style={{ 
                              background: servizio.tipologia_colore || '#f3f4f6',
                              color: 'white',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              fontSize: '12px',
                              marginLeft: '8px'
                            }}>
                              {servizio.tipologia_icona} {servizio.tipologia_nome}
                            </span>
                          )}
                        </div>
                        {servizio.articolo_descrizione && (
                          <div className="service-description">{servizio.articolo_descrizione}</div>
                        )}
                        {servizio.prezzo_partner && (
                          <div className="service-price">Prezzo Partner: €{servizio.prezzo_partner}</div>
                        )}
                        {servizio.note && (
                          <div className="service-notes">Note: {servizio.note}</div>
                        )}
                      </div>
                      <button
                        className="btn btn-delete"
                        onClick={() => removeServizioFromPartner(servizio.id)}
                        title="Rimuovi servizio"
                      >
                        🗑️
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowServicesModal(false)}
              >
                Chiudi
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Service Modal */}
      {showAddServiceModal && selectedPartner && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>➕ Aggiungi Servizio a {selectedPartner.nome}</h2>
              <button 
                className="modal-close"
                onClick={() => setShowAddServiceModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Servizio *</label>
                <select
                  value={servizioFormData.articolo_id}
                  onChange={(e) => setServizioFormData({...servizioFormData, articolo_id: parseInt(e.target.value)})}
                >
                  <option value={0}>Seleziona un servizio</option>
                  {getAvailableArticoli().map(articolo => (
                    <option key={articolo.id} value={articolo.id}>
                      {articolo.codice} - {articolo.nome}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Prezzo Partner (€)</label>
                <input
                  type="number"
                  step="0.01"
                  value={servizioFormData.prezzo_partner || ''}
                  onChange={(e) => setServizioFormData({...servizioFormData, prezzo_partner: e.target.value ? parseFloat(e.target.value) : undefined})}
                  placeholder="Prezzo specifico per questo partner"
                />
              </div>
              <div className="form-group">
                <label>Note</label>
                <textarea
                  value={servizioFormData.note}
                  onChange={(e) => setServizioFormData({...servizioFormData, note: e.target.value})}
                  placeholder="Note specifiche per questo servizio"
                  rows={3}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowAddServiceModal(false)}
              >
                Annulla
              </button>
              <button 
                className="btn btn-primary"
                onClick={addServizioToPartner}
                disabled={!servizioFormData.articolo_id}
              >
                Aggiungi Servizio
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Partner;
