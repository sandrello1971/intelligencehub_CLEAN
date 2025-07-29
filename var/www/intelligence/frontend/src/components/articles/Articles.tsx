import React, { useState, useEffect } from 'react';
import './Articles.css';

interface TipologiaServizio {
  id: number;
  nome: string;
  descrizione: string;
  colore: string;
  icona: string;
  attivo: boolean;
}

interface Partner {
  id: number;
  nome: string;
  ragione_sociale?: string;
  email?: string;
  telefono?: string;
  attivo: boolean;
  servizi_count: number;
}

interface ModelloTicket {
  id: string;
  nome: string;
  descrizione: string;
  priority: string;
  is_active: boolean;
}

interface Article {
  id: number;
  codice: string;
  nome: string;
  descrizione: string;
  tipo_prodotto: 'semplice' | 'composito';
  prezzo_base?: number;
  durata_mesi?: number;
  attivo: boolean;
  art_kit: boolean;
  tipologia_servizio_id?: number;
  partner_id?: number;
  responsabile_user_id?: string;
  created_at: string;
  updated_at: string;
  // Dati relazionali
  tipologia?: TipologiaServizio;
  partner?: Partner;
}

interface ArticleFormData {
  codice: string;
  nome: string;
  descrizione: string;
  tipo_prodotto: 'semplice' | 'composito';
  prezzo_base?: number;
  durata_mesi?: number;
  tipologia_servizio_id?: number;
  partner_id?: number;
  responsabile_user_id?: string;
}

const Articles: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [tipologie, setTipologie] = useState<TipologiaServizio[]>([]);
  const [partner, setPartner] = useState<Partner[]>([]);
  const [partnerFiltrati, setPartnerFiltrati] = useState<Partner[]>([]);
  const [availableUsers, setAvailableUsers] = useState<any[]>([]);
  const [modelliTicket, setModelliTicket] = useState<ModelloTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingArticle, setEditingArticle] = useState<Article | null>(null);
  const [formData, setFormData] = useState<ArticleFormData>({
    codice: '',
    nome: '',
    descrizione: '',
    tipo_prodotto: 'semplice'
  });

  // Fetch functions
  const fetchArticles = async (search = '') => {
    try {
      const searchParam = search ? `?search=${encodeURIComponent(search)}` : '';
      const response = await fetch(`/api/v1/articles/${searchParam}`);
      const data = await response.json();
      
      if (data.success) {
        setArticles(data.articles);
      }
    } catch (error) {
      console.error('Error fetching articles:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTipologie = async () => {
    try {
      const response = await fetch('/api/v1/tipologie-servizi/?attivo=true');
      const data = await response.json();
      
      if (data.success) {
        setTipologie(data.tipologie);
      }
    } catch (error) {
      console.error('Error fetching tipologie:', error);
    }
  };

  const fetchPartner = async () => {
    try {
      const response = await fetch('/api/v1/partner/?attivo=true');
      const data = await response.json();
      
      if (data.success) {
        setPartner(data.partner);
      }
    } catch (error) {
      console.error('Error fetching partner:', error);
    }
  };

  const fetchPartnerByServizio = async (articoloId?: number) => {
    if (!articoloId) {
      setPartnerFiltrati(partner);
      return;
    }

    try {
      const response = await fetch(`/api/v1/partner/by-servizio/${articoloId}`);
      const data = await response.json();
      
      if (data.success) {
        setPartnerFiltrati(data.partner);
      } else {
        setPartnerFiltrati(partner); // Fallback a tutti i partner
      }
    } catch (error) {
      console.error('Error fetching partner by servizio:', error);
      setPartnerFiltrati(partner);
    }
  };
  
  const fetchAvailableUsers = async () => {
    try {
      const response = await fetch('/api/v1/articles/users-disponibili');
      const data = await response.json();
      if (data.success) {
        setAvailableUsers(data.users);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // CRUD operations

  const fetchModelliTicket = async () => {
    try {
      const response = await fetch("/api/v1/templates/ticket-templates", {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setModelliTicket(data);
      }
    } catch (error) {
      console.error("Error fetching modelli ticket:", error);
    }
  };
  const createArticle = async () => {
    try {
      const response = await fetch('/api/v1/articles/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowCreateModal(false);
        setFormData({
          codice: "",
          nome: "",
          descrizione: "",
          tipo_prodotto: "semplice",
          responsabile_user_id: ""
        });
        fetchArticles(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Creazione fallita'}`);
      }
    } catch (error) {
      console.error('Error creating article:', error);
      alert('❌ Errore durante la creazione');
    }
  };

  const updateArticle = async () => {
    if (!editingArticle) return;
    
    try {
      const response = await fetch(`/api/v1/articles/${editingArticle.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingArticle(null);
        fetchArticles(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Aggiornamento fallito'}`);
      }
    } catch (error) {
      console.error('Error updating article:', error);
      alert('❌ Errore durante l\'aggiornamento');
    }
  };

  const deleteArticle = async (article: Article) => {
    if (!window.confirm(`Sei sicuro di voler eliminare "${article.codice} - ${article.nome}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`/api/v1/articles/${article.id}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchArticles(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || 'Eliminazione fallita'}`);
      }
    } catch (error) {
      console.error('Error deleting article:', error);
      alert('❌ Errore durante l\'eliminazione');
    }
  };

  // Modal handlers
  const openEditModal = (article: Article) => {
    setEditingArticle(article);
    setFormData({
      codice: article.codice,
      nome: article.nome,
      descrizione: article.descrizione,
      tipo_prodotto: article.tipo_prodotto,
      prezzo_base: article.prezzo_base,
      durata_mesi: article.durata_mesi,
      responsabile_user_id: article.responsabile_user_id || "",
      tipologia_servizio_id: article.tipologia_servizio_id,
      partner_id: article.partner_id,
      modello_ticket_id: article.modello_ticket_id,
    });
    setShowEditModal(true);
  };

  const openCreateModal = () => {
    setFormData({
      codice: "",
      nome: "",
      descrizione: "",
      tipo_prodotto: "semplice",
      responsabile_user_id: ""
    });
    setPartnerFiltrati(partner);
    setShowCreateModal(true);
  };

  // Effects
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      fetchArticles(searchTerm);
    }, 300);
    
    return () => clearTimeout(delayedSearch);
  }, [searchTerm]);

  useEffect(() => {
    fetchArticles();
    fetchTipologie();
    fetchPartner();
    fetchAvailableUsers();
    fetchModelliTicket();
  }, []);

  // Filter partner when form data changes
  useEffect(() => {
    if (formData.tipo_prodotto === 'semplice' && formData.tipologia_servizio_id) {
      // Per i servizi semplici, mostra solo partner che erogano quel tipo di servizio
      // Per ora mostriamo tutti, ma qui potresti implementare filtri più specifici
      setPartnerFiltrati(partner);
    } else {
      setPartnerFiltrati(partner);
    }
  }, [formData.tipologia_servizio_id, formData.tipo_prodotto, partner]);

  const filteredArticles = articles.filter(article =>
    article.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    article.codice.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getTipologiaById = (id?: number) => {
    return tipologie.find(t => t.id === id);
  };

  const getPartnerById = (id?: number) => {
    return partner.find(p => p.id === id);
  };

  if (loading) {
    return (
      <div className="articles-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          Caricamento articoli...
        </div>
      </div>
    );
  }

  return (
    <div className="articles-container">
      {/* Header */}
      <div className="articles-header">
        <div className="articles-title">
          <h1>📄 Gestione Articoli</h1>
          <p>Gestisci i tuoi prodotti e servizi con tipologie e partner</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={openCreateModal}
        >
          ➕ Nuovo Articolo
        </button>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{articles.length}</div>
          <div className="stat-label">Totali</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{articles.filter(a => a.attivo).length}</div>
          <div className="stat-label">Attivi</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{articles.filter(a => a.tipo_prodotto === 'semplice').length}</div>
          <div className="stat-label">Servizi</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{articles.filter(a => a.tipo_prodotto === 'composito').length}</div>
          <div className="stat-label">Kit Commerciali</div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="search-section">
        <div className="search-input-container">
          <input
            type="text"
            placeholder="🔍 Cerca per codice o nome..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      {/* Articles Table */}
      <div className="articles-table-container">
        <table className="articles-table">
          <thead>
            <tr>
              <th>Codice</th>
              <th>Nome</th>
              <th>Tipo</th>
              <th>Tipologia</th>
              <th>Partner</th>
              <th>Prezzo Base</th>
              <th>Durata</th>
              <th>Stato</th>
              <th>Azioni</th>
            </tr>
          </thead>
          <tbody>
            {filteredArticles.map((article) => {
              const tipologia = getTipologiaById(article.tipologia_servizio_id);
              const partnerInfo = getPartnerById(article.partner_id);
              
              return (
                <tr key={article.id}>
                  <td>
                    <span className="article-code">{article.codice}</span>
                  </td>
                  <td>
                    <div className="article-name">
                      <strong>{article.nome}</strong>
                      {article.descrizione && (
                        <div className="article-description">{article.descrizione}</div>
                      )}
                    </div>
                  </td>
                  <td>
                    <span className={`type-badge ${article.tipo_prodotto}`}>
                      {article.tipo_prodotto === 'semplice' ? '🔹 Servizio' : '🔸 Kit Commerciale'}
                    </span>
                  </td>
                  <td>
                    {tipologia ? (
                      <span 
                        className="tipologia-badge"
                        style={{ backgroundColor: tipologia.colore + '20', color: tipologia.colore }}
                      >
                        {tipologia.icona} {tipologia.nome}
                      </span>
                    ) : (
                      <span className="no-data">Non specificata</span>
                    )}
                  </td>
                  <td>
                    {partnerInfo ? (
                      <div className="partner-info">
                        <strong>{partnerInfo.nome}</strong>
                        {partnerInfo.email && (
                          <div className="partner-email">{partnerInfo.email}</div>
                        )}
                      </div>
                    ) : (
                      <span className="no-data">Nessun partner</span>
                    )}
                  </td>
                  <td>
                    {article.prezzo_base ? `€ ${article.prezzo_base}` : '-'}
                  </td>
                  <td>
                    {article.durata_mesi ? `${article.durata_mesi} mesi` : '-'}
                  </td>
                  <td>
                    <span className={`status-badge ${article.attivo ? 'active' : 'inactive'}`}>
                      {article.attivo ? '✅ Attivo' : '❌ Inattivo'}
                    </span>
                  </td>
                  <td>
                    <div className="actions">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => openEditModal(article)}
                        title="Modifica"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => deleteArticle(article)}
                        title="Elimina"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredArticles.length === 0 && (
          <div className="no-results">
            <div className="no-results-icon">📄</div>
            <h3>Nessun articolo trovato</h3>
            <p>
              {searchTerm 
                ? `Nessun risultato per "${searchTerm}"`
                : 'Non ci sono ancora articoli. Creane uno nuovo!'
              }
            </p>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>➕ Nuovo Articolo</h2>
              <button 
                className="modal-close"
                onClick={() => setShowCreateModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Codice *</label>
                <input
                  type="text"
                  value={formData.codice}
                  onChange={(e) => setFormData({...formData, codice: e.target.value})}
                  placeholder="Es: F40"
                  maxLength={10}
                />
              </div>
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                  placeholder="Es: Formazione 4.0"
                />
              </div>
              <div className="form-group">
                <label>Descrizione</label>
                <textarea
                  value={formData.descrizione}
                  onChange={(e) => setFormData({...formData, descrizione: e.target.value})}
                  placeholder="Descrizione dettagliata del prodotto/servizio"
                  rows={3}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Tipo Prodotto *</label>
                  <select
                    value={formData.tipo_prodotto}
                    onChange={(e) => setFormData({...formData, tipo_prodotto: e.target.value as 'semplice' | 'composito'})}
                  >
                    <option value="semplice">🔹 Servizio</option>
                    <option value="composito">🔸 Kit Commerciale</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Tipologia Servizio</label>
                  <select
                    value={formData.tipologia_servizio_id || ''}
                    onChange={(e) => setFormData({...formData, tipologia_servizio_id: e.target.value ? parseInt(e.target.value) : undefined})}
                  >
                    <option value="">Seleziona tipologia...</option>
                    {tipologie.map(tipologia => (
                      <option key={tipologia.id} value={tipologia.id}>
                        {tipologia.icona} {tipologia.nome}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Partner</label>
                  <select
                    value={formData.partner_id || ''}
                    onChange={(e) => setFormData({...formData, partner_id: e.target.value ? parseInt(e.target.value) : undefined})}
                  >
                    <option value="">Seleziona partner...</option>
                    {partnerFiltrati.map(p => (
                      <option key={p.id} value={p.id}>
                        {p.nome} ({p.servizi_count} servizi)
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Responsabile</label>
                  <select
                    value={formData.responsabile_user_id || ''}
                    onChange={(e) => setFormData({...formData, responsabile_user_id: e.target.value || undefined})}
                  >
                    <option value="">Seleziona responsabile...</option>
                    {availableUsers.map(user => (
                      <option key={user.id} value={user.id}>
                        {user.display_name} ({user.role})
                      </option>
                    ))}
                  </select>
                </div>
              </div>
                <div className="form-group">
                  <label>Template Ticket</label>
                  <select
                    value={formData.modello_ticket_id || ""}
                    onChange={(e) => setFormData({...formData, modello_ticket_id: e.target.value || undefined})}
                  >
                    <option value="">Nessun template...</option>
                    {modelliTicket.map(modello => (
                      <option key={modello.id} value={modello.id}>
                        {modello.nome} - {modello.priority}
                      </option>
                    ))}
                  </select>
                </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Prezzo Base (€)</label>
                  <input
                    type="number"
                    value={formData.prezzo_base || ''}
                    onChange={(e) => setFormData({...formData, prezzo_base: parseFloat(e.target.value) || undefined})}
                    placeholder="0.00"
                    step="0.01"
                  />
                </div>
                <div className="form-group">
                  <label>Durata (mesi)</label>
                  <input
                    type="number"
                    value={formData.durata_mesi || ''}
                    onChange={(e) => setFormData({...formData, durata_mesi: parseInt(e.target.value) || undefined})}
                  />
                </div>
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
                onClick={createArticle}
                disabled={!formData.codice || !formData.nome}
              >
                Crea Articolo
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingArticle && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>✏️ Modifica Articolo</h2>
              <button 
                className="modal-close"
                onClick={() => setShowEditModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Codice *</label>
                <input
                  type="text"
                  value={formData.codice}
                  onChange={(e) => setFormData({...formData, codice: e.target.value})}
                  maxLength={10}
                />
              </div>
              <div className="form-group">
                <label>Nome *</label>
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
              <div className="form-row">
                <div className="form-group">
                  <label>Tipo Prodotto *</label>
                  <select
                    value={formData.tipo_prodotto}
                    onChange={(e) => setFormData({...formData, tipo_prodotto: e.target.value as 'semplice' | 'composito'})}
                  >
                    <option value="semplice">🔹 Servizio</option>
                    <option value="composito">🔸 Kit Commerciale</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Tipologia Servizio</label>
                  <select
                    value={formData.tipologia_servizio_id || ''}
                    onChange={(e) => setFormData({...formData, tipologia_servizio_id: e.target.value ? parseInt(e.target.value) : undefined})}
                  >
                    <option value="">Seleziona tipologia...</option>
                    {tipologie.map(tipologia => (
                      <option key={tipologia.id} value={tipologia.id}>
                        {tipologia.icona} {tipologia.nome}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Partner</label>
                  <select
                    value={formData.partner_id || ''}
                    onChange={(e) => setFormData({...formData, partner_id: e.target.value ? parseInt(e.target.value) : undefined})}
                  >
                    <option value="">Seleziona partner...</option>
                    {partnerFiltrati.map(p => (
                      <option key={p.id} value={p.id}>
                        {p.nome} ({p.servizi_count} servizi)
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Prezzo Base (€)</label>
                  <input
                    type="number"
                    value={formData.prezzo_base || ''}
                    onChange={(e) => setFormData({...formData, prezzo_base: parseFloat(e.target.value) || undefined})}
                    step="0.01"
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Durata (mesi)</label>
                  <input
                    type="number"
                    value={formData.durata_mesi || ''}
                    onChange={(e) => setFormData({...formData, durata_mesi: parseInt(e.target.value) || undefined})}
                  />
                </div>
                <div className="form-group">
                  <label>Responsabile</label>
                  <select
                    value={formData.responsabile_user_id || ''}
                    onChange={(e) => setFormData({...formData, responsabile_user_id: e.target.value || undefined})}
                  >
                    <option value="">Seleziona responsabile...</option>
                    {availableUsers.map(user => (
                      <option key={user.id} value={user.id}>
                        {user.display_name} ({user.role})
                      </option>
                    ))}
                  </select>
                <div className="form-group">
                  <label>Template Ticket</label>
                  <select
                    value={formData.modello_ticket_id || ""}
                    onChange={(e) => setFormData({...formData, modello_ticket_id: e.target.value || undefined})}
                  >
                    <option value="">Nessun template...</option>
                    {modelliTicket.map(modello => (
                      <option key={modello.id} value={modello.id}>
                        {modello.nome} - {modello.priority}
                      </option>
                    ))}
                  </select>
                </div>
                </div>
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
                onClick={updateArticle}
                disabled={!formData.codice || !formData.nome}
              >
                Salva Modifiche
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Articles;
