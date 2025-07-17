import React, { useState, useEffect } from 'react';
import './TipologieServizi.css';

interface TipologiaServizio {
  id: number;
  nome: string;
  descrizione?: string;
  colore: string;
  icona: string;
  attivo: boolean;
  created_at: string;
  updated_at: string;
}

interface FormData {
  nome: string;
  descrizione: string;
  colore: string;
  icona: string;
  attivo: boolean;
}

const TipologieServizi: React.FC = () => {
  const [tipologie, setTipologie] = useState<TipologiaServizio[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTipologia, setEditingTipologia] = useState<TipologiaServizio | null>(null);
  
  const [formData, setFormData] = useState<FormData>({
    nome: '',
    descrizione: '',
    colore: '#3B82F6',
    icona: '📋',
    attivo: true
  });

  // Icone disponibili
  const iconeDisponibili = ['📋', '💼', '🔧', '💻', '📊', '🎯', '🚀', '⚙️', '📱', '🌐'];
  
  // Colori disponibili
  const coloriDisponibili = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'];

  // Fetch tipologie
  const fetchTipologie = async (search = '') => {
    try {
      const query = search ? `?search=${encodeURIComponent(search)}` : '';
      const response = await fetch(`/api/v1/tipologie-servizi/${query}`);
      const data = await response.json();
      
      if (data.success) {
        setTipologie(data.tipologie);
      }
    } catch (error) {
      console.error('Error fetching tipologie:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTipologie(searchTerm);
  }, [searchTerm]);

  // Create tipologia
  const createTipologia = async () => {
    try {
      const response = await fetch('/api/v1/tipologie-servizi/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowCreateModal(false);
        setFormData({
          nome: '',
          descrizione: '',
          colore: '#3B82F6',
          icona: '📋',
          attivo: true
        });
        fetchTipologie(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.error || 'Creazione fallita'}`);
      }
    } catch (error) {
      console.error('Error creating tipologia:', error);
      alert('❌ Errore durante la creazione');
    }
  };

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };

  // Delete tipologia
  const deleteTipologia = async (tipologia: TipologiaServizio) => {
    if (!confirm(`Sei sicuro di voler eliminare "${tipologia.nome}"?`)) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${tipologia.id}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchTipologie(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.error || 'Eliminazione fallita'}`);
      }
    } catch (error) {
      console.error('Error deleting tipologia:', error);
      alert('❌ Errore durante l\'eliminazione');
    }
  };

  // Filter tipologie
  const filteredTipologie = tipologie.filter(tipologia =>
    tipologia.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (tipologia.descrizione && tipologia.descrizione.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return <div className="loading">Caricamento tipologie...</div>;
  }

  return (
    <div className="tipologie-servizi">
      <div className="page-header">
        <div className="header-content">
          <h1>🏷️ Tipologie di Servizi</h1>
          <p>Gestisci le categorie per organizzare i tuoi servizi</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          ➕ Nuova Tipologia
        </button>
      </div>

      <div className="search-section">
        <div className="search-input-container">
          <input
            type="text"
            placeholder="🔍 Cerca tipologie..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="tipologie-grid">
        {filteredTipologie.map(tipologia => (
          <div key={tipologia.id} className="tipologia-card">
            <div className="tipologia-header">
              <div className="tipologia-icon" style={{ backgroundColor: tipologia.colore + '20', color: tipologia.colore }}>
                {tipologia.icona}
              </div>
              <div className="tipologia-info">
                <h3>{tipologia.nome}</h3>
                <div className="tipologia-meta">
                  <span className={`status-badge ${tipologia.attivo ? 'active' : 'inactive'}`}>
                    {tipologia.attivo ? '✅ Attiva' : '❌ Inattiva'}
                  </span>
                </div>
              </div>
              <div className="tipologia-actions">
                <button
                  className="btn btn-edit btn-sm"
                  onClick={() => openEditModal(tipologia)}
                  title="Modifica"
                >
                  ✏️
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => deleteTipologia(tipologia)}
                  title="Elimina"
                >
                  🗑️
                </button>
              </div>
            </div>
            {tipologia.descrizione && (
              <div className="tipologia-description">
                {tipologia.descrizione}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>➕ Nuova Tipologia</h2>
              <button onClick={() => setShowCreateModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                  placeholder="Es: Servizi Digitali"
                />
              </div>
              <div className="form-group">
                <label>Descrizione</label>
                <textarea
                  value={formData.descrizione}
                  onChange={(e) => setFormData({...formData, descrizione: e.target.value})}
                  placeholder="Descrizione tipologia"
                  rows={3}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Icona</label>
                  <select
                    value={formData.icona}
                    onChange={(e) => setFormData({...formData, icona: e.target.value})}
                  >
                    {iconeDisponibili.map(icona => (
                      <option key={icona} value={icona}>{icona} {icona}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Colore</label>
                  <select
                    value={formData.colore}
                    onChange={(e) => setFormData({...formData, colore: e.target.value})}
                  >
                    {coloriDisponibili.map(colore => (
                      <option key={colore} value={colore}>{colore}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                Annulla
              </button>
              <button 
                className="btn btn-primary"
                onClick={createTipologia}
                disabled={!formData.nome}
              >
                Crea
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingTipologia && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>✏️ Modifica Tipologia</h2>
              <button onClick={() => setShowEditModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                  placeholder="Es: Servizi Digitali"
                />
              </div>
              <div className="form-group">
                <label>Descrizione</label>
                <textarea
                  value={formData.descrizione}
                  onChange={(e) => setFormData({...formData, descrizione: e.target.value})}
                  placeholder="Descrizione tipologia"
                  rows={3}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Icona</label>
                  <select
                    value={formData.icona}
                    onChange={(e) => setFormData({...formData, icona: e.target.value})}
                  >
                    {iconeDisponibili.map(icona => (
                      <option key={icona} value={icona}>{icona} {icona}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Colore</label>
                  <select
                    value={formData.colore}
                    onChange={(e) => setFormData({...formData, colore: e.target.value})}
                  >
                    {coloriDisponibili.map(colore => (
                      <option key={colore} value={colore}>{colore}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.attivo}
                    onChange={(e) => setFormData({...formData, attivo: e.target.checked})}
                  />
                  Tipologia attiva
                </label>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowEditModal(false)}>
                Annulla
              </button>
              <button 
                className="btn btn-primary"
                onClick={updateTipologia}
                disabled={!formData.nome}
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

export default TipologieServizi;
